from django.urls import path
from .views import ParkCreateView, trip_planner

urlpatterns = [
    path('add/', ParkCreateView.as_view(), name='park-add'),
    path("trip-planner/<int:park_id>/", trip_planner, name="trip_planner"),
]

