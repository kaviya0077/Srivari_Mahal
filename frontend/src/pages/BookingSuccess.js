import React, { useEffect } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import "../App.css";

const BookingSuccess = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const booking = state?.booking;

  // Redirect to home if accessed directly without booking data
  useEffect(() => {
    if (!booking) {
      console.warn("No booking data found in navigation state");
    }
  }, [booking]);

  return (
    <div className="home-container">
      <div className="form-container booking-success">
        {booking ? (
          <>
            <h2>🎉 Booking Confirmed!</h2>
            <div className="success-badge">Successfully Submitted</div>
            
            <p>Thank you, <strong>{booking.name}</strong>!</p>
            <p>Your booking for <strong>{booking.event_type}</strong> has been received.</p>
            
            {booking.from_date && booking.to_date && (
              <p>
                <strong>Date: </strong>
                {booking.from_date} {booking.to_date !== booking.from_date && `to ${booking.to_date}`}
              </p>
            )}
            
            {booking.phone && (
              <p><strong>Contact: </strong>{booking.phone}</p>
            )}
            
            <p>We will contact you shortly with further details.</p>
            
            <Link to="/" className="success-btn">
              Go Back to Home
            </Link>
          </>
        ) : (
          <>
            <h2>Booking Submitted</h2>
            <p>
              Your booking has been successfully submitted! 
              We will contact you shortly with further details.
            </p>
            <p>
              If you don't receive a confirmation email within 24 hours, 
              please contact us directly.
            </p>
            <Link to="/" className="success-btn">
              Go Back to Home
            </Link>
          </>
        )}
      </div>
    </div>
  );
};

export default BookingSuccess;