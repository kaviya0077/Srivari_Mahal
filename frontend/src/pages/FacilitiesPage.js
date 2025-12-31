import React from "react";
import "../App.css";

const FacilitiesPage = () => (
  <div className="home-container">
    <div className="gallery-container">
      <h2 className="facility-title">Facilities Available</h2>
      <div className="facilities-grid">

        <div className="facility-card">
          <h3>Spacious AC Halls</h3>
          <p>
            Fully air-conditioned marriage & party halls with elegant interiors
            and comfortable seating for large gatherings.
          </p>
        </div>

        <div className="facility-card">
          <h3>Decor & Lighting</h3>
          <p>
            Premium stage decoration, mood lighting, floral arrangements and
            custom theme options available.
          </p>
        </div>

        <div className="facility-card">
          <h3>Catering Services</h3>
          <p>
            Veg & Non-Veg catering with multiple menu choices, hygienic kitchen,
            and professional serving staff.
          </p>
        </div>

        <div className="facility-card">
          <h3>Parking Area</h3>
          <p>
            Large parking space with security assistance to ensure convenience
            for your guests.
          </p>
        </div>

        <div className="facility-card">
          <h3>Generator Backup</h3>
          <p>
            Full power backup to ensure uninterrupted events without any
            disturbance.
          </p>
        </div>

        <div className="facility-card">
          <h3>Rooms & Changing Area (AC)</h3>
          <p>
            12 guest rooms, plus separate dedicated bride and groom suites 
            featuring mirrors, comfortable seating, and private washrooms.
          </p>
        </div>

        <div className="facility-card">
          <h3>Temple</h3>
          <p>
            A peaceful Vinayagar shrine inside the premises 
            — perfect for Pooja, Muhurtham rituals and blessings before the ceremony.
          </p>
        </div>

        <div className="facility-card">
          <h3>24x7 CCTV Surveillance</h3>
          <p>
            Monitored with high-definition CCTV coverage, ensuring guest safety, 
            quick incident tracking, and complete peace of mind.
          </p>
        </div>

      </div>
    </div>
  </div>
);
export default FacilitiesPage;