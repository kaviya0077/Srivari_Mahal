# backend/api/urls.py
from django.urls import path
from .views import (
    bookings_list,
    booking_detail,
    booking_receipt,
    booking_dates,
    dashboard_stats,
    export_bookings_csv,
    update_booking_status,
    expenses_list,
    expense_detail,
    export_expenses
)

urlpatterns = [
    # 📌 List all + Create booking
    path("bookings/", bookings_list, name="bookings-list"),

    # 📌 Get single booking
    path("bookings/<int:pk>/", booking_detail, name="booking-detail"),

    path("bookings/<int:pk>/receipt/", booking_receipt, name="booking-receipt"),
    path("expenses/", expenses_list),
    path("expenses/<int:pk>/", expense_detail),
    path("expenses/export/", export_expenses),

    # 📌 Approve / Reject booking
    path("bookings/<int:pk>/status/", update_booking_status, name="booking-status"),

    # 📌 Availability Calendar
    path("bookings/dates/", booking_dates, name="booking-dates"),

    # 📌 Export CSV
    path("bookings/export/", export_bookings_csv, name="export-bookings-csv"),

    # 📌 Dashboard
    path("dashboard-stats/", dashboard_stats, name="dashboard-stats"),
]