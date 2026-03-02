# backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookingViewSet,
    booking_receipt,  # ✅ Make sure imported
    booking_dates,
    dashboard_stats,
    export_bookings_csv,
    update_booking_status,
    update_payment,
    create_payment_intent,
    expenses_list,
    expense_detail,
    export_expenses,
)

# Router for ViewSet
router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # ⚠️ CRITICAL: ALL specific booking routes MUST come BEFORE router
    
    # 📌 Receipt - MUST be first
    path("bookings/<int:pk>/receipt/", booking_receipt, name="booking-receipt"),
    
    # 📌 Booking dates calendar
    path("bookings/dates/", booking_dates, name="booking-dates"),
    
    # 📌 Export CSV
    path("bookings/export/", export_bookings_csv, name="export-bookings-csv"),
    
    # 📌 Update status
    path("bookings/<int:pk>/status/", update_booking_status, name="booking-status"),
    
    # 📌 Update payment
    path("bookings/<int:pk>/payment/", update_payment, name="update-payment"),
    
    # ✅ NOW include router (creates /bookings/ list and /bookings/<id>/ detail)
    path('', include(router.urls)),
    
    # 📌 Dashboard
    path("dashboard-stats/", dashboard_stats, name="dashboard-stats"),
    
    # 📌 Payment
    path("create-payment-intent/", create_payment_intent, name="create-payment-intent"),
    
    # 📌 Expenses
    path("expenses/", expenses_list, name="expenses-list"),
    path("expenses/<int:pk>/", expense_detail, name="expense-detail"),
    path("expenses/export/", export_expenses, name="export-expenses"),
]