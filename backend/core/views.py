from django.shortcuts import render

from activities.models import Activity
from hotels.models import Hotel


def home(request):
    activities = Activity.objects.filter(
        is_active= True
    ).order_by("title")[:6]
    hotels = Hotel.objects.filter(is_active=True).order_by("name")[:6]
    return render(request, 'core/home.html', {
        "activities": activities,
        "hotels": hotels,
    })

def aboutus(request):
    return render(request, "core/aboutus.html")
