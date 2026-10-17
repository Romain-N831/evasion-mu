from django.db import models


class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    min_participants = models.PositiveSmallIntegerField(default=1)
    max_participants = models.PositiveSmallIntegerField(null=True, blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        constraints = [
            models.CheckConstraint(condition=models.Q(current_price__gte=0), name="activity_price_non_negative"),
            models.CheckConstraint(condition=models.Q(min_participants__gte=1), name="activity_min_participants_positive"),
            models.CheckConstraint(condition=models.Q(max_participants__isnull=True) |
                models.Q(max_participants__gte=models.F("min_participants")), name="activity_max_participants_valid"),
        ]

    def __str__(self):
        return self.title


class ActivitySlot(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="slots")
    starts_at = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["starts_at"]
        constraints = [
            models.UniqueConstraint(fields=["activity", "starts_at"], name="unique_activity_slot_start"),
            models.CheckConstraint(condition=models.Q(capacity__gte=1), name="activity_slot_capacity_positive"),
        ]

    def __str__(self):
        return f"{self.activity.title} — {self.starts_at:%Y-%m-%d %H:%M}"


class ActivityBlockedDate(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="blocked_dates",
                                 null=True, blank=True,
                                 help_text="Leave blank to block that date for all activities.")
    date = models.DateField()
    reason = models.CharField(max_length=255)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.activity or 'All activities'} — {self.date}: {self.reason}"


# Create your models here.
