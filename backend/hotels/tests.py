from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

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


class HotelViewTest(TestCase):

    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Lagoon View Resort",
            city="Flic en Flac",
            region="West",
            star_rating=4,
            is_active=True,
        )
        self.inactive_hotel = Hotel.objects.create(
            name="Hidden Hotel",
            city="Port Louis",
            region="Northwest",
            is_active=False,
        )
        RoomType.objects.create(
            hotel=self.hotel,
            name="Deluxe Room",
            price_per_night=Decimal("4500.00"),
            total_rooms=4,
        )
        RoomType.objects.create(
            hotel=self.hotel,
            name="Standard Room",
            price_per_night=Decimal("2800.00"),
            total_rooms=8,
        )

    def test_hotel_list_renders_active_hotels(self):
        response = self.client.get(reverse("hotels:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lagoon View Resort")
        self.assertNotContains(response, "Hidden Hotel")

    def test_hotel_list_filters_by_search_and_region(self):
        response = self.client.get(
            reverse("hotels:list"),
            {"q": "Lagoon", "region": "West"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lagoon View Resort")

        empty_response = self.client.get(
            reverse("hotels:list"),
            {"region": "East"},
        )
        self.assertContains(empty_response, "No hotels found")

    def test_hotel_detail_uses_cheapest_room_as_starting_price(self):
        response = self.client.get(
            reverse("hotels:detail", args=[self.hotel.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rs 2800.00")
        self.assertContains(response, 'id="rooms"')

    def test_inactive_hotel_detail_returns_404(self):
        response = self.client.get(
            reverse("hotels:detail", args=[self.inactive_hotel.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_hotel_delete_uses_confirm_template_for_staff(self):
        from django.contrib.auth.models import Permission, User

        user = User.objects.create_user(username="staff", password="pass12345")
        permission = Permission.objects.get(codename="delete_hotel")
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.get(
            reverse("hotels:hotel_delete", args=[self.hotel.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotels/hotel_confirm_delete.html")