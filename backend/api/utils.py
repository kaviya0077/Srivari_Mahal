from django.core.mail import send_mail
from django.conf import settings

# =====================================================
# 📧 EMAIL NOTIFICATIONS (Customer + Owner)
# =====================================================
def send_booking_confirmation(booking):
    """
    Send booking confirmation email to customer and notification to owner
    """
    print(f"📧 SENDING EMAIL TO: {booking.email}")
    
    try:
        # Customer email
        subject = "🎉 Booking Confirmed — Sri Vari Mahal"
        message = f"""
Dear {booking.name},

Your booking has been successfully received.

📅 Event: {booking.event_type}
📆 From Date: {booking.from_date}
📆 To Date: {booking.to_date}
⏰ Time: {booking.start_time} to {booking.end_time}
👥 Estimated Guests: {booking.estimated_guests}

📌 Status: {booking.status}

We are excited to host your event at Sri Vari Mahal.
Our team will reach out soon for further coordination.

Warm Regards,  
Sri Vari Mahal A/C
📞 +91 98431 86231
📞 +91 88702 01981
📧 srivarimahal2025kpm@gmail.com
"""

        # Correct parameter order:
        # send_mail(subject, message, from_email, recipient_list, fail_silently)
        send_mail(
            subject,                                    # Subject
            message,                                    # Message body
            settings.DEFAULT_FROM_EMAIL,                # From email (must be configured)
            [booking.email],                            # Recipient list (to customer)
            fail_silently=False,
        )
        
        print("✅ CUSTOMER EMAIL SENT SUCCESSFULLY")
        
        # Optional: Send notification to owner
        owner_subject = f"🔔 New Booking: {booking.event_type}"
        owner_message = f"""
New booking received!

Customer: {booking.name}
Phone: {booking.phone}
Email: {booking.email}
Event: {booking.event_type}
Date: {booking.from_date} to {booking.to_date}
Guests: {booking.estimated_guests}
Status: {booking.status}

Please review and confirm.
"""
        
        send_mail(
            owner_subject,
            owner_message,
            settings.DEFAULT_FROM_EMAIL,
            ["srivarimahal2025kpm@gmail.com"],          # 
            fail_silently=True,                         
        )
        
        print("✅ OWNER NOTIFICATION SENT")
        
    except Exception as e:
        print(f"❌ EMAIL ERROR: {str(e)}")
        raise  # Re-raise to see the full error in console