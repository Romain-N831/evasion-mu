# Generated manually because the repository's checked-in virtual environment
# references a Python interpreter that is no longer installed on this machine.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hotelreservation",
            name="guests_count",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="hotelreservation",
            name="inventory_released",
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name="hotelreservation",
            constraint=models.CheckConstraint(
                condition=models.Q(("guests_count__gte", 1)),
                name="hotel_reservation_guests_positive",
            ),
        ),
    ]
