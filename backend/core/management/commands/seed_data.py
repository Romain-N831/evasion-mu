from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hotels.models import Hotel, RoomType, RoomAvailability
from activities.models import Activity, ActivitySlot


class Command(BaseCommand):
    help = "Populate Evasion.mu with sample hotels, rooms, activities and availability."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()

        hotels_data = [
            {
                "name": "Lagoon View Resort",
                "description": "A relaxing beachfront resort with lagoon views and tropical gardens.",
                "address": "Wolmar Coastal Road",
                "city": "Flic en Flac",
                "region": "West",
                "star_rating": 4,
            },
            {
                "name": "Belle Mare Beach Hotel",
                "description": "A coastal hotel offering access to the sandy beaches of the east.",
                "address": "Coastal Road",
                "city": "Belle Mare",
                "region": "East",
                "star_rating": 4,
            },
            {
                "name": "Le Morne Mountain Retreat",
                "description": "A peaceful retreat near Le Morne Brabant and the southwest lagoon.",
                "address": "Le Morne Peninsula",
                "city": "Le Morne",
                "region": "Southwest",
                "star_rating": 5,
            },
            {
                "name": "Grand Baie Harbour Hotel",
                "description": "A convenient base for beaches, restaurants and northern island excursions.",
                "address": "Royal Road",
                "city": "Grand Baie",
                "region": "North",
                "star_rating": 3,
            },
            {
                "name": "Chamarel Nature Lodge",
                "description": "A nature-focused lodge near the forests and scenic landscapes of Chamarel.",
                "address": "Chamarel Village",
                "city": "Chamarel",
                "region": "Southwest",
                "star_rating": 3,
            },
        ]

        rooms_data = [
            {
                "name": "Standard Room",
                "description": "Comfortable room for a short island stay.",
                "max_occupancy": 2,
                "price_per_night": Decimal("2800.00"),
                "total_rooms": 10,
            },
            {
                "name": "Deluxe Room",
                "description": "Spacious room with additional comfort.",
                "max_occupancy": 3,
                "price_per_night": Decimal("4500.00"),
                "total_rooms": 6,
            },
            {
                "name": "Family Suite",
                "description": "Larger accommodation suitable for families.",
                "max_occupancy": 4,
                "price_per_night": Decimal("6800.00"),
                "total_rooms": 3,
            },
        ]

        activities_data = [
            {
                "title": "Ile aux Cerfs Boat Trip",
                "description": "Enjoy a boat excursion to Ile aux Cerfs and its beautiful beaches.",
                "location": "Trou d'Eau Douce",
                "category": "Boat Trip",
                "current_price": Decimal("1800.00"),
                "duration_minutes": 360,
                "max_participants": 20,
            },
            {
                "title": "Dolphin Watching Excursion",
                "description": "Join an early-morning boat trip to observe dolphins responsibly.",
                "location": "Tamarin Bay",
                "category": "Wildlife",
                "current_price": Decimal("2200.00"),
                "duration_minutes": 180,
                "max_participants": 12,
            },
            {
                "title": "Le Morne Guided Hike",
                "description": "Discover the landscape and history of Le Morne with a guide.",
                "location": "Le Morne Brabant",
                "category": "Hiking",
                "current_price": Decimal("1500.00"),
                "duration_minutes": 240,
                "max_participants": 10,
            },
            {
                "title": "Blue Bay Snorkelling",
                "description": "Explore the marine life of the Blue Bay Marine Park.",
                "location": "Blue Bay",
                "category": "Water Sports",
                "current_price": Decimal("1200.00"),
                "duration_minutes": 120,
                "max_participants": 10,
            },
            {
                "title": "Chamarel Seven Coloured Earth",
                "description": "Visit the famous coloured earth landscape and nearby viewpoints.",
                "location": "Chamarel",
                "category": "Sightseeing",
                "current_price": Decimal("900.00"),
                "duration_minutes": 120,
                "max_participants": 15,
            },
            {
                "title": "Port Louis Cultural Tour",
                "description": "Discover local history, markets and cultural landmarks in the capital.",
                "location": "Port Louis",
                "category": "Cultural Tour",
                "current_price": Decimal("1000.00"),
                "duration_minutes": 180,
                "max_participants": 12,
            },
            {
                "title": "Casela Nature Adventure",
                "description": "Spend time exploring outdoor attractions at Casela Nature Parks.",
                "location": "Cascavelle",
                "category": "Nature",
                "current_price": Decimal("1600.00"),
                "duration_minutes": 240,
                "max_participants": 15,
            },
            {
                "title": "Northern Islands Cruise",
                "description": "Take a boat excursion around the northern islands of Mauritius.",
                "location": "Grand Baie",
                "category": "Boat Trip",
                "current_price": Decimal("2500.00"),
                "duration_minutes": 360,
                "max_participants": 18,
            },
        ]

        hotels_created = 0
        rooms_created = 0
        availability_created = 0
        activities_created = 0
        slots_created = 0

        for hotel_data in hotels_data:
            hotel, created = Hotel.objects.update_or_create(
                name=hotel_data["name"],
                defaults=hotel_data,
            )
            hotels_created += int(created)

            for room_data in rooms_data:
                room, created = RoomType.objects.update_or_create(
                    hotel=hotel,
                    name=room_data["name"],
                    defaults=room_data,
                )
                rooms_created += int(created)

                for day_offset in range(30):
                    availability_date = today + timedelta(days=day_offset)

                    _, created = RoomAvailability.objects.get_or_create(
                        room_type=room,
                        date=availability_date,
                        defaults={"available_rooms": room.total_rooms},
                    )
                    availability_created += int(created)

        for activity_data in activities_data:
            activity, created = Activity.objects.update_or_create(
                title=activity_data["title"],
                defaults=activity_data,
            )
            activities_created += int(created)

            for day_offset in range(1, 8):
                slot_date = today + timedelta(days=day_offset)
                starts_at = timezone.make_aware(
                    timezone.datetime(
                        slot_date.year,
                        slot_date.month,
                        slot_date.day,
                        9,
                        0,
                    )
                )

                _, created = ActivitySlot.objects.get_or_create(
                    activity=activity,
                    starts_at=starts_at,
                    defaults={
                        "capacity": activity.max_participants or 10,
                        "is_active": True,
                    },
                )
                slots_created += int(created)

        self.stdout.write(self.style.SUCCESS("Evasion.mu sample data setup complete."))
        self.stdout.write(f"New hotels: {hotels_created}")
        self.stdout.write(f"New room types: {rooms_created}")
        self.stdout.write(f"New room availability records: {availability_created}")
        self.stdout.write(f"New activities: {activities_created}")
        self.stdout.write(f"New activity slots: {slots_created}")