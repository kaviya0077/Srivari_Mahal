from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'event_type',
        'from_date',
        'to_date',
        # 'total_amount',
        # 'advance_amount',
        # 'paid_amount',
        # 'balance',
        'status',
        'payment_status',
    )

    list_filter = (
        'status',
        'event_type',
    )

    search_fields = (
        'name',
        'email',
        'phone',
    )
