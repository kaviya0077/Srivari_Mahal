import React, { useEffect, useState } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import API from "../api";
import "react-big-calendar/lib/css/react-big-calendar.css"; 
import "../App.css";

const localizer = momentLocalizer(moment);

export default function AvailabilityPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Load Booking Dates
  useEffect(() => {
    let mounted = true;
    const fetchDates = async () => {
      try {
        console.log("📅 Fetching calendar data...");
        const res = await API.get("/bookings/dates/");
        console.log("✅ Calendar data received:", res.data);

        if (mounted) {
          const formatted = res.data.map((ev) => ({
            title: ev.title || "Booked",
            start: new Date(ev.start),
            end: new Date(ev.end),
            status: "booked",
          }));

          setEvents(formatted);
        }
      } catch (err) {
        console.error("❌ Error loading calendar:", err);
        console.error("❌ Error details:", err.response?.data);
        if (mounted) setError("Failed to load calendar data.");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchDates();
    return () => (mounted = false);
  }, []);

  // Style booked vs available
  const eventStyleGetter = (event) => {
    let backgroundColor = "#4b6cb7";

    if (event.status === "booked") backgroundColor = "#ff5252";

    return {
      style: {
        backgroundColor,
        color: "white",
        borderRadius: "8px",
        border: "none",
        padding: "4px",
      },
    };
  };

  // Weekend highlight
  const dayPropGetter = (date) => {
    const weekend = date.getDay() === 0 || date.getDay() === 6;
    return {
      style: {
        backgroundColor: weekend ? "#f9f9f9" : "white",
      },
    };
  };

  return (
    // <div className="home-container"> 
      <div className="availability-page">
        <h2 className="page-title">Availability Calendar</h2>

        {/* legend */}
        <div className="legend">
          <span className="legend-item">
            <span className="legend-color booked"></span> Booked
          </span>
          <span className="legend-item">
            <span className="legend-color available"></span> Available
          </span>
        </div>

        {loading ? (
          <div className="loading-message">Loading calendar…</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <div className="calendar-wrapper">
            <Calendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              views={["month", "week", "day"]}
              popup={true}
              eventPropGetter={eventStyleGetter}
              dayPropGetter={dayPropGetter}
            />
          </div>
        )}
      </div>
  );
}