// src/components/Navbar.js
import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import "../App.css";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const isAdmin = !!localStorage.getItem("access_token");
  const showAdminLogin = process.env.REACT_APP_SHOW_ADMIN === "true";

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="nav-logo">Sri Vari Mahal A/C</div>

      <ul className="nav-links">
        {!isAdmin ? (
          <>
            <li>
              <Link
                to="/"
                className={location.pathname === "/" ? "active" : ""}
              >
                Home
              </Link>
            </li>

            <li>
              <Link
                to="/gallery"
                className={location.pathname === "/gallery" ? "active" : ""}
              >
                Gallery
              </Link>
            </li>

            <li>
              <Link
                to="/pricing"
                className={location.pathname === "/pricing" ? "active" : ""}
              >
                Pricing
              </Link>
            </li>

            <li>
              <Link
                to="/facilities"
                className={location.pathname === "/facilities" ? "active" : ""}
              >
                Facilities
              </Link>
            </li>

            <li>
              <Link
                to="/book-now"
                className={location.pathname === "/book-now" ? "active" : ""}
              >
                Book Now
              </Link>
            </li>

            {/* 👇 Admin Login only if FEATURE FLAG is true */}
            {showAdminLogin && !isAdmin &&(
              <li>
                <Link
                  to="/login"
                  className={location.pathname === "/login" ? "active" : ""}
                >
                  Admin Login
                </Link>
              </li>
            )}
          </>
        ) : (
          <>
            <li>
              <Link
                to="/dashboard"
                className={location.pathname === "/dashboard" ? "active" : ""}
              >
                Dashboard
              </Link>
            </li>

            <li>
              <Link
                to="/bookings"
                className={location.pathname === "/bookings" ? "active" : ""}
              >
                Bookings
              </Link>
            </li>

            <li>
              <Link
                to="/availability"
                className={
                  location.pathname === "/availability" ? "active" : ""
                }
              >
                Availability
              </Link>
            </li>

            <li>
              <Link
                to="/expenses"
                className={
                  location.pathname === "/expenses" ? "active" : ""
                }
              >
                Expenses
              </Link>
            </li>

            <li>
              <button className="btn-logout" onClick={handleLogout}>
                Logout
              </button>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}