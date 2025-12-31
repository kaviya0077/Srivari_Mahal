// src/pages/BookingDetailPage.js
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../api";
import jsPDF from "jspdf";

export default function BookingDetailPage() {
  const { id } = useParams();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);

    API.get(`bookings/${id}/`)
      .then((res) => {
        setBooking(res.data);
        setError("");
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load booking details.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  // ===============================
  // 📄 PDF RECEIPT GENERATION
  // ===============================
  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFont("Helvetica", "bold");
    doc.setFontSize(18);
    doc.text("Booking Receipt", 70, 20);
    doc.setFontSize(12);
    doc.setFont("Helvetica", "normal");
    doc.text(`Booking ID: ${booking.id}`, 20, 40);
    doc.text(`Client Name: ${booking.name}`, 20, 50);
    doc.text(`Phone: ${booking.phone}`, 20, 60);
    doc.text(`Email: ${booking.email}`, 20, 70);
    doc.text(`Event Type: ${booking.event_type}`, 20, 80);
    doc.text(
      `Event Date: ${new Date(booking.event_date).toLocaleDateString()}`,
      20,
      90
    );

    doc.text(`Message:`, 20, 105);
    doc.text(booking.message || "N/A", 20, 115, { maxWidth: 170 });
    doc.save(`Booking_${booking.id}_Receipt.pdf`);
  };

  // ===============================
  // UI SECTION
  // ===============================

  if (loading) return <div className="container">Loading booking details...</div>;
  if (error) return <div className="container error">{error}</div>;
  if (!booking) return <div className="container">Booking not found.</div>;

  return (
    <div className="page-container">
      <div className="form-container">
        <p><strong>Client Name:</strong> {booking.name}</p>
        <p><strong>Phone:</strong> {booking.phone}</p>
        <p><strong>Email:</strong> {booking.email}</p>
        <p><strong>Event Type:</strong> {booking.event_type}</p>
        <p>
          <strong>Event Date:</strong>{" "}
          {new Date(booking.event_date).toLocaleDateString()}
        </p>
        <p><strong>Message:</strong> {booking.message || "No message provided"}</p>
        <button className="btn-primary" onClick={generatePDF}>
          Download Receipt (PDF)
        </button>
      </div>
    </div>
  );
}