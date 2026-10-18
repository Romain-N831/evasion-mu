from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending review"
        APPROVED = "APPROVED", "Approved"
        HIDDEN = "HIDDEN", "Hidden"

    customer = models.ForeignKey("users.Customer", on_delete=models.CASCADE, related_name="reviews")
    hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    activity = models.ForeignKey("activities.Activity", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    moderation_status = models.CharField(max_length=10, choices=ModerationStatus.choices,
                                          default=ModerationStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5),
                                   name="review_rating_between_1_and_5"),
        ]

    def __str__(self):
        return f"{self.rating}/5 — {self.activity.title}"
