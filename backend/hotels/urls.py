
from django.urls import path
from . import views

app_name = "hotels"

urlpatterns = [

    # Public hotel pages
    path("", views.hotel_list, name="list"),
    path("<int:hotel_id>/", views.hotel_detail, name="detail"),

    # Hotel management
    path("add/", views.HotelCreate.as_view(), name="hotel_add"),
    path("<int:pk>/edit/", views.HotelUpdate.as_view(), name="hotel_edit"),
    path("<int:pk>/delete/", views.HotelDelete.as_view(), name="hotel_delete"),

    # Room type management
    path("rooms/add/", views.RoomTypeCreate.as_view(), name="room_add"),
    path("rooms/<int:pk>/edit/", views.RoomTypeUpdate.as_view(), name="room_edit"),
    path("rooms/<int:pk>/delete/", views.RoomTypeDelete.as_view(), name="room_delete"),

    # Room availability management
    path(
        "availability/add/",
        views.RoomAvailabilityCreate.as_view(),
        name="availability_add"
    ),

    path(
        "availability/<int:pk>/edit/",
        views.RoomAvailabilityUpdate.as_view(),
        name="availability_edit"
    ),

    path(
        "availability/<int:pk>/delete/",
        views.RoomAvailabilityDelete.as_view(),
        name="availability_delete"
    ),
]
