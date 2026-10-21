from django.urls import path, include
from . import views

urlpatterns = [
    path("activity/<int:activity_id>/", views.activity_reviews, name="activity_reviews"),
    path("activity/<int:activity_id>/add/", views.add_review, name="add_review"),
]