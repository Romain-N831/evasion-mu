from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from activities.models import Activity
from hotels.models import Hotel


class HomepageTests(TestCase):
    def test_homepage_shows_active_activities_and_hotels_in_carousels(self):
        activity = Activity.objects.create(
            title="Homepage activity", location="Blue Bay",
            current_price=Decimal("850.00"), is_active=True,
        )
        inactive_activity = Activity.objects.create(
            title="Hidden activity", location="Hidden",
            current_price=Decimal("100.00"), is_active=False,
        )
        hotel = Hotel.objects.create(
            name="Homepage hotel", city="Grand Baie", region="North", is_active=True,
        )
        Hotel.objects.create(name="Hidden hotel", is_active=False)

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-carousel')
        self.assertContains(response, activity.title)
        self.assertNotContains(response, inactive_activity.title)
        self.assertContains(response, hotel.name)
        self.assertNotContains(response, "Hidden hotel")
        self.assertContains(response, reverse("activities:detail", args=[activity.pk]))
        self.assertContains(response, reverse("hotels:detail", args=[hotel.pk]))

    def test_homepage_has_empty_states_when_there_is_no_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Our activities are coming soon")
        self.assertContains(response, "Our hotel collection is coming soon")
