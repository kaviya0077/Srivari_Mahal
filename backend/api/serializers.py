# backend/api/serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Booking, Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ['id', 'created_at']

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
        print("🔍 Running serializer validation...")
        print(f"Data received: {data}")
        
        # Get the instance if this is an update
        instance = self.instance
        
        # Merge with existing data if updating
        if instance:
            merged_data = {**instance.__dict__, **data}
        else:
            merged_data = data
        
        # Check date logic
        from_date = merged_data.get('from_date')
        to_date = merged_data.get('to_date')

        from_date = merged_data.get('from_date')
        to_date = merged_data.get('to_date')
        
        if from_date and to_date:
            if to_date < from_date:
                raise serializers.ValidationError({
                    'to_date': 'End date must be after or equal to start date.'
                })
        
        # Create temporary instance for model validation
        temp_instance = instance if instance else Booking()
        for key, value in data.items():
            setattr(temp_instance, key, value)
        
        # Run model's clean() method
        try:
            temp_instance.clean()
        except DjangoValidationError as e:
            print(f"❌ Model validation failed: {e.message_dict}")
            raise serializers.ValidationError(e.message_dict)
        
        print("✅ Validation passed")
        return data
    
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