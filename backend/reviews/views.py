from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

import backend.reviews.models
from backend.activities.models import Activity
from .models import Review
from .forms import ReviewForm

def activity_reviews(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    reviews = Review.objects.filter(
        activity=activity,
        moderation_status=Review.ModerationStatus.APPROVED
    )
    return render(request, "reviews/activity_reviews.html", {
        "activity": activity,
        "reviews": reviews
    })

@login_required
def add_review(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.activity = activity
            review.moderation_status = Review.ModerationStatus.PENDING

            review.customer = request.user.customer
            review.save()

            return redirect("activity_review", activity_id=activity.id)

        else:
            form = ReviewForm()

        return render(request, "reviews/add_review.html", {
            "activity": activity,
            "form": form
        })


# Create your views here.
