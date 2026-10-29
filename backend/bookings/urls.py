# Define routes within the bookings app.
from django.urls import path

# Import our own booking views.
from . import views


# Keep these URL names separate from names in other apps.
app_name = 'bookings'


urlpatterns = [
    # Customer cancellation request for one owned booking.
    path(
        '<int:pk>/cancel/',
        views.request_cancellation,
        name='request-cancellation',
    ),
    
    # Activity booking form: /bookings/activity/5/
    # activity_id identifies the activity the customer wants to book.
    # Django passes this ID to the book_activity() function in views.py.
    path(
        'activity/<int:activity_id>/',
        views.book_activity,
        name='book-activity',
    ),


    # Customer booking history: /bookings/my-bookings/
    path(
        'my-bookings/',
        views.BookingListView.as_view(),
        name='booking-list',
    ),

    # One booking: for example, /bookings/12/
    # <int:pk> captures a whole number and passes it to DetailView.
    path(
        '<int:pk>/',
        views.BookingDetailView.as_view(),
        name='booking-detail',
    ),

]
