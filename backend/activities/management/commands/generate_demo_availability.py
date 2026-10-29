from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from activities.models import Activity, ActivitySlot
from hotels.models import RoomType, RoomAvailability


class Command(BaseCommand):
    help = "Generate missing demo activity slots and hotel room availability."

    def add_arguments(self, parser):
        parser.add_argument("--activity-days", type=int, default=30)
        parser.add_argument("--room-days", type=int, default=90)
        parser.add_argument(
            "--times",
            default="09:00,13:00,16:00",
            help="Comma-separated 24-hour times, e.g. 09:00,13:00",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        activity_days = options["activity_days"]
        room_days = options["room_days"]

        if activity_days < 1 or room_days < 1:
            self.stderr.write("Day ranges must be at least 1.")
            return

        try:
            slot_times = [
                time.fromisoformat(value.strip())
                for value in options["times"].split(",")
            ]
        except ValueError:
            self.stderr.write(
                "Invalid time format. Example: --times 09:00,13:00"
            )
            return

        if not slot_times:
            self.stderr.write("Provide at least one slot time.")
            return

        today = timezone.localdate()
        now = timezone.now()

        created_slots = 0
        created_availability = 0

        activities = Activity.objects.filter(is_active=True)
        room_types = RoomType.objects.filter(
            is_active=True,
            hotel__is_active=True,
        )

        for activity in activities:
            # Use the activity's configured maximum where available.
            capacity = activity.max_participants or 10
            capacity = max(capacity, activity.min_participants)

            for day_offset in range(activity_days):
                slot_date = today + timedelta(days=day_offset)

                for slot_time in slot_times:
                    starts_at = timezone.make_aware(
                        datetime.combine(slot_date, slot_time),
                        timezone.get_current_timezone(),
                    )

                    # Never create a slot that is already in the past.
                    if starts_at <= now:
                        continue

                    _, created = ActivitySlot.objects.get_or_create(
                        activity=activity,
                        starts_at=starts_at,
                        defaults={
                            "capacity": capacity,
                            "is_active": True,
                        },
                    )

                    if created:
                        created_slots += 1

        for room_type in room_types:
            for day_offset in range(room_days):
                availability_date = today + timedelta(days=day_offset)

                _, created = RoomAvailability.objects.get_or_create(
                    room_type=room_type,
                    date=availability_date,
                    defaults={
                        "available_rooms": room_type.total_rooms,
                    },
                )

                if created:
                    created_availability += 1

        self.stdout.write(self.style.SUCCESS(
            "Demo availability generation complete.\n"
            f"Active activities checked: {activities.count()}\n"
            f"Active room types checked: {room_types.count()}\n"
            f"New activity slots: {created_slots}\n"
            f"New room availability records: {created_availability}\n"
            f"Activity horizon: {activity_days} days\n"
            f"Room horizon: {room_days} days\n"
            f"Starting date: {today}"
        ))