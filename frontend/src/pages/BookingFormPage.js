// src/pages/BookingFormPage.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import "../App.css";

const BookingFormPage = () => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    alternate_phone: "",
    email: "",
    event_type: "",
    from_date: "",
    to_date: "",
    start_time: "",
    end_time: "",
    address_line: "",
    state: "",
    city: "",
    pincode: "",
    message: "",
    estimated_guests: "",
    food_preference: "",
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: "" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const res = await API.post("/bookings/", formData);
      console.log("✅ Booking Success:", res.data);
      
      // Navigate immediately with booking data
      navigate("/booking-success", {
        state: { booking: res.data },
        replace: true // This prevents going back to form with submitted data
      });

    } catch (err) {
      console.error("❌ Booking Error:", err.response?.data || err.message);

      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ non_field_errors: "Something went wrong. Please try again." });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="form-container">
        <h2>Book Your Event</h2>

        {errors.non_field_errors && (
          <div className="error-box">{errors.non_field_errors}</div>
        )}

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="name"
            placeholder="Full Name"
            value={formData.name}
            onChange={handleChange}
            className="full-width"
            required
          />
          {errors.name && <span className="error-text">{errors.name}</span>}

          <input
            type="tel"
            name="phone"
            placeholder="Phone Number"
            value={formData.phone}
            onChange={handleChange}
            required
          />
          {errors.phone && <span className="error-text">{errors.phone}</span>}

          <input
            type="tel"
            name="alternate_phone"
            placeholder="Alternate Contact"
            value={formData.alternate_phone}
            onChange={handleChange}
          />

          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={formData.email}
            onChange={handleChange}
            required
          />
          {errors.email && <span className="error-text">{errors.email}</span>}

          <input
            type="text"
            name="address_line"
            placeholder="Street / Address Line"
            value={formData.address_line}
            onChange={handleChange}
            className="full-width"
          />

          <input
            type="text"
            name="state"
            placeholder="State"
            value={formData.state}
            onChange={handleChange}
          />

          <input
            type="text"
            name="city"
            placeholder="City"
            value={formData.city}
            onChange={handleChange}
          />

          <input
            type="text"
            name="pincode"
            placeholder="Pincode"
            value={formData.pincode}
            onChange={handleChange}
          />

          <div className="three-row">

            <select
              name="event_type"
              value={formData.event_type}
              onChange={handleChange}
              required
            >
              <option value="">Select Event Type</option>
              <option value="Wedding">Wedding</option>
              <option value="Engagement">Engagement</option>
              <option value="Reception">Reception</option>
              <option value="Birthday">Birthday Party</option>
              <option value="Corporate">Corporate Event</option>
              <option value="Other">Other</option>
            </select>
            {errors.event_type && <span className="error-text">{errors.event_type}</span>}

            <input
              type="number"
              name="estimated_guests"
              placeholder="Estimated Guests"
              value={formData.estimated_guests}
              onChange={handleChange}
            />

            <select
              name="food_preference"
              value={formData.food_preference}
              onChange={handleChange}
            >
              <option value="">Food Preference</option>
              <option value="Veg">Veg</option>
              <option value="Non-Veg">Non-Veg</option>
              <option value="Both">Both</option>
            </select>

          </div>

          <div className="time-row">

            <input
              type="date"
              name="from_date"
              value={formData.from_date}
              onChange={handleChange}
              required
            />
            {errors.from_date && <span className="error-text">{errors.from_date}</span>}

            <input
              type="date"
              name="to_date"
              value={formData.to_date}
              onChange={handleChange}
              required
            />
            {errors.to_date && <span className="error-text">{errors.to_date}</span>}

            <input
              type="time"
              name="start_time"
              value={formData.start_time}
              onChange={handleChange}
            />

            <input
              type="time"
              name="end_time"
              value={formData.end_time}
              onChange={handleChange}
            />

          </div>

          <textarea
            name="message"
            placeholder="Additional Message"
            value={formData.message}
            onChange={handleChange}
            className="full-width"
            rows={4}
          />

          <button className="btn-primary full-width" type="submit" disabled={loading}>
            {loading ? "Submitting..." : "Submit Booking"}
          </button>

        </form>
      </div>
    </div>
  );
};

export default BookingFormPage;