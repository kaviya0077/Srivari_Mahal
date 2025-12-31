// src/pages/DashboardPage.js
import React, { useEffect, useState } from "react";
import API from "../api";

// 📊 Recharts
import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line
} from "recharts";

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  // Load dashboard stats
  useEffect(() => {
    API.get("dashboard-stats/")
      .then((res) => setStats(res.data))
      .catch((err) => {
        console.error("Dashboard Error:", err);
        setError("Failed to load dashboard statistics.");
      });
  }, []);

  if (error) return <div className="page-container error">{error}</div>;
  if (!stats) return <div className="page-container">Loading dashboard...</div>;

  // 🎨 Pie Chart Colors
  const COLORS = ["#4b6cb7", "#36d1dc", "#ff7b7b", "#82ca9d", "#8884d8"];

  // 📅 Format months for chart display
  const monthNames = [
    "",
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
  ];

  const monthlyData = stats.bookings_per_month.map((m) => ({
    month: monthNames[m.month],
    count: m.count,
  }));

  const eventTypeData = stats.event_type_distribution.map((e) => ({
    name: e.event_type,
    value: e.count,
  }));

  return (
      <div className="page-container">
        <h2 className="page-title">Admin Dashboard</h2>

        {/* ======================= */}
        {/* 🔥 STAT CARDS */}
        {/* ======================= */}
        <div className="dashboard-cards">
          <div className="dashboard-card">
            <h3>Total Bookings</h3>
            <p>{stats.total_bookings}</p>
          </div>

          <div className="dashboard-card">
            <h3>Unread Inquiries</h3>
            <p>{stats.unread_inquiries}</p>
          </div>

          <div className="dashboard-card">
            <h3>Upcoming Events</h3>
            <p>{stats.upcoming_events}</p>
          </div>
        </div>

        {/* ======================= */}
        {/* 📊 BOOKINGS PER MONTH CHART */}
        {/* ======================= */}
        <div className="chart-container">
          <h3>Bookings Per Month</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#4b6cb7" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* ======================= */}
        {/* 🎉 EVENT TYPE PIE CHART */}
        {/* ======================= */}
        <div className="chart-container">
          <h3>Event Type Distribution</h3>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={eventTypeData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={110}
                label
              >
                {eventTypeData.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend layout="horizontal" verticalAlign="bottom" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
  );
}