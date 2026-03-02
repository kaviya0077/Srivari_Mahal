// src/pages/EditBookingPage.js
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../api";
import "../App.css";

const EditBookingPage = () => {
  const { id } = useParams();
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
    status: "",
  });

  const [receiptData, setReceiptData] = useState({
    receipt_number: "",
    issue_date: new Date().toISOString().split('T')[0],
    admin_remarks: "",
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);

  const getApiBaseUrl = () => {
    if (process.env.REACT_APP_API_URL) {
      return process.env.REACT_APP_API_URL.replace('/api', '');
    }
    return window.location.hostname === 'localhost' 
      ? "http://localhost:8000" 
      : "https://srivari-mahal.onrender.com";
  };

  const API_BASE_URL = getApiBaseUrl();

  useEffect(() => {
    loadBooking();
  }, [id]);

  const loadBooking = async () => {
    try {
      const res = await API.get(`/bookings/${id}/`);
      setFormData(res.data);
      
      // Auto-generate receipt number if not exists
      setReceiptData(prev => ({
        ...prev,
        receipt_number: `SVM-${String(res.data.id).padStart(4, '0')}`,
      }));
      
      setLoading(false);
    } catch (err) {
      console.error("Error loading booking:", err);
      setError(
        typeof err.response?.data === 'string' 
          ? err.response.data 
          : "Failed to load booking details"
      );
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleReceiptChange = (e) => {
    const { name, value } = e.target;
    console.log(`📝 Receipt field changed: ${name} = "${value}"`);
    setReceiptData({ ...receiptData, [name]: value });
  };
  
const handleUpdate = async (e) => {
  e.preventDefault();
  
  try {
    await API.patch(`/bookings/${id}/`, formData);
    alert("✅ Booking updated successfully!");
  } catch (err) {
    console.error("Error updating booking:", err);
    console.error("❌ Error details:", err.response?.data); // ✅ Log the actual error
    
    // Show the actual validation error
    const errorMsg = err.response?.data?.non_field_errors 
      ? err.response.data.non_field_errors.join(', ')
      : JSON.stringify(err.response?.data) || "Failed to update booking";
    
    setError(errorMsg);
    alert(`Update failed: ${errorMsg}`); // ✅ Show user the error
  }
};

const handleGenerateReceipt = async () => {
  setGenerating(true);
  
  try {
    console.log("📤 Updating booking...");
    await API.patch(`/bookings/${id}/`, formData);
    console.log("✅ Booking updated");
    
    const token = localStorage.getItem('access_token');

    // Build query parameters - properly encode all values
    const params = new URLSearchParams();
    params.append('receipt_number', receiptData.receipt_number);
    params.append('issue_date', receiptData.issue_date);
    
    // ✅ Only add admin_remarks if it has content
    if (receiptData.admin_remarks && receiptData.admin_remarks.trim()) {
      params.append('admin_remarks', receiptData.admin_remarks.trim());
    }
    
    console.log("📄 Receipt params:", params.toString());
    console.log("📝 Admin remarks:", receiptData.admin_remarks);

    // ✅ Append params to URL
    const response = await fetch(`${API_BASE_URL}/api/bookings/${id}/receipt/?${params.toString()}`, {
      method: 'GET',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Server response:', errorText);
      throw new Error(`Failed to generate receipt: ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Receipt_${receiptData.receipt_number}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    alert("✅ Receipt generated successfully!");
  } catch (error) {
    console.error("❌ Receipt generation failed:", error);
    alert(`Failed to generate receipt: ${error.message}`);
  } finally {
    setGenerating(false);
  }
};

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          Loading booking details...
        </div>
      </div>
    );
  }
  
  if (error && !formData.name) {
    return (
      <div className="page-container">
        <div className="error-box">{String(error)}</div>
        <button 
          onClick={() => navigate('/bookings')} 
          className="btn-primary" 
          style={{ marginTop: '20px' }}
        >
          ← Back to Bookings
        </button>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="form-container">
        <h2>Edit Booking - ID: {id}</h2>

        {error && <div className="error-box">{String(error)}</div>}

        <form onSubmit={handleUpdate}>
          {/* Customer Details Section */}
          <h3 style={{ gridColumn: 'span 3', color: '#0F3057', marginTop: '20px' }}>
            Customer Details
          </h3>

          <input
            type="text"
            name="name"
            placeholder="Full Name"
            value={formData.name}
            onChange={handleChange}
            className="full-width"
            required
          />

          <input
            type="tel"
            name="phone"
            placeholder="Phone Number"
            value={formData.phone}
            onChange={handleChange}
            required
          />

          <input
            type="tel"
            name="alternate_phone"
            placeholder="Alternate Contact"
            value={formData.alternate_phone || ''}
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

          <input
            type="text"
            name="address_line"
            placeholder="Street / Address Line"
            value={formData.address_line || ''}
            onChange={handleChange}
            className="full-width"
          />

          <input
            type="text"
            name="state"
            placeholder="State"
            value={formData.state || ''}
            onChange={handleChange}
          />

          <input
            type="text"
            name="city"
            placeholder="City"
            value={formData.city || ''}
            onChange={handleChange}
          />

          <input
            type="text"
            name="pincode"
            placeholder="Pincode"
            value={formData.pincode || ''}
            onChange={handleChange}
          />

          {/* Event Details Section */}
          <h3 style={{ gridColumn: 'span 3', color: '#0F3057', marginTop: '20px' }}>
            Event Details
          </h3>

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

            <input
              type="number"
              name="estimated_guests"
              placeholder="Estimated Guests"
              value={formData.estimated_guests || ''}
              onChange={handleChange}
            />

            <select
              name="food_preference"
              value={formData.food_preference || ''}
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

            <input
              type="date"
              name="to_date"
              value={formData.to_date}
              onChange={handleChange}
              required
            />

            <input
              type="time"
              name="start_time"
              value={formData.start_time || ''}
              onChange={handleChange}
            />

            <input
              type="time"
              name="end_time"
              value={formData.end_time || ''}
              onChange={handleChange}
            />
          </div>

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            style={{ gridColumn: 'span 3' }}
          >
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>

          <textarea
            name="message"
            placeholder="Customer Message / Special Requests"
            value={formData.message || ''}
            onChange={handleChange}
            className="full-width"
            rows={3}
          />

          {/* Receipt Generation Section */}
          <h3 style={{ 
            gridColumn: 'span 3', 
            color: '#0F3057', 
            marginTop: '30px', 
            borderTop: '2px solid #6a11cb', 
            paddingTop: '20px' 
          }}>
            Receipt Details
          </h3>

          <input
            type="text"
            name="receipt_number"
            placeholder="Receipt Number (e.g., SVM-0001)"
            value={receiptData.receipt_number}
            onChange={handleReceiptChange}
            required
          />

          <input
            type="date"
            name="issue_date"
            value={receiptData.issue_date}
            onChange={handleReceiptChange}
            required
          />

          <div style={{ gridColumn: 'span 1' }}></div>

          <textarea
            name="admin_remarks"
            placeholder="Admin Remarks (will be printed on receipt)"
            value={receiptData.admin_remarks}
            onChange={handleReceiptChange}
            style={{ gridColumn: 'span 3' }}
            rows={4}
          />

          {/* Action Buttons */}
          <button 
            type="submit" 
            className="btn-primary" 
            style={{ gridColumn: 'span 1' }}
          >
            Update Booking
          </button>

          <button
            type="button"
            onClick={handleGenerateReceipt}
            disabled={generating}
            className="btn-primary"
            style={{ 
              gridColumn: 'span 2',
              background: generating 
                ? '#ccc' 
                : 'linear-gradient(90deg, #28a745, #20c997)',
              cursor: generating ? 'not-allowed' : 'pointer'
            }}
          >
            {generating ? 'Generating...' : '📄 Generate Receipt'}
          </button>

          <button
            type="button"
            onClick={() => navigate('/bookings')}
            style={{
              gridColumn: 'span 3',
              marginTop: '10px',
              background: '#6c757d',
              color: 'white',
              padding: '12px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            ← Back to Bookings
          </button>
        </form>
      </div>
    </div>
  );
};

export default EditBookingPage;