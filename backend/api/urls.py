# backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookingViewSet,  # ✅ Added ViewSet import
    booking_detail,
    booking_receipt,
    booking_dates,
    dashboard_stats,
    export_bookings_csv,
    update_booking_status,
    expenses_list,
    expense_detail,
    export_expenses,
    # update_payment,  # ✅ Added for payment updates
    # create_payment_intent,  # ✅ Added for Stripe
)

# ✅ Create router for ViewSet
router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
# 📌 Availability Calendar - MUST come before router
    path("bookings/dates/", booking_dates, name="booking-dates"),
    
    # 📌 Export CSV - MUST come before router
    path("bookings/export/", export_bookings_csv, name="export-bookings-csv"),
    
    # 📌 Booking receipt
    path("bookings/<int:pk>/receipt/", booking_receipt, name="booking-receipt"),
    
    # 📌 Approve / Reject booking
    path("bookings/<int:pk>/status/", update_booking_status, name="booking-status"),
    
    # 📌 Payment update
    # path("bookings/<int:pk>/payment/", update_payment, name="update-payment"),
    
    # 📌 Get single booking
    path("bookings/<int:pk>/", booking_detail, name="booking-detail"),
    
    # ✅ NOW include router (this creates /bookings/ for list/create)
    path('', include(router.urls)),
    
    # 📌 Dashboard
    path("dashboard-stats/", dashboard_stats, name="dashboard-stats"),
    
    # 📌 Stripe payment intent
    # path("create-payment-intent/", create_payment_intent, name="create-payment-intent"),
    
    # 📌 Expenses
    path("expenses/", expenses_list),
    path("expenses/<int:pk>/", expense_detail),
    path("expenses/export/", export_expenses),
]