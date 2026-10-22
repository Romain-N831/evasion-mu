from django.contrib import admin
from .models import PromoCode, Booking, Reservation, HotelReservation

admin.site.register(PromoCode)
admin.site.register(Booking)
admin.site.register(Reservation)
admin.site.register(HotelReservation)