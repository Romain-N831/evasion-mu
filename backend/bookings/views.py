# Render our introductory bookings page.
from django.shortcuts import render

# Require users to log in before accessing protected class-based views.
from django.contrib.auth.mixins import LoginRequiredMixin

# Resolve named URLs when Django needs them.
from django.urls import reverse_lazy

# Django provides standard views for displaying lists and individual records.
from django.views import generic

# Import our existing Booking model.
from .models import Booking


# Keep the introductory bookings page available to everyone.
def index(request):
    context = {
        'page_title': 'Bookings',
    }
    return render(request, 'bookings/home.html', context)


# Display the bookings belonging to the logged-in customer.
# LoginRequiredMixin must appear before generic.ListView.
class BookingListView(LoginRequiredMixin, generic.ListView):

    # Tell Django which model this page displays.
    model = Booking

    # Specify the HTML template used for this page.
    template_name = 'bookings/booking_list.html'

    # The template will access the results using "booking_list".
    context_object_name = 'booking_list'

    # Send visitors here if they have not logged in.
    login_url = reverse_lazy('bookings:login')

    # Decide which database records this customer may see.
    def get_queryset(self):

        # Follow Booking -> Customer -> User.
        # Only include bookings linked to the currently logged-in user.
        # A user without a Customer profile receives an empty list.
        return Booking.objects.filter(
            customer__user=self.request.user
        ).order_by('-booking_date', '-pk')


# Display one booking and its associated reservations.
class BookingDetailView(LoginRequiredMixin, generic.DetailView):

    model = Booking
    template_name = 'bookings/booking_detail.html'

    # The template will access this single record using "booking".
    context_object_name = 'booking'

    login_url = reverse_lazy('bookings:login')

    def get_queryset(self):

        # Restrict the available records BEFORE Django looks up the URL's ID.
        # This prevents someone from viewing another customer's booking
        # simply by changing the number in the address bar.
        return Booking.objects.filter(
            customer__user=self.request.user
        )
# Create your views here.
