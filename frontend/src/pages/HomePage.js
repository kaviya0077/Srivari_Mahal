import React from "react";
import { Link } from "react-router-dom";
import "../App.css";
import EventsHosted from "../components/EventsHosted";

const HomePage = () => (
  <div className="home-container">
    <div className="home-panel">
      <div className="home-content">
        <h1>
          Welcome to <span className="highlight">Sri Vari Mahal</span>
        </h1>
        <p>Your perfect destination for weddings, events, and celebrations.</p>

        {/* 📞 CONTACT + MAP (inside home-content) */}
        <div className="contact-block">
          <div className="contact-info">
            <h2>Contact Us</h2>
            <p><strong>Address:</strong><br/>
              Sri Vari Mahal A/C - Grand Marriage & Party Hall,<br/>
              Kannadasan Street, Abirami Nagar,<br/>
              Baluchetty Chatram, Sirunaiperugal,<br/>
              Kanchipuram, Tamil Nadu - 631551
            </p>
            <p><strong>Phone:</strong>{" "}<a href="tel:+919843186231">9843186231, 8870201981 </a></p>
            <p><strong>Email:</strong>{" "}<a href="mailto:srivarimahal@gmail.com">srivarimahal2025kpm@gmail.com</a></p>
          </div>
          <div className="map-container">
            <iframe
              title="Sri Vari Mahal Map"
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3889.4860131193636!2d79.62694979999999!3d12.876439700000002!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3a52c75a0fa10a6b%3A0xf68b5f23b7e317ee!2sSri%20Vari%20Mahal%20A%2FC!5e0!3m2!1sen!2sin!4v1766851502696!5m2!1sen!2sin"
              style={{ border: 0 }}
              allowfullscreen
              loading="lazy" 
              referrerpolicy="no-referrer-when-downgrade"></iframe>
          </div>
        </div>
      </div>

      {/* 🎉 Events section stays as-is */}
      <EventsHosted />

    </div>
  </div>
);

export default HomePage;