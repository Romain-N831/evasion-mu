from django.urls import path
from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.wishlist_view, name="detail"),
    path("add/", views.add_to_wishlist, name="add"),
    path("remove/<int:item_id>/", views.remove_from_wishlist, name="remove"),
]