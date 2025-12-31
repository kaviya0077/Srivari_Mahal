# backend/api/utils.py

from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from twilio.rest import Client


# =====================================================
# 📧 EMAIL NOTIFICATIONS (Customer + Owner)
# =====================================================
def send_booking_confirmation(booking):
    print("📧 SENDING EMAIL TO:", booking.email)
    subject = "🎉 Booking Confirmed — Sri Vari Mahal"
    message = f"""
Dear {booking.name},

Your booking has been successfully received.

📅 Event: {booking.event_type}
📆 Date: {booking.event_date}
⏰ Time: {booking.start_time} to {booking.end_time}

💰 Total Amount: ₹{booking.total_amount}
📌 Status: {booking.status}

We are excited to host your event at Sri Vari Mahal.
Our team will reach out soon for further coordination.

Warm Regards,  
Sri Vari Mahal A/C
📞 +91 98431 86231
📞 +91 88702 01981
"""

    send_mail(
        subject,
        message,
        "srivarimahal2025kpm@gmail.com",                     
        [booking.email],
        fail_silently=False,
    )

    # ------------------------------
    # Email to Owner (Admin)
    # ------------------------------
    # owner_email = getattr(settings, "OWNER_EMAIL", None)
    # if owner_email:
    #     send_mail(
    #         f"New Booking #{booking.id}",
    #         f"New booking details: {booking}",
    #         settings.DEFAULT_FROM_EMAIL,
    #         [owner_email],
    #         fail_silently=True
    #     )


# =====================================================
# 📱 SMS NOTIFICATIONS via Twilio
# =====================================================
# def send_sms(to, body):
#     """
#     Sends SMS to user using Twilio.
#     """

#     client = Client(
#         settings.TWILIO_ACCOUNT_SID,
#         settings.TWILIO_AUTH_TOKEN
#     )

#     client.messages.create(
#         body=body,
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=to
#     )