from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    class Method(models.TextChoices):
        CREDIT_CARD = "CREDIT_CARD", "Credit card"
        DEBIT_CARD = "DEBIT_CARD", "Debit card"
        ONLINE_TRANSFER = "ONLINE_TRANSFER", "Online transfer"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESSFUL = "SUCCESSFUL", "Successful"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"
        PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", "Partially refunded"

    class TransactionType(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        REFUND = "REFUND", "Refund"

    booking = models.ForeignKey("bookings.Booking", on_delete=models.PROTECT, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[MinValueValidator(0)])
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices, default=TransactionType.PAYMENT)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True, unique=True)

    class Meta:
        ordering = ["-payment_date"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount_paid__gte=0), name="payment_amount_non_negative"),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} — {self.amount_paid} ({self.status})"
