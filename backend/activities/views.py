from django.shortcuts import render

from .models import Activity


def activity_list(request):
    activities = Activity.objects.filter(is_active=True)

    # Search by activity title or location.
    search_query = request.GET.get("q", "").strip()
    if search_query:
        activities = activities.filter(
            title__icontains=search_query
        ) | activities.filter(
            location__icontains=search_query
        )

    # Filter by category when one is selected.
    selected_category = request.GET.get("category", "").strip()
    if selected_category:
        activities = activities.filter(category=selected_category)

    # Get the available categories for the filter dropdown.
    categories = (
        Activity.objects.filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    context = {
        "activities": activities,
        "categories": categories,
        "search_query": search_query,
        "selected_category": selected_category,
    }

    return render(request, "activities/activity_list.html", context)