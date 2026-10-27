# Create your views here.

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Hotel, RoomType, RoomAvailability


# Display all active hotels and allow searching.
def hotel_list(request):

    hotels = Hotel.objects.filter(is_active=True)

    search_query = request.GET.get("q", "").strip()

    if search_query:
        hotels = hotels.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(region__icontains=search_query)
        )

    selected_region = request.GET.get("region", "").strip()

    if selected_region:
        hotels = hotels.filter(region__iexact=selected_region)

    regions = (
        Hotel.objects.filter(is_active=True)
        .exclude(region="")
        .values_list("region", flat=True)
        .distinct()
        .order_by("region")
    )

    context = {
        "hotels": hotels,
        "search_query": search_query,
        "regions": regions,
        "selected_region": selected_region,
    }

    return render(request, "hotels/hotel_list.html", context)


# Display one hotel and its active room types.
def hotel_detail(request, hotel_id):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id,
        is_active=True
    )

    room_types = hotel.room_types.filter(is_active=True)

    context = {
        "hotel": hotel,
        "room_types": room_types,
    }

    return render(
        request,
        "hotels/hotel_detail.html",
        context
    )


# Create a hotel.
class HotelCreate(PermissionRequiredMixin, CreateView):

    model = Hotel
    fields = [
        "name",
        "description",
        "address",
        "city",
        "region",
        "star_rating",
        "image_url",
        "is_active",
    ]

    permission_required = "hotels.add_hotel"
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:list")


# Update a hotel.
class HotelUpdate(PermissionRequiredMixin, UpdateView):

    model = Hotel
    fields = [
        "name",
        "description",
        "address",
        "city",
        "region",
        "star_rating",
        "image_url",
        "is_active",
    ]

    permission_required = "hotels.change_hotel"
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:list")


# Delete a hotel.
class HotelDelete(PermissionRequiredMixin, DeleteView):

    model = Hotel
    permission_required = "hotels.delete_hotel"
    template_name = "hotels/hotel_confirm_delete.html"
    success_url = reverse_lazy("hotels:list")


# Create a room type.
class RoomTypeCreate(PermissionRequiredMixin, CreateView):

    model = RoomType
    fields = "__all__"

    permission_required = "hotels.add_roomtype"
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:list")


# Update a room type.
class RoomTypeUpdate(PermissionRequiredMixin, UpdateView):

    model = RoomType
    fields = "__all__"

    permission_required = "hotels.change_roomtype"
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:list")


# Delete a room type.
class RoomTypeDelete(PermissionRequiredMixin, DeleteView):

    model = RoomType
    permission_required = "hotels.delete_roomtype"
    template_name = "hotels/hotel_confirm_delete.html"
    success_url = reverse_lazy("hotels:list")


# Create room availability.
class RoomAvailabilityCreate(
    PermissionRequiredMixin, CreateView
):

    model = RoomAvailability
    fields = "__all__"

    permission_required = "hotels.add_roomavailability"
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:list")


# Update room availability.
class RoomAvailabilityUpdate(
    PermissionRequiredMixin, UpdateView
):

    model = RoomAvailability
    fields = "__all__"

    permission_required = "hotels.change_roomavailability"
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:list")


# Delete room availability.
class RoomAvailabilityDelete(
    PermissionRequiredMixin, DeleteView
):

    model = RoomAvailability
    permission_required = "hotels.delete_roomavailability"
    template_name = "hotels/hotel_confirm_delete.html"
    success_url = reverse_lazy("hotels:list")
