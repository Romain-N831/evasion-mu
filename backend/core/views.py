from django.shortcuts import render

from activities.models import Activity


def home(request):
    activities = Activity.objects.filter(
        is_active= True
    ).order_by("title")[:6]
    return render(request, 'core/home.html', {
        "activities": activities
    })