import React from "react";
import { useLocation, Link } from "react-router-dom";
import "../App.css";

const BookingSuccess = () => {
  const { state } = useLocation();
  const booking = state?.booking;

  return (
    <div className="home-container">
      <div className="form-container">
        <h2>🎉 Booking Confirmed!</h2>

        {booking ? (
          <>
            <div className="success-badge">Successfully Submitted</div>
            <p>Thank you, <strong>{booking.name}</strong>.</p>
            <p>Your booking for <strong>{booking.event_type}</strong> has been received.</p>
            <p><strong>Date: </strong>{booking?.from_date} - {booking?.to_date}</p>
            <p>We will contact you shortly with further details.</p>
          </>
        ) : (
          <p>We couldn't load your booking details.  
                If you recently submitted a booking, please check your email or contact us.</p>
        )}
        <Link to="/" className="success-btn">
          Go Back to Home
        </Link>
      </div>
    </div>
  );
};
export default BookingSuccess;
