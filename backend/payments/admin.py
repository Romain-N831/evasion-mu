from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Allow staff to inspect simulated payment records without editing receipts."""
    list_display = (
        "id", "booking", "amount_paid", "payment_method", "status",
        "transaction_type", "payment_date",
    )
    list_filter = ("status", "payment_method", "transaction_type", "payment_date")
    search_fields = ("transaction_reference", "booking__customer__user__username")
    readonly_fields = ("payment_date", "transaction_reference")
