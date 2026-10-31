# Import Django's administration tools.
from django.contrib import admin

# Import the four existing models from this app's models.py file.
from .models import Booking, Reservation, HotelReservation, PromoCode


# Configure how overall bookings appear in Django admin.
# ModelAdmin provides the standard admin behaviour that we customise below.
class BookingAdmin(admin.ModelAdmin):

    # Each name below becomes a column on the bookings list page.
    # These names match fields already defined in the Booking model.
    list_display = (
        'id',
        'customer',
        'booking_date',
        'total_amount',
        'status',
    )

    # Add sidebar filters for booking status and creation date.
    # For example, an administrator can display only Pending bookings.
    list_filter = (
        'status',
        'booking_date',
    )

    # Search using information from the customer's linked login account.
    # Double underscores let Django follow relationships between models:
    # Booking -> Customer -> User -> username, first_name, or last_name.
    search_fields = (
        'customer__user__username',
        'customer__user__first_name',
        'customer__user__last_name',
    )

    # Show these automatically generated values on the booking form,
    # but prevent administrators from typing replacements into these fields.
    readonly_fields = (
        'booking_date',
        'ticket_reference',
        'cancellation_requested_at',
    )

    # Make customer cancellation requests visible to staff reviewing bookings.
    fieldsets = (
        ('Booking details', {
            'fields': (
                'customer', 'booking_date', 'total_amount', 'status',
                'promo_code', 'discount_amount', 'ticket_reference',
            ),
        }),
        ('Cancellation request', {
            'fields': ('cancellation_requested_at', 'cancellation_reason'),
        }),
        ('Reschedule request', {
            'fields': ('reschedule_requested_for', 'reschedule_reason'),
        }),
    )


# Configure activity reservations.
# Each Reservation links an overall Booking to an ActivitySlot.
class ReservationAdmin(admin.ModelAdmin):

    # "activity" and "scheduled_date" are existing properties in your model.
    # They read information from the linked activity slot.
    list_display = (
        'id',
        'booking',
        'activity',
        'scheduled_date',
        'participant_count',
        'unit_price',
    )

    # Filter reservations by their activity.
    # Follow Reservation -> ActivitySlot -> Activity.
    list_filter = (
        'activity_slot__activity',
    )

    # Search by activity title or the booking customer's username.
    # Search fields use actual model relationships, not the properties above.
    search_fields = (
        'activity_slot__activity__title',
        'booking__customer__user__username',
    )


# Configure hotel reservations.
# Each HotelReservation links a Booking to a RoomType and stay dates.
class HotelReservationAdmin(admin.ModelAdmin):

    # Display the selected room type, dates, quantity, and nightly price.
    list_display = (
        'id',
        'booking',
        'room_type',
        'check_in',
        'check_out',
        'rooms_count',
        'guests_count',
        'price_per_night',
        'inventory_released',
    )

    # Allow administrators to filter hotel reservations by stay dates.
    list_filter = (
        'check_in',
        'check_out',
    )

    # Search through the room type's hotel, the room type itself,
    # or the booking customer's username.
    search_fields = (
        'room_type__hotel__name',
        'room_type__name',
        'booking__customer__user__username',
    )


# Configure promotional discount codes.
class PromoCodeAdmin(admin.ModelAdmin):

    # Display the discount details, validity period, and active status.
    list_display = (
        'code',
        'discount_type',
        'discount_value',
        'valid_from',
        'valid_until',
        'is_active',
    )

    # Filter codes by whether they are active and by discount type.
    list_filter = (
        'is_active',
        'discount_type',
    )

    # Add a search box that searches the promotional code text.
    search_fields = (
        'code',
    )


# Register each model with its corresponding admin configuration.
# First argument: the database model.
# Second argument: the class describing its admin appearance.
admin.site.register(Booking, BookingAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(HotelReservation, HotelReservationAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)
