import React from "react";
import "../App.css";

const PricingPage = () => (
  <div className="home-container">
    <div className="gallery-container">
      <h2 className="price-title">Pricing & Packages</h2>
      <div className="pricing-grid">

        {/* Marriage Hall */}
        <div className="pricing-card">
          <div className="pricing-card-header">
            <h3>Marriage Hall (24 hrs)</h3>
          </div>
          <div className="pricing-card-body">
            <p className="price">₹ 1,25,000</p>
            <ul>
              <li>Full-Day Booking</li>
              <li>Stage & Seating</li>
              <li>Basic Decoration</li>
              <li>Lighting Setup</li>
              <li>Catering (Veg and Non Veg)</li>
              <li>DJ</li>
            </ul>
          </div>
        </div>

        {/* Marriage Hall */}
        <div className="pricing-card">
          <div className="pricing-card-header">
            <h3>Marriage Hall (12 hrs)</h3>
          </div>
          <div className="pricing-card-body">
            <p className="price">₹ 60,000</p>
            <ul>
              <li>Half-Day Booking</li>
              <li>Stage & Seating</li>
              <li>Basic Decoration</li>
              <li>Lighting Setup</li>
              <li>Catering (Veg and Non Veg)</li>
              <li>DJ</li>
            </ul>
          </div>
        </div>

        {/* Party Hall */}
        <div className="pricing-card">
          <div className="pricing-card-header">
            <h3>Party Hall (12 hrs)</h3>
          </div>
          <div className="pricing-card-body">
            <p className="price">₹ 30,000</p>
            <ul>
              <li>Half-Day Booking</li>
              <li>Stage & Seating</li>
              <li>Basic Decoration</li>
              <li>Lighting Setup</li>
              <li>Catering (Veg and Non Veg)</li>
              <li>DJ</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
);
export default PricingPage;