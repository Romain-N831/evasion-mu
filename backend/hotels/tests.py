# Create your tests here.
from django.test import TestCase
from datetime import date

from .models import Hotel, RoomType, RoomAvailability


class HotelModelTest(TestCase):

    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            description="A hotel in Mauritius",
            city="Curepipe",
            region="Plaines Wilhems",
            star_rating=4
        )

    def test_hotel_creation(self):
        self.assertEqual(self.hotel.name, "Test Hotel")

    def test_hotel_string_representation(self):
        self.assertEqual(str(self.hotel), "Test Hotel")


class RoomTypeModelTest(TestCase):

    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel"
        )

        self.room = RoomType.objects.create(
            hotel=self.hotel,
            name="Deluxe Room",
            max_occupancy=2,
            price_per_night=1500,
            total_rooms=5
        )

    def test_room_type_creation(self):
        self.assertEqual(self.room.name, "Deluxe Room")

    def test_room_type_string_representation(self):
        self.assertEqual(str(self.room), "Test Hotel — Deluxe Room")


class RoomAvailabilityModelTest(TestCase):

    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Test Hotel"
        )

        self.room = RoomType.objects.create(
            hotel=self.hotel,
            name="Standard Room",
            price_per_night=1000,
            total_rooms=5
        )

        self.availability = RoomAvailability.objects.create(
            room_type=self.room,
            date=date(2026, 12, 1),
            available_rooms=3
        )

    def test_availability_creation(self):
        self.assertEqual(self.availability.available_rooms, 3)

    def test_availability_string_representation(self):
        self.assertIn("3 available", str(self.availability))