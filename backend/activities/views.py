from django.shortcuts import render

from .models import Activity


def activity_list(request):
    activities = Activity.objects.filter(is_active=True)

    context = {
        "activities": activities,
    }

    return render(request, "activities/activity_list.html", context)
