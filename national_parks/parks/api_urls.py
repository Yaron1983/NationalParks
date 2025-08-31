from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ParkViewSet, RatingViewSet

router = DefaultRouter()
router.register(r'parks', ParkViewSet, basename='park')
router.register(r'ratings', RatingViewSet, basename='rating')

urlpatterns = [
    path('', include(router.urls)),
] 