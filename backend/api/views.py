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
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def draw_border(pdf):
    pdf.setStrokeColor(colors.HexColor("#4b6cb7"))
    pdf.setLineWidth(3)
    pdf.rect(25, 25, 545, 792, stroke=1, fill=0)

def booking_receipt(request, pk):
    booking = Booking.objects.get(pk=pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="receipt_{booking.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60)
    styles = getSampleStyleSheet()

    header = Paragraph(
        "<b><font size=18 color='#2a0845'>Sri Vari Mahal A/C</font></b>",
        styles["Title"],
    )

    subtitle = Paragraph(
        "<font size=12 color='#555'>Booking Confirmation Receipt</font>",
        styles["Normal"],
    )

    details_table = Table(
        [
            ["Receipt No:", f"R-{booking.id}", "Date:", booking.created_at.strftime('%d-%m-%Y')],
        ],
        colWidths=[90, 180, 90, 120],
    )
    details_table.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.gray),
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ])
    )

    section_style = ParagraphStyle(
        "section",
        parent=styles["Heading3"],
        textColor=colors.HexColor("#4b6cb7"),
    )

    customer = Table(
        [
            ["Name", booking.name],
            ["Phone", booking.phone],
            ["Email", booking.email or "-"],
            ["Address", booking.address_line or "-"],
        ],
        colWidths=[120, 350],
    )

    customer.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.aliceblue),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.gray),
    ]))

    event = Table(
        [
            ["Event Type", booking.event_type],
            ["Event Dates", f"{booking.from_date} → {booking.to_date}"],
            ["Event Time", f"{booking.start_time} → {booking.end_time}"],
            ["Guests", booking.estimated_guests],
        ],
        colWidths=[120, 350],
    )

    event.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.aliceblue),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.gray),
    ]))

    payments = Table(
        [
            # ["Total Amount", f"₹ {booking.total_amount or 0}"],
            # ["Advance Paid", f"₹ {booking.paid_amount or 0}"],
            # ["Balance", f"₹ {(booking.total_amount or 0) - (booking.paid_amount or 0)}"],
            ["Status", booking.status.capitalize()],
        ],
        colWidths=[120, 350],
    )

    payments.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.aliceblue),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.gray),
    ]))

    footer = Paragraph(
        "<br/><font size=9 color='#555'>Thank you for choosing Sri Vari Mahal. "
        "We look forward to hosting your event!<br/>"
        "📞 98431 86231 | 88702 01981</font>",
        styles["Normal"],
    )

    content = [
        header, subtitle, Spacer(1, 10),
        details_table, Spacer(1, 16),

        Paragraph("Customer Details", section_style),
        customer, Spacer(1, 14),

        Paragraph("Event Details", section_style),
        event, Spacer(1, 14),

        Paragraph("Payment Summary", section_style),
        payments, Spacer(1, 20),

        footer
    ]

    def on_first_page(pdf, doc):
        draw_border(pdf)

    doc.build(content, onFirstPage=on_first_page)
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