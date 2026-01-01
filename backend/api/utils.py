from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_booking_confirmation(booking):
    try:
        subject = f"Booking Confirmation - {booking.event_type}"
        message = f"""
Dear {booking.name},

Thank you for booking with Sri Vari Mahal A/C!

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event Type: {booking.event_type}
Date: {booking.from_date} to {booking.to_date}
Time: {booking.start_time} - {booking.end_time}
Guests: {booking.estimated_guests or 'Not specified'}
Food Preference: {booking.food_preference or 'Not specified'}

Contact Details:
Name: {booking.name}
Phone: {booking.phone}
Email: {booking.email}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We will contact you shortly to confirm your booking and discuss further details.

Best regards,
Sri Vari Mahal A/C Team
📞 98431 86231 | 88702 01981
        """

        logger.info(f"📧 Sending email to: {booking.email}")
        logger.info(f"📧 From: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"📧 Backend: {settings.EMAIL_BACKEND}")
        
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            fail_silently=False,
        )
        
        if result == 1:
            logger.info(f"✅ Email sent successfully to {booking.email}")
        else:
            logger.warning(f"⚠️ Email send returned {result}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Email sending failed: {str(e)}")
        logger.exception("Full traceback:")
        return False