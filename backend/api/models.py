# backend/api/models.py
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=25)
    email = models.EmailField()
    event_type = models.CharField(max_length=100)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    address_line = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # paid = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    # total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_guests = models.IntegerField(null=True, blank=True, default=0)
    food_preference = models.CharField(max_length=50, blank=True, null=True)
    alternate_phone = models.CharField(max_length=25, blank=True, null=True)

    @property
    def payment_status(self):
        if self.balance == 0:
            return "Paid"
        if self.paid_amount > 0:
            return "Advance Paid"
        return "Pending"
    
    def __str__(self):
        return f"{self.name} - {self.event_type} from {self.from_date} to {self.to_date}"
    
    def clean(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValidationError("End date cannot be earlier than start date.")
        
        start = self.from_date
        end = self.to_date or self.from_date

        conflicting = Booking.objects.filter(
            Q(from_date__lte=end) & Q(to_date__gte=start)
        )

        # exclude self when editing
        if self.pk:
            conflicting = conflicting.exclude(pk=self.pk)

        if conflicting.exists():
            raise ValidationError("Hall is already booked for selected dates.")
        
        if self.from_date == self.to_date:
            conflicting_time = Booking.objects.filter(
                from_date=self.from_date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )

            if self.pk:
                conflicting_time = conflicting_time.exclude(pk=self.pk)

            if conflicting_time.exists():
                raise ValidationError("Time slot is already booked.")

class Expense(models.Model):
    function_date = models.DateField()

    # money fields
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_recovery = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # expense breakdown
    gens = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ladies = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    flag = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waste_room_cleaning = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electrician = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    radio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    light = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Expense — {self.function_date}"
