# Define routes within the bookings app.
from django.urls import path

# Use Django's existing login and logout views.
from django.contrib.auth import views as auth_views

# Import our own booking views.
from . import views


# Keep these URL names separate from names in other apps.
app_name = 'bookings'


urlpatterns = [
    # Introductory page: /bookings/
    path('', views.index, name='index'),
    
    
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

    # Login using Django's existing account and password handling.
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='bookings/login.html',

            # Default destination after login when no "next" URL is supplied.
            next_page='bookings:booking-list',
        ),
        name='login',
    ),

    # Logout accepts a POST request, submitted by our logout form.
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='bookings:index',
        ),
        name='logout',
    ),
]