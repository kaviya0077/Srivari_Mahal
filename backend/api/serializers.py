# backend/api/serializers.py
from rest_framework import serializers
from .models import Booking
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    # ============================
    #  🔍 VALIDATION RULES
    # ============================
    def validate(self, data):
        """
        - Ensure advance payment must be paid before approval.
        - paid_amount must be >= advance_amount.
        - balance = total_amount - paid_amount.
        """
        # total = data.get("total_amount", self.instance.total_amount if self.instance else 0)
        # advance = data.get("advance_amount", self.instance.advance_amount if self.instance else 0)
        # paid = data.get("paid_amount", self.instance.paid_amount if self.instance else 0)
        # status_value = data.get("status", self.instance.status if self.instance else "pending")
        instance = Booking(**data)
        instance.clean()

        # ⚠️ Rule 1 — paid_amount cannot exceed total
        # if paid > total:
        #     raise serializers.ValidationError({
        #         "paid_amount": "Paid amount cannot be greater than total amount."
        #     })

        # ⚠️ Rule 2 — must pay at least advance amount before confirmation
        # if status_value == "approved" and paid < advance:
        #     raise serializers.ValidationError({
        #         "paid_amount": "Advance amount must be fully paid before booking approval."
        #     })
        return data

    # ============================
    #  💾 Update balance automatically
    # ============================
    # def update(self, instance, validated_data):
    #     instance = super().update(instance, validated_data)
    #     # Auto-calc balance
    #     instance.balance = instance.total_amount - instance.paid_amount
    #     instance.save()
    #     return instance
    
    # def create(self, validated_data):
    #     booking = super().create(validated_data)
    #     booking.balance = booking.total_amount - booking.paid_amount
    #     booking.save()
    #     return booking