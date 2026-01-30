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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.http import HttpResponse
from datetime import datetime
from .models import Booking

def draw_modern_header(c, doc):
    """Draw modern header with gradient background"""
    width, height = A4
    
    # Top gradient banner - compact
    c.setFillColor(colors.HexColor("#1a237e"))
    c.rect(0, height - 75, width, 75, fill=1, stroke=0)
    
    # Accent stripe
    c.setFillColor(colors.HexColor("#00bcd4"))
    c.rect(0, height - 82, width, 7, fill=1, stroke=0)
    
    # Bottom accent line
    c.setStrokeColor(colors.HexColor("#00bcd4"))
    c.setLineWidth(2)
    c.line(40, height - 88, width - 40, height - 88)

def booking_receipt(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return HttpResponse("Booking not found", status=404)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="SriVari_Receipt_{booking.id}.pdf"'

    # Create PDF with optimized margins for full single page
    doc = SimpleDocTemplate(
        response, 
        pagesize=A4,
        rightMargin=38,
        leftMargin=38,
        topMargin=98,
        bottomMargin=32
    )
    
    styles = getSampleStyleSheet()
    story = []

    # ==========================================
    # CUSTOM STYLES
    # ==========================================
    
    # Label style
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=13
    )
    
    # Value style
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#212121"),
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    )
    
    # Section Header Style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor("#1a237e"),
        spaceAfter=3,
        spaceBefore=5,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leftIndent=10
    )
    
    # Footer style
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#616161"),
        alignment=TA_CENTER,
        leading=11
    )

    # ==========================================
    # RECEIPT INFO BAR
    # ==========================================
    
    story.append(Spacer(1, 4))
    
    receipt_data = [
        [
            Paragraph(f"<b>Receipt #:</b> SVM-{str(booking.id).zfill(4)}", value_style),
            Paragraph(f"<b>Issue Date:</b> {booking.created_at.strftime('%d %b %Y')}", value_style),
            Paragraph(f"<b>Status:</b> <font color='{'#155724' if booking.status=='approved' else '#856404' if booking.status=='pending' else '#721c24'}'>{booking.status.upper()}</font>", value_style)
        ]
    ]
    
    # Status-based color
    status_colors = {
        'pending': colors.HexColor("#fff9e6"),
        'approved': colors.HexColor("#e8f5e9"),
        'rejected': colors.HexColor("#ffebee")
    }
    
    receipt_table = Table(receipt_data, colWidths=[180, 180, 180])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_colors.get(booking.status.lower(), colors.HexColor("#f5f5f5"))),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#00bcd4")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(receipt_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # CUSTOMER DETAILS
    # ==========================================
    
    story.append(Paragraph("CUSTOMER INFORMATION", section_style))
    story.append(Spacer(1, 2))
    
    customer_data = [
        [Paragraph("Full Name", label_style), Paragraph(booking.name, value_style)],
        [Paragraph("Contact", label_style), Paragraph(booking.phone, value_style)],
        [Paragraph("Email", label_style), Paragraph(booking.email or "Not Provided", value_style)],
        [Paragraph("Address", label_style), Paragraph(booking.address_line or "Not Provided", value_style)],
    ]
    
    customer_table = Table(customer_data, colWidths=[130, 410])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e3f2fd")),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#90caf9")),
        ('LINEBELOW', (0, -1), (-1, -1), 0, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # EVENT DETAILS
    # ==========================================
    
    story.append(Paragraph("EVENT DETAILS", section_style))
    story.append(Spacer(1, 2))
    
    # Format dates nicely
    same_day = booking.from_date == booking.to_date
    if same_day:
        event_date_str = booking.from_date.strftime('%d %B %Y')
    else:
        event_date_str = f"{booking.from_date.strftime('%d %b')} - {booking.to_date.strftime('%d %b %Y')}"
    
    event_data = [
        [Paragraph("Event Type", label_style), Paragraph(booking.event_type, value_style)],
        [Paragraph("Event Date", label_style), Paragraph(event_date_str, value_style)],
        [Paragraph("Event Time", label_style), Paragraph(f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}", value_style)],
        [Paragraph("Expected Guests", label_style), Paragraph(f"{booking.estimated_guests} Guests", value_style)],
        [Paragraph("Food Preference", label_style), Paragraph(booking.food_preference or "To be decided", value_style)],
    ]
    
    event_table = Table(event_data, colWidths=[130, 410])
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e3f2fd")),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#90caf9")),
        ('LINEBELOW', (0, -1), (-1, -1), 0, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(event_table)
    
    # ==========================================
    # SPECIAL REQUESTS - Conditional
    # ==========================================
    
    if booking.message:
        story.append(Spacer(1, 10))
        story.append(Paragraph("SPECIAL REQUESTS", section_style))
        story.append(Spacer(1, 2))
        
        message_data = [[Paragraph(booking.message, value_style)]]
        
        message_table = Table(message_data, colWidths=[540])
        message_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fff3e0")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#ffb74d")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(message_table)

    # ==========================================
    # BOOKING STATUS BADGE
    # ==========================================
    
    story.append(Spacer(1, 12))
    
    status_badge_colors = {
        'pending': (colors.HexColor("#fff3cd"), colors.HexColor("#856404")),
        'approved': (colors.HexColor("#d4edda"), colors.HexColor("#155724")),
        'rejected': (colors.HexColor("#f8d7da"), colors.HexColor("#721c24"))
    }
    
    bg_color, text_color = status_badge_colors.get(
        booking.status.lower(), 
        (colors.HexColor("#e0e0e0"), colors.black)
    )
    
    status_para = ParagraphStyle(
        'StatusBadge',
        parent=styles['Normal'],
        fontSize=13,
        textColor=text_color,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    status_data = [[Paragraph(f"BOOKING STATUS: {booking.status.upper()}", status_para)]]
    
    status_table = Table(status_data, colWidths=[540])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 2, text_color),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # FOOTER
    # ==========================================
    
    # Divider
    divider = Table([['']], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor("#00bcd4")),
    ]))
    story.append(divider)
    story.append(Spacer(1, 6))
    
    # Thank you message
    story.append(Paragraph(
        "<b>Thank You for Choosing Sri Vari Mahal A/C!</b>",
        ParagraphStyle('ThankYou', parent=styles['Normal'], fontSize=11,
                      textColor=colors.HexColor("#1a237e"), alignment=TA_CENTER, 
                      fontName='Helvetica-Bold', spaceAfter=4)
    ))
    
    story.append(Paragraph(
        "We look forward to making your celebration truly memorable.",
        footer_style
    ))
    story.append(Spacer(1, 5))
    
    # Contact info - compact format
    contact_data = [
        [Paragraph("Phone: +91 98431 86231 | +91 88702 01981", footer_style)],
        [Paragraph("Email: srivarimahal2025kpm@gmail.com", footer_style)],
        [Paragraph("Address: Sri Vari Mahal A/C - Grand Marriage & Party Hall, Kannadasan Street, Abirami Nagar, Baluchetty Chatram, Sirunaiperugal, Kanchipuram - 631551", footer_style)]
    ]
    
    contact_table = Table(contact_data, colWidths=[540])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(contact_table)
    story.append(Spacer(1, 5))
    
    # Disclaimer
    story.append(Paragraph(
        "<i>This is a computer-generated document. No signature required.</i>",
        ParagraphStyle('Disclaimer', parent=footer_style, fontSize=7,
                      textColor=colors.HexColor("#9e9e9e"))
    ))

    # ==========================================
    # BUILD PDF WITH HEADER ON FIRST PAGE
    # ==========================================
    
    def first_page(c, doc):
        c.saveState()
        draw_modern_header(c, doc)
        
        # Add title and subtitle on the colored header
        width, height = A4
        c.setFont('Helvetica-Bold', 20)
        c.setFillColor(colors.white)
        c.drawCentredString(width / 2, height - 35, "SRI VARI MAHAL A/C")
        
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor("#b3e5fc"))
        c.drawCentredString(width / 2, height - 50, "Grand Marriage & Party Hall")
        c.drawCentredString(width / 2, height - 62, "Booking Confirmation Receipt")
        c.restoreState()

    doc.build(story, onFirstPage=first_page)
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