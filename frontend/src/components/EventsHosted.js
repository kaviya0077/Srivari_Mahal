import React from "react";
import "../App.css";
import { Link } from "react-router-dom";

const events = [
  { title: "Wedding", image: require("../assets/wedding.png") },
  { title: "Engagement", image: require("../assets/engagement.png") },
  { title: "Reception", image: require("../assets/reception.png") },
  { title: "Birthday Party", image: require("../assets/birthday.png") },
  { title: "Corporate Event", image: require("../assets/corporate.png") },
  { title: "Other Events", image: require("../assets/other.png") },
];

export default function EventsHosted() {
  return (
    <section className="events-section">
      <h2 className="events-title">Events We Host</h2>
      <div className="events-grid">
        {events.map((ev, idx) => (
          <Link
            to="/pricing"
            key={idx}
            style={{ textDecoration: "none" }}
          >
            <div className="event-card">
              <div className="event-image">
                <img src={ev.image} alt={ev.title} />
              </div>
              <h3>{ev.title}</h3>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}