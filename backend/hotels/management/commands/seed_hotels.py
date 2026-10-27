
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hotels.models import Hotel, RoomType, RoomAvailability


class Command(BaseCommand):
    help = "Seed additional sample hotels, room types and availability."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()

        hotels_data = [
            {
                "name": "Tamarin Sunset Hotel",
                "description": (
                    "A relaxing west-coast hotel with sunset views, "
                    "comfortable rooms and easy access to Tamarin Bay."
                ),
                "address": "Coastal Road",
                "city": "Tamarin",
                "region": "West",
                "star_rating": 4,
            },
            {
                "name": "Port Louis City Hotel",
                "description": (
                    "A convenient city hotel close to local markets, "
                    "restaurants and cultural attractions."
                ),
                "address": "Jules Koenig Street",
                "city": "Port Louis",
                "region": "Northwest",
                "star_rating": 3,
            },
            {
                "name": "Blue Bay Coral Resort",
                "description": (
                    "A seaside resort offering easy access to Blue Bay "
                    "and its famous marine park."
                ),
                "address": "Blue Bay Coastal Road",
                "city": "Blue Bay",
                "region": "Southeast",
                "star_rating": 4,
            },
            {
                "name": "Trou aux Biches Garden Hotel",
                "description": (
                    "A tropical hotel with landscaped gardens, "
                    "spacious rooms and nearby sandy beaches."
                ),
                "address": "Trou aux Biches Road",
                "city": "Trou aux Biches",
                "region": "North",
                "star_rating": 4,
            },
            {
                "name": "Mahebourg Heritage Inn",
                "description": (
                    "A welcoming guesthouse inspired by local heritage, "
                    "near the waterfront and historic town centre."
                ),
                "address": "Royal Road",
                "city": "Mahebourg",
                "region": "Southeast",
                "star_rating": 3,
            },
        ]

        rooms_data = [
            {
                "name": "Standard Room",
                "description": "A comfortable room for two guests.",
                "max_occupancy": 2,
                "price_per_night": Decimal("3000.00"),
                "total_rooms": 10,
            },
            {
                "name": "Deluxe Room",
                "description": "A spacious room with upgraded amenities.",
                "max_occupancy": 3,
                "price_per_night": Decimal("4800.00"),
                "total_rooms": 6,
            },
            {
                "name": "Family Suite",
                "description": "A larger suite suitable for family holidays.",
                "max_occupancy": 4,
                "price_per_night": Decimal("7200.00"),
                "total_rooms": 3,
            },
        ]

        hotels_created = 0
        rooms_created = 0
        availability_created = 0

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
                    availability_date = today + timedelta(
                        days=day_offset
                    )

                    _, created = RoomAvailability.objects.get_or_create(
                        room_type=room,
                        date=availability_date,
                        defaults={
                            "available_rooms": room.total_rooms,
                        },
                    )
                    availability_created += int(created)

        self.stdout.write(
            self.style.SUCCESS("Hotel seeding completed successfully.")
        )
        self.stdout.write(f"New hotels: {hotels_created}")
        self.stdout.write(f"New room types: {rooms_created}")
        self.stdout.write(
            f"New availability records: {availability_created}"
        )
