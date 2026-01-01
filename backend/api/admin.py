from django.contrib import admin
from .models import Booking, Expense

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'event_type', 'from_date', 'to_date', 'status', 'phone', 'created_at']
    list_filter = ['status', 'event_type', 'from_date']
    search_fields = ['name', 'phone', 'email']
    ordering = ['-created_at']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['function_date', 'advance', 'balance', 'total']
    ordering = ['-function_date']