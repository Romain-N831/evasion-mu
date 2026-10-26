from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q, Avg, Count
from django.utils import timezone

from .models import Activity, ActivityBlockedDate
from reviews.models import Review


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


def activity_detail(request, activity_id):
    activity = get_object_or_404(
        Activity,
        id=activity_id,
        is_active=True
    )

    # Retrieve only approved reviews for this activity.
    approved_reviews = Review.objects.filter(
        activity=activity,
        moderation_status=Review.ModerationStatus.APPROVED
    )

    # Calculate the average rating and approved review count.
    review_summary = approved_reviews.aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id")
    )

    # Show the three newest approved reviews on the detail page.
    review_preview = approved_reviews.order_by(
        "-created_at"
    )[:3]
    
    # Retrieve dates blocked for this activity or all activities.
    blocked_dates = ActivityBlockedDate.objects.filter(
        Q(activity=activity) | Q(activity__isnull=True)
    ).values_list("date", flat=True)    

    # Find upcoming sessions and calculate booked places.
    slots = (
        activity.slots
        .filter(
            is_active=True,
            starts_at__gte=timezone.now()
        )
        .exclude(
            starts_at__date__in=blocked_dates
        )
        .annotate(
            booked_places=Sum(
                "reservations__participant_count",
                filter=Q(
                    reservations__booking__status__in=[
                        "PENDING",
                        "CONFIRMED"
                    ]
                )
            )
        )
        .order_by("starts_at")
    )

    for slot in slots:
        slot.available_places = slot.capacity - (
            slot.booked_places or 0
        )

    available_slots = [
        slot for slot in slots
        if slot.available_places > 0
    ]

    context = {
        "activity": activity,
        "available_slots": available_slots,
        "average_rating": review_summary["average_rating"],
        "total_reviews": review_summary["total_reviews"],
        "review_preview": review_preview,
    }

    return render(
        request,
        "activities/activity_detail.html",
        context
    )
