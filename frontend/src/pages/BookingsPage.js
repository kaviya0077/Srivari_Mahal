import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api";

export default function BookingsPage() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

  const loadBookings = async () => {
    try {
      const res = await API.get("/bookings/");
      const sortedBookings = res.data.sort((a, b) => a.id - b.id);
      setBookings(sortedBookings);
      setError(null);
    } catch (err) {
      console.error("Error fetching bookings:", err);
      setError(err.response?.data || "Failed to load bookings.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookings();
  }, []);

  const handleApprove = async (id) => {
    if (!window.confirm("Approve this booking?")) return;
    try {
      await API.patch(`/bookings/${id}/status/`, { status: "approved" });
      alert("Booking approved!");
      loadBookings();
    } catch (error) {
      setError(error.response?.data || "Failed to approve booking.");
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm("Reject this booking?")) return;
    try {
      await API.patch(`/bookings/${id}/status/`, { status: "rejected" });
      alert("Booking rejected!");
      loadBookings();
    } catch (error) {
      setError(error.response?.data || "Failed to reject booking.");
    }
  };

// Updated to use environment variable
  const downloadCSV = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/bookings/export/`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sri_vari_mahal_bookings_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      alert("✅ CSV downloaded successfully!");
    } catch (error) {
      console.error("❌ Export failed:", error);
      alert("Failed to export CSV. Please try again.");
    }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString("en-GB");

    const getStatusBadgeClass = (status) => {
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

  // 🔔 Show API errors at the top (but not per-field)
  const renderErrors = () => {
    if (!error) return null;

    // Plain string
    if (typeof error === "string") {
      return <div className="error-box">{error}</div>;
    }

    // DRF error object
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

  if (loading) return <div className="page-container">Loading bookings...</div>;
  if (error && !bookings.length)
    return <div className="page-container">{renderErrors()}</div>;

  return (
    <div className="page-container">
      {renderErrors()}

      <h2 className="page-title">Bookings</h2>

      <button className="btn-csv-simple" onClick={downloadCSV}>
        Download CSV
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
              <th>Evnet Time</th>
              <th>Actions</th>
              <th>Receipt</th>
            </tr>
          </thead>

          <tbody>
            {bookings.map((b) => (
              <tr key={b.id}>
                <td>{b.id}</td>
                <td>{b.name}</td>
                <td>{b.event_type}</td>
                <td>
                  <span className={getStatusBadgeClass(b.status)}>
                    {b.status}
                  </span>
                </td>
                <td>{formatDate(b.from_date)} → {formatDate(b.to_date)}</td>
                <td>{b.start_time} → {b.end_time}</td>

                <td>
                  <button
                    className="booking-btn btn-approve"
                    onClick={() => handleApprove(b.id)}
                  >
                    Approve
                  </button>

                  <button
                    className="booking-btn btn-reject"
                    onClick={() => handleReject(b.id)}
                  >
                    Reject
                  </button>
                </td>
                <td>
                  <a
                    href={`http://127.0.0.1:8000/api/bookings/${b.id}/receipt/`}
                    target="blank"
                    rel="noopener noreferrer"
                    className="btn-view-simple"
                  >
                    View
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}