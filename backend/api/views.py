# backend/api/views.py

import csv
import stripe
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from datetime import datetime, time as dtime, timedelta
from .utils import send_booking_confirmation
from reportlab.pdfgen import canvas
from .models import Booking
from .serializers import BookingSerializer
stripe.api_key = "YOUR_SECRET_KEY"


# ======================================================
# 🔵 VIEWSET — Main CRUD (Used by Router)
# ======================================================
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-from_date')
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create to handle email in background
        """
        # Validate and save booking
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        booking = serializer.instance
        
        print(f"✔️ BOOKING CREATED — ID: {booking.id}")
        
        import threading
        def send_email_async():
            try:
                print("📧 TRIGGERING EMAIL IN BACKGROUND")
                send_booking_confirmation(booking)
                print("✅ EMAIL SENT SUCCESSFULLY")
            except Exception as e:
                print(f"❌ EMAIL FAILED (but booking saved): {str(e)}")
        
        email_thread = threading.Thread(target=send_email_async)
        email_thread.daemon = True
        email_thread.start()
        
        # Return success immediately
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def perform_create(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [AllowAny()]
        return [IsAuthenticated()]

# ======================================================
# 🟢 GET ALL BOOKINGS / CREATE BOOKING (Public)
# ======================================================
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def bookings_list(request):
    if request.method == 'GET':
        bookings = Booking.objects.order_by('-from_date')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # status will ALWAYS begin as pending
        data = request.data.copy()
        data["status"] = "pending"

        serializer = BookingSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            booking = serializer.save()

            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("❌ Booking creation error:", str(e))
            print("⚙️ Received data:", request.data)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ======================================================
# 🟢 GET SINGLE BOOKING
# ======================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def booking_detail(request, pk):
    try:
        booking = Booking.objects.get(id=pk)
        return Response(BookingSerializer(booking).data)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)


# ======================================================
# 🟢 AVAILABILITY CALENDAR
# ======================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def booking_dates(request):
    bookings = Booking.objects.all()
    events = []

    for booking in bookings:
        try:
            start_date = booking.from_date
            end_date = booking.to_date

            if hasattr(booking, "start_time") and booking.start_time:
                start_dt = datetime.combine(start_date, booking.start_time)
            else:
                start_dt = datetime.combine(start_date, dtime.min)

            if hasattr(booking, "end_time") and booking.end_time:
                end_dt = datetime.combine(end_date, booking.end_time)
            else:
                end_dt = datetime.combine(end_date, dtime.max.replace(microsecond=0))
            
            if end_dt <= start_dt:
                end_dt = start_dt + timedelta(hours=1)

            events.append({
                "title": booking.event_type or "Booking",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            })
        except Exception as e:
            print(f"⚠️ Skipping booking id={getattr(booking, 'id', 'unknown')} due to error:", e)
            continue

    return Response(events)


# ======================================================
# 🟢 DASHBOARD STATISTICS
# ======================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request):

    monthly = (
        Booking.objects.annotate(month=ExtractMonth('from_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    event_types = (
        Booking.objects.values('event_type')
        .annotate(count=Count('id'))
    )

    unread_inquiries = Booking.objects.filter(status='pending').count()
    today = timezone.now().date()
    upcoming_events = Booking.objects.filter(from_date__gte=today).count()
    
    stats = {
        "bookings_per_month": list(monthly),
        "event_type_distribution": list(event_types),
        "total_bookings": Booking.objects.count(),
        "unread_inquiries": unread_inquiries,
        "upcoming_events": upcoming_events, 
        
    }
    return Response(stats)


# ======================================================
# 🟢 EXPORT CSV
# ======================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def export_bookings_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Phone', 'Email', 'Event Type', 'From Date', 'To Date', 'Start Time', 'End Time', 'Message'])
    for b in Booking.objects.all().order_by('-from_date'):
        writer.writerow([b.id, b.name, b.phone, b.email, b.event_type, b.from_date, b.to_date, b.start_time, b.end_time, b.message])
    return response

# ======================================================
# 🟣 UPDATE BOOKING STATUS (Admin Only)
# ======================================================
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_booking_status(request, pk):
    try:
        booking = Booking.objects.get(id=pk)
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"error": "Status field is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if new_status not in ['approved', 'rejected', 'pending']:
            return Response(
                {"error": "Invalid status. Must be 'approved', 'rejected', or 'pending'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = new_status
        booking.save()
        return Response(
            {
                "message": f"Status updated to {new_status}.",
                "booking": BookingSerializer(booking).data
            },
            status=status.HTTP_200_OK
        )
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# ======================================================
# 🟢 PAYMENT SUCCESS — UPDATE BOOKING
#     PATCH /api/bookings/<id>/payment/
# ======================================================
@api_view(['PATCH'])
@permission_classes([AllowAny])   # payment can be updated by user or webhook
def update_payment(request, pk):
    """
    Called by frontend AFTER verifying payment success.
    Example body:
    {
        "amount_paid": 3000
    }
    """
    try:
        booking = Booking.objects.get(id=pk)
        amount = request.data.get("amount_paid")
        if amount is None:
            return Response({"error": "amount_paid is required"}, status=400)
        booking.paid_amount += float(amount)
        booking.balance = float(booking.total_amount) - float(booking.paid_amount)
        if booking.paid_amount >= booking.advance_amount:
            booking.paid = True
        booking.save()
        return Response({"message": "Payment updated", "booking": BookingSerializer(booking).data})
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

# ======================================================
# 🟣 CREATE PAYMENT INTENT (Stripe)
# ======================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_intent(request):
    """
    FRONTEND calls:
    {
        "amount": 5000
    }
    """
    try:
        amount = int(float(request.data["amount"]) * 100)  # ₹ to paise
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="inr",
            automatic_payment_methods={"enabled": True}
        )
        return Response({"clientSecret": intent["client_secret"]})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from datetime import datetime

def draw_elegant_border(c, doc):
    """Draw an elegant border with gradient effect"""
    # Outer border - Purple gradient color
    c.setStrokeColor(colors.HexColor("#6a11cb"))
    c.setLineWidth(4)
    c.rect(30, 30, A4[0] - 60, A4[1] - 60, stroke=1, fill=0)
    
    # Inner border - Lighter purple
    c.setStrokeColor(colors.HexColor("#9d50bb"))
    c.setLineWidth(1)
    c.rect(35, 35, A4[0] - 70, A4[1] - 70, stroke=1, fill=0)

def booking_receipt(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return HttpResponse("Booking not found", status=404)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="SriVari_Receipt_{booking.id}.pdf"'

    # Create PDF with margins
    doc = SimpleDocTemplate(
        response, 
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    story = []

    # ==========================================
    # CUSTOM STYLES
    # ==========================================
    
    # Main Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor("#2a0845"),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    )
    
    # Subtitle Style
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor("#6a11cb"),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Section Header Style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        spaceAfter=10,
        spaceBefore=5,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor("#6a11cb"),
        borderPadding=(8, 8, 8, 8)
    )
    
    # Normal text style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#333333"),
        alignment=TA_LEFT,
        leading=16
    )
    
    # Footer style
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
        leading=12
    )

    # ==========================================
    # HEADER SECTION
    # ==========================================
    
    # Main Title
    story.append(Paragraph("SRI VARI MAHAL A/C", title_style))
    story.append(Paragraph("Grand Marriage & Party Hall", subtitle_style))
    
    # Receipt Info Bar
    receipt_info = [
        [
            Paragraph(f"<b>Receipt No:</b> SVM-{str(booking.id).zfill(4)}", normal_style),
            Paragraph(f"<b>Date:</b> {booking.created_at.strftime('%d %B %Y')}", normal_style)
        ]
    ]
    
    receipt_table = Table(receipt_info, colWidths=[270, 270])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0e6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#9d50bb")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(receipt_table)
    story.append(Spacer(1, 20))

    # ==========================================
    # CUSTOMER DETAILS SECTION
    # ==========================================
    
    story.append(Paragraph("CUSTOMER DETAILS", section_style))
    story.append(Spacer(1, 8))
    
    customer_data = [
        ["Full Name", booking.name],
        ["Contact Number", booking.phone],
        ["Email Address", booking.email or "Not Provided"],
        ["Address", booking.address_line or "Not Provided"],
    ]
    
    customer_table = Table(customer_data, colWidths=[150, 390])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#2a0845")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#333333")),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 20))

    # ==========================================
    # EVENT DETAILS SECTION
    # ==========================================
    
    story.append(Paragraph("EVENT DETAILS", section_style))
    story.append(Spacer(1, 8))
    
    event_data = [
        ["Event Type", booking.event_type],
        ["Event Date", f"{booking.from_date.strftime('%d %B %Y')} to {booking.to_date.strftime('%d %B %Y')}"],
        ["Event Time", f"{booking.start_time.strftime('%I:%M %p')} to {booking.end_time.strftime('%I:%M %p')}"],
        ["Expected Guests", f"{booking.estimated_guests} Guests"],
        ["Food Preference", booking.food_preference or "Not Specified"],
    ]
    
    event_table = Table(event_data, colWidths=[150, 390])
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#2a0845")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#333333")),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(event_table)
    story.append(Spacer(1, 20))

    # ==========================================
    # BOOKING STATUS SECTION
    # ==========================================
    
    story.append(Paragraph("BOOKING STATUS", section_style))
    story.append(Spacer(1, 8))
    
    # Status color coding
    status_colors = {
        'pending': colors.HexColor("#fff3cd"),
        'approved': colors.HexColor("#d4edda"),
        'rejected': colors.HexColor("#f8d7da")
    }
    
    status_text_colors = {
        'pending': colors.HexColor("#856404"),
        'approved': colors.HexColor("#155724"),
        'rejected': colors.HexColor("#721c24")
    }
    
    status_bg = status_colors.get(booking.status.lower(), colors.HexColor("#e9ecef"))
    status_text = status_text_colors.get(booking.status.lower(), colors.black)
    
    status_data = [
        ["Current Status", booking.status.upper()],
    ]
    
    status_table = Table(status_data, colWidths=[150, 390])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
        ('BACKGROUND', (1, 0), (1, -1), status_bg),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#2a0845")),
        ('TEXTCOLOR', (1, 0), (1, -1), status_text),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 25))

    # ==========================================
    # FOOTER SECTION
    # ==========================================
    
    # Divider line
    divider = Table([['']], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 2, colors.HexColor("#6a11cb")),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    # Thank you message
    story.append(Paragraph(
        "<b>Thank you for choosing Sri Vari Mahal A/C for your special occasion!</b>",
        footer_style
    ))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "We are committed to making your event memorable and successful.",
        footer_style
    ))
    story.append(Spacer(1, 12))
    
    # Contact Information
    contact_info = """
    <b>Contact:</b> +91 98431 86231 | +91 88702 01981<br/>
    <b>Email:</b> srivarimahal2025kpm@gmail.com<br/>
    <b>Address:</b> Kannadasan Street, Abirami Nagar, Kanchipuram - 631551
    """
    story.append(Paragraph(contact_info, footer_style))
    story.append(Spacer(1, 15))
    
    # Computer generated note
    story.append(Paragraph(
        "<i>This is a computer-generated receipt and does not require a signature.</i>",
        footer_style
    ))

    # ==========================================
    # BUILD PDF
    # ==========================================
    
    doc.build(story, onFirstPage=draw_elegant_border, onLaterPages=draw_elegant_border)
    
    return response

from .models import Expense
from .serializers import ExpenseSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import csv

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expenses_list(request):
    if request.method == 'GET':
        expenses = Expense.objects.all().order_by('-function_date')
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    try:
        exp = Expense.objects.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if request.method == 'PUT':
        serializer = ExpenseSerializer(exp, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        exp.delete()
        return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_expenses(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Function Date", "Advance", "Balance", "Damage Recovery",
        "Gens", "Ladies", "Flag", "Waste Cleaning",
        "Electrician", "Radio", "Light", "Total"
    ])

    for e in Expense.objects.all():
        writer.writerow([
            e.function_date, e.advance, e.balance, e.damage_recovery,
            e.gens, e.ladies, e.flag, e.waste_room_cleaning,
            e.electrician, e.radio, e.light, e.total
        ])

    return response