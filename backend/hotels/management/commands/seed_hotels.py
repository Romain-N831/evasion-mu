"""Seed real Mauritius hotels for local development.

Hotel names and locations are based on the Mauritius Tourism Authority's
accommodation directory. Room categories, prices and availability are
illustrative demo data only; they are not live hotel inventory or official rates.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hotels.models import Hotel, RoomType, RoomAvailability


class Command(BaseCommand):
    help = "Seed real Mauritius hotels with illustrative room and availability demo data."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()

        hotels_data = [
            {
                "name": "Labourdonnais Waterfront Hotel",
                "image_path": "hotels/images/labourdonnais.jpeg",
                "description": "A waterfront hotel at Caudan Waterfront in Port Louis, close to the capital's business district, shops and restaurants.",
                "address": "Caudan Waterfront",
                "city": "Port Louis",
                "region": "Port Louis",
                "star_rating": 5,
            },
            {
                "name": "Hennessy Park Hotel",
                "image_path": "hotels/images/hennessy-park.jpeg",
                "description": "A contemporary hotel in Ebene Cybercity, convenient for business travel and exploring the central plateau.",
                "address": "65, Cybercity",
                "city": "Ebene",
                "region": "Moka",
                "star_rating": 4,
            },
            {
                "name": "Hilton Mauritius Resort & Spa",
                "image_path": "hotels/images/hilton-mauritius.jpeg",
                "description": "A beachfront resort in Wolmar, Flic en Flac, on the west coast of Mauritius.",
                "address": "Wolmar, Flic en Flac",
                "city": "Flic en Flac",
                "region": "Black River",
                "star_rating": 5,
            },
            {
                "name": "La Pirogue Mauritius",
                "image_path": "hotels/images/la-pirogue.jpeg",
                "description": "A beachfront resort in Wolmar, Flic en Flac, known for its thatched-roof bungalow style and tropical gardens.",
                "address": "Wolmar Coastal Road",
                "city": "Flic en Flac",
                "region": "Black River",
                "star_rating": 4,
            },
            {
                "name": "Sugar Beach Mauritius",
                "image_path": "hotels/images/sugar-beach.jpeg",
                "description": "A beachfront resort on the west coast at Wolmar, Flic en Flac.",
                "address": "Wolmar, Flic en Flac",
                "city": "Flic en Flac",
                "region": "Black River",
                "star_rating": 5,
            },
            {
                "name": "Constance Belle Mare Plage",
                "image_path": "hotels/images/constance-belle-mare.jpeg",
                "description": "A resort on the east coast at Belle Mare, with beachfront accommodation and golf facilities.",
                "address": "Pointe de Flacq, Belle Mare",
                "city": "Belle Mare",
                "region": "Flacq",
                "star_rating": 5,
            },
            {
                "name": "LUX* Belle Mare Resort & Villas",
                "image_path": "hotels/images/lux-belle-mare.jpeg",
                "description": "A beachfront resort on the east coast at Belle Mare, overlooking the lagoon.",
                "address": "Coastal Road, Belle Mare",
                "city": "Belle Mare",
                "region": "Flacq",
                "star_rating": 5,
            },
            {
                "name": "Four Seasons Resort Mauritius at Anahita",
                "image_path": "hotels/images/four-seasons-anahita.jpeg",
                "description": "A luxury villa resort at Beau Champ on the east coast, set beside a lagoon and golf estate.",
                "address": "Beau Champ, Grand River South East",
                "city": "Beau Champ",
                "region": "Flacq",
                "star_rating": 5,
            },
            {
                "name": "Heritage Le Telfair Golf & Wellness Resort",
                "image_path": "hotels/images/heritage-le-telfair.jpeg",
                "description": "A resort in the Bel Ombre estate on Mauritius's south coast, with golf, wellness facilities and access to the surrounding nature.",
                "address": "Domaine de Bel Ombre",
                "city": "Bel Ombre",
                "region": "Savanne",
                "star_rating": 5,
            },
            {
                "name": "Dinarobin Beachcomber Golf Resort & Spa",
                "image_path": "hotels/images/dinarobin.jpeg",
                "description": "An all-suite beachfront resort on the Le Morne peninsula in southwest Mauritius, beneath Le Morne Brabant.",
                "address": "Le Morne Peninsula",
                "city": "Le Morne",
                "region": "Black River",
                "star_rating": 5,
            },
            {
                "name": "Trou aux Biches Beachcomber Golf Resort & Spa",
                "image_path": "hotels/images/trou-aux-biches.jpeg",
                "description": "A beachfront resort in Trou aux Biches on the northwest coast, with tropical gardens and leisure facilities.",
                "address": "Trou aux Biches",
                "city": "Trou aux Biches",
                "region": "Pamplemousses",
                "star_rating": 5,
            },
            {
                "name": "Constance Prince Maurice",
                "image_path": "hotels/images/constance-prince-maurice.jpeg",
                "description": "A luxury resort on the northeast coast at Poste de Flacq, set beside a sheltered lagoon.",
                "address": "Choisy Road, Poste de Flacq",
                "city": "Poste de Flacq",
                "region": "Flacq",
                "star_rating": 5,
            },
        ]

        # Deactivate old fictional seed records without deleting existing data.
        legacy_demo_names = [
            "Tamarin Sunset Hotel",
            "Port Louis City Hotel",
            "Blue Bay Coral Resort",
            "Trou aux Biches Garden Hotel",
            "Mahebourg Heritage Inn",
        ]
        Hotel.objects.filter(name__in=legacy_demo_names).update(is_active=False)

        # Illustrative demo data, not actual hotel inventory or official rates.
        rooms_data = [
            {
                "name": "Standard Room",
                "description": "Illustrative sample room data for project demonstration.",
                "max_occupancy": 2,
                "price_per_night": Decimal("4500.00"),
                "total_rooms": 10,
            },
            {
                "name": "Deluxe Room",
                "description": "Illustrative sample room data for project demonstration.",
                "max_occupancy": 3,
                "price_per_night": Decimal("7500.00"),
                "total_rooms": 6,
            },
            {
                "name": "Family Suite",
                "description": "Illustrative sample room data for project demonstration.",
                "max_occupancy": 4,
                "price_per_night": Decimal("12000.00"),
                "total_rooms": 3,
            },
        ]

        hotels_created = 0
        rooms_created = 0
        availability_created = 0

        for hotel_data in hotels_data:
            hotel, created = Hotel.objects.update_or_create(
                name=hotel_data["name"],
                defaults={**hotel_data, "is_active": True},
            )
            hotels_created += int(created)

            for room_data in rooms_data:
                room, created = RoomType.objects.update_or_create(
                    hotel=hotel,
                    name=room_data["name"],
                    defaults={**room_data, "is_active": True},
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

        self.stdout.write(
            self.style.SUCCESS("Hotel seeding completed successfully.")
        )
        self.stdout.write(f"Hotel records created: {hotels_created}")
        self.stdout.write(f"Room type records created: {rooms_created}")
        self.stdout.write(
            f"Availability records created: {availability_created}"
        )
        self.stdout.write(
            self.style.WARNING(
                "Reminder: room types, prices and availability are illustrative demo data."
            )
        )
