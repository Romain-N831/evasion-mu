from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
# render -> combines a template with data and returns an HTML response
# get_object_or_404 -> retrieves an object from the database. If it doesn't exist, Django returns a 404 error
# redirect -> sends the user to another URL after an action
from activities.models import Activity # imports the activity model so we can retrieve the activity being reviewed
from bookings.models import Booking, Reservation
from .models import Review # imports the Review model so we can retrieve and save reviews
from .forms import ReviewForm # imports the form that collects a rating and comment
# the '.' means the current Django app, which is reviews
def activity_reviews(request, activity_id): # displays approved reviews for an activity
    # request contains information about the incoming HTTP request
    activity = get_object_or_404(Activity, id=activity_id, is_active=True) # ask Django to find an Activity with database ID that matches the activity_id
    # if it does not exist, Django returns a 404 response

    reviews = Review.objects.filter( # filter() -> retrieves records matching the condition
        activity = activity,
        moderation_status=Review.ModerationStatus.APPROVED # selects only reviews that have been approved
    )

    summary = reviews.aggregate(
        average_rating = Avg("rating"),
        total_reviews = Count("id")
    )

    context = {
        "activity": activity,
        "reviews": reviews,
        "average_rating": summary["average_rating"],
        "total_reviews": summary["total_reviews"],
    }

    return render(request, "reviews/review.html", context
    )

@login_required # restricts a view to authenticated users
def add_review(request, activity_id): # allows a logged-in customer to submit a review
    activity = get_object_or_404(Activity, id=activity_id, is_active=True)

    # A customer may review an activity only after taking part in it.
    # Reservation -> ActivitySlot -> Activity links the booking to the activity.
    eligible_booking_exists = Reservation.objects.filter(
        booking__customer__user=request.user,
        booking__status=Booking.Status.COMPLETED,
        activity_slot__activity=activity,
    ).exists()

    if not eligible_booking_exists:
        messages.error(
            request,
            "You can review this activity only after a completed booking.",
        )
        return redirect("activity_reviews", activity_id=activity.pk)

    # Keep one review per customer for an activity, even while it is pending.
    if Review.objects.filter(
        customer__user=request.user,
        activity=activity,
    ).exists():
        messages.info(request, "You have already submitted a review for this activity.")
        return redirect("activity_reviews", activity_id=activity.pk)

    if request.method == "POST": # usually used to submit data to the server
        form = ReviewForm(request.POST)

        if form.is_valid(): # checks if the submitted data satisfies the form's validation rules
            review = form.save(commit=False) # create the review without saving it
            review.activity = activity
            review.customer = request.user.customer_profile
            review.moderation_status = Review.ModerationStatus.PENDING # the review won't appear in the public list until it's approved

            review.save() # save the review

            return redirect("activity_reviews", activity_id=activity.id)

    else:
        form = ReviewForm() # handle a GET request

    return render(request, "reviews/add_review.html", {
        "activity": activity,
        "form": form
    })



