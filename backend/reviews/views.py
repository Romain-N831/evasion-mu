from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# render -> combines a template with data and returns an HTML response
# get_object_or_404 -> retrieves an object from the database. If it doesn't exist, Django returns a 404 error
# redirect -> sends the user to another URL after an action
from activities.models import Activity # imports the activity model so we can retrieve the activity being reviewed
from .models import Review # imports the Review model so we can retrieve and save reviews
from .forms import ReviewForm # imports the form that collects a rating and comment
# the '.' means the current Django app, which is reviews
def activity_reviews(request, activity_id): # displays approved reviews for an activity
    # request contains information about the incoming HTTP request
    activity = get_object_or_404(Activity, id=activity_id) # ask Django to find an Activity with database ID that matches the activity_id
    # if it does not exist, Django returns a 404 response

    reviews = Review.objects.filter( # filter() -> retrieves records matching the condition
        activity=activity,
        moderation_status=Review.ModerationStatus.APPROVED # selects only reviews that have been approved
    )
    return render(request, "reviews/reviews.html", {
        "activity": activity,
        "reviews": reviews
    })

@login_required # restricts a view to authenticated users
def add_review(request, activity_id): # allows a logged-in customer to submit a review
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == "POST": # usually used to submit data to the server
        form = ReviewForm(request.POST)

        if form.is_valid(): # checks if the submitted data satisfies the form's validation rules
            review = form.save(commit=False) # create the review without saving it
            review.activity = activity
            review.moderation_status = Review.ModerationStatus.PENDING # the review won't appear in the public list until it's approved

            review.customer = request.user.customer
            review.save() # save the review

            return redirect("activity_reviews", activity_id=activity.id)

    else:
        form = ReviewForm() # handle a GET request

    return render(request, "reviews/add_review.html", {
        "activity": activity,
        "form": form
    })



