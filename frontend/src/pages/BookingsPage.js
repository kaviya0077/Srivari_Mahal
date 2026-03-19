import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";

export default function BookingsPage() {
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState("Checking...");

  // ✅ Get API base URL
  const getApiBaseUrl = () => {
    if (process.env.REACT_APP_API_URL) {
      return process.env.REACT_APP_API_URL.replace('/api', '');
    }
    
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return "http://localhost:8000";
    }
    
    return "https://your-backend-domain.com";
  };

  const API_BASE_URL = getApiBaseUrl();

  // ✅ Test API connectivity
  const testApiConnection = async () => {
    try {
      console.log("🔍 Testing API connection to:", API_BASE_URL);
      const response = await API.get("/bookings/");
      console.log("✅ API Connection successful");
      setApiStatus("Connected ✓");
      return true;
    } catch (err) {
      console.error("❌ API Connection failed:", err);
      setApiStatus(`Failed: ${err.message}`);
      return false;
    }
  };

  // ✅ Load bookings with ASCENDING order (1, 2, 3...)
  const loadBookings = async () => {
    try {
      setLoading(true);
      setError("");
      
      console.log("📡 Fetching bookings from API...");
      const res = await API.get("/bookings/");
      
      console.log("📦 Raw API Response:", res.data);
      console.log("📊 Total bookings received:", res.data?.length || 0);

      if (!res.data || res.data.length === 0) {
        console.warn("⚠️ No bookings found in response");
        setBookings([]);
        setError("No bookings found in the system.");
        return;
      }

      // ✅ CRITICAL: Sort by ID in ASCENDING order (1, 2, 3...)
      // NOT descending like before (which was b.id - a.id)
      const sortedBookings = res.data.sort((a, b) => a.id - b.id);
      
      console.log("✅ Bookings loaded successfully:", sortedBookings.length);
      console.log("📊 Order:", sortedBookings.map(b => b.id).join(", "));
      
      setBookings(sortedBookings);
      setError(null);
    } catch (err) {
      console.error("❌ Error fetching bookings:", err);
      console.error("Error response:", err.response);
      
      const errorMsg = err.response?.data?.detail || 
                       err.response?.data?.error || 
                       err.message || 
                       "Failed to load bookings";
      
      setError(errorMsg);
      setBookings([]);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Run on component mount
  useEffect(() => {
    console.log("🚀 BookingsPage mounted");
    testApiConnection();
    loadBookings();
  }, []);

  const handleApprove = async (id) => {
    if (!window.confirm("Approve this booking?")) return;
    try {
      console.log("✅ Approving booking:", id);
      await API.patch(`/bookings/${id}/status/`, { status: "approved" });
      alert("Booking approved!");
      loadBookings();
    } catch (error) {
      console.error("❌ Approve error:", error);
      setError(error.response?.data?.detail || "Failed to approve booking.");
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm("Reject this booking?")) return;
    try {
      console.log("❌ Rejecting booking:", id);
      await API.patch(`/bookings/${id}/status/`, { status: "rejected" });
      alert("Booking rejected!");
      loadBookings();
    } catch (error) {
      console.error("❌ Reject error:", error);
      setError(error.response?.data?.detail || "Failed to reject booking.");
    }
  };

const downloadCSV = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/bookings/export/`, {
      method: 'GET',
      headers: {
        // ✅ Do NOT send "Accept: text/csv" — let browser accept anything
        ...(token && { 'Authorization': `Bearer ${token}` }),
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    // ✅ .xlsx extension now
    link.setAttribute('download', `sri_vari_mahal_bookings_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("❌ Export failed:", error);
    alert("Failed to export: " + error.message);
  }
};

  // ✅ Format date helper
  const formatDate = (d) => {
    if (!d) return "N/A";
    return new Date(d).toLocaleDateString("en-GB");
  };

  // ✅ Get status badge class
  const getStatusBadgeClass = (status) => {
    if (!status) return "status-badge status-default";
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case "approved":
        return "status-badge status-approved";
      case "rejected":
        return "status-badge status-rejected";
      case "pending":
        return "status-badge status-pending";
      default:
        return "status-badge status-default";
    }
  };

  // ✅ Render error messages
  const renderErrors = () => {
    if (!error) return null;

    if (typeof error === "string") {
      return (
        <div className="error-box">
          <strong>⚠️ Error:</strong> {error}
        </div>
      );
    }

    return (
      <div className="error-box">
        {Object.entries(error).map(([field, messages]) => (
          <p key={field}>
            <strong>{field}:</strong>{" "}
            {Array.isArray(messages) ? messages.join(", ") : messages}
          </p>
        ))}
      </div>
    );
  };

  // ✅ Loading state
  if (loading) {
    return (
      <div className="page-container">
        <h2 className="page-title">Bookings Management</h2>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>⏳ Loading bookings...</p>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>API Status: {apiStatus}</p>
        </div>
      </div>
    );
  }

  // ✅ Error state with no bookings
  if (error && bookings.length === 0) {
    return (
      <div className="page-container">
        <h2 className="page-title">Bookings Management</h2>
        {renderErrors()}
        <div style={{ 
          textAlign: 'center', 
          padding: '40px',
          backgroundColor: '#f9f9f9',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <p style={{ fontSize: '1.1rem', color: '#666' }}>
            🔍 No bookings to display
          </p>
          <p style={{ fontSize: '0.9rem', color: '#999' }}>
            Bookings will appear here once they are created.
          </p>
          <button 
            onClick={() => loadBookings()}
            style={{
              marginTop: '15px',
              padding: '10px 20px',
              backgroundColor: '#4b6cb7',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            🔄 Refresh
          </button>
        </div>
      </div>
    );
  }

  // ✅ Main render
  return (
    <div className="page-container">
      {renderErrors()}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
        <h2 className="page-title">Bookings Management</h2>
        <p style={{ fontSize: '0.85rem', color: '#666' }}>
          {/* 📊 Total: <strong>{bookings.length}</strong> bookings | API: {apiStatus} */}
        </p>
      </div>

      <button className="btn-csv-simple" onClick={downloadCSV}>
        📥 Download CSV
      </button>

      <div className="table-wrapper">
        <table className="styled-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Event</th>
              <th>Status</th>
              <th>Event Date</th>
              <th>Event Time</th>
              <th>Actions</th>
              <th>Edit</th>
            </tr>
          </thead>

          <tbody>
            {bookings && bookings.length > 0 ? (
              bookings.map((b) => (
                <tr key={b.id}>
                  <td><strong>{b.id}</strong></td>
                  <td>{b.name || "N/A"}</td>
                  <td>{b.event_type || "N/A"}</td>
                  <td>
                    <span className={getStatusBadgeClass(b.status)}>
                      {b.status || "Unknown"}
                    </span>
                  </td>
                  <td>
                    {b.from_date && b.to_date 
                      ? `${formatDate(b.from_date)} → ${formatDate(b.to_date)}`
                      : "N/A"
                    }
                  </td>
                  <td>
                    {b.start_time && b.end_time
                      ? `${b.start_time} → ${b.end_time}`
                      : "N/A"
                    }
                  </td>

                  <td>
                    {b.status && b.status.toLowerCase() === 'pending' ? (
                      <>
                        <button
                          className="booking-btn btn-approve"
                          onClick={() => handleApprove(b.id)}
                          title="Approve this booking"
                        >
                          ✓ Approve
                        </button>

                        <button
                          className="booking-btn btn-reject"
                          onClick={() => handleReject(b.id)}
                          title="Reject this booking"
                        >
                          ✗ Reject
                        </button>
                      </>
                    ) : (
                      <span style={{ 
                        color: b.status === 'approved' ? '#28a745' : '#dc3545',
                        fontWeight: '600',
                        fontSize: '0.9rem'
                      }}>
                        {b.status === 'approved' ? '✓ Approved' : '✗ Rejected'}
                      </span>
                    )}
                  </td>
                  
                  <td>
                    <button
                      className="btn-edit"
                      onClick={() => navigate(`/bookings/edit/${b.id}`)}
                      title="Edit this booking"
                    >
                      ✏️ Edit
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '30px' }}>
                  No bookings found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Info panel - shows booking IDs in order
      <div style={{
        marginTop: '30px',
        padding: '15px',
        backgroundColor: '#f0f7ff',
        borderRadius: '6px',
        fontSize: '0.9rem',
        color: '#0066cc',
        border: '1px solid #b3d9ff'
      }}> */}
        {/* <strong>📊 Booking IDs in Order:</strong> {bookings.length > 0 ? bookings.map(b => b.id).join(", ") : "No bookings"} */}
      {/* </div> */}
    </div>
  );
}