import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

// 🌐 Public Pages
import HomePage from "./pages/HomePage";
import BookingFormPage from "./pages/BookingFormPage";
import GalleryPage from "./pages/GalleryPage";
import PricingPage from "./pages/PricingPage";
import FacilitiesPage from "./pages/FacilitiesPage";
import BookingDetailPage from "./pages/BookingDetailPage";
import BookingSuccess from "./pages/BookingSuccess";
import LoginPage from "./pages/LoginPage";

// 🔐 Admin Pages
import DashboardPage from "./pages/DashboardPage";
import EditBookingPage from './pages/EditBookingPage';
import BookingsPage from "./pages/BookingsPage";
import AvailabilityPage from "./pages/AvailabilityPage";
import ExpensesPage from "./pages/ExpensesPage";

// 🛡️ Protected Route
import ProtectedRoute from "./components/ProtectedRoute";

// Private Route
import PrivateRoute from "./components/PrivateRoute";

import "./App.css";

function App() {
  return (
    <Router>
      <Navbar />

      <Routes>
        {/* 🌐 Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/gallery" element={<GalleryPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/facilities" element={<FacilitiesPage />} />
        <Route path="/book-now" element={<BookingFormPage />} />
        <Route path="/bookings/edit/:id" element={<PrivateRoute><EditBookingPage /></PrivateRoute>} />
        <Route path="/booking-success" element={<BookingSuccess />} />
        <Route path="/bookings/:id" element={<BookingDetailPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* 🔐 Admin Routes (Protected) */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/bookings"
          element={
            <ProtectedRoute>
              <BookingsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/availability"
          element={
            <ProtectedRoute>
              <AvailabilityPage />
            </ProtectedRoute>
          }
        />

        <Route 
          path="/expenses" 
          element={
            <ProtectedRoute>
              <ExpensesPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;