from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Park, Rating
from .serializers import ParkSerializer, RatingSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if isinstance(obj, Rating):
            return obj.user == request.user
        return request.user.is_superuser


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class ParkViewSet(viewsets.ModelViewSet):
    queryset = Park.objects.all().order_by('name')
    serializer_class = ParkSerializer
    permission_classes = [AdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        country = self.request.query_params.get('country')
        region = self.request.query_params.get('region')
        name = self.request.query_params.get('name')
        location = self.request.query_params.get('location')
        has_image = self.request.query_params.get('has_image')
        has_website = self.request.query_params.get('has_website')
        
        if country:
            qs = qs.filter(country__iexact=country)
        if region:
            qs = qs.filter(region__iexact=region)
        if name:
            qs = qs.filter(name__icontains=name)
        if location:
            qs = qs.filter(location__icontains=location)
        if has_image:
            qs = qs.exclude(image='').exclude(image__isnull=True)
        if has_website:
            qs = qs.exclude(official_website='').exclude(official_website__isnull=True)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        park = self.get_object()
        score = request.data.get('score')
        comment = request.data.get('comment', '')
        try:
            score_int = int(score)
        except (TypeError, ValueError):
            return Response({'detail': 'score must be an integer between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        if score_int < 1 or score_int > 5:
            return Response({'detail': 'score must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            park=park,
            defaults={'score': score_int, 'comment': comment}
        )
        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def ratings(self, request, pk=None):
        park = self.get_object()
        qs = park.ratings.all().order_by('-created_at')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = RatingSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RatingSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def stats(self, request):
        """Get park statistics"""
        total_parks = Park.objects.count()
        parks_with_images = Park.objects.exclude(image='').exclude(image__isnull=True).count()
        parks_with_websites = Park.objects.exclude(official_website='').exclude(official_website__isnull=True).count()
        total_ratings = Rating.objects.count()
        
        return Response({
            'total_parks': total_parks,
            'parks_with_images': parks_with_images,
            'parks_with_websites': parks_with_websites,
            'total_ratings': total_ratings,
            'image_percentage': round((parks_with_images / total_parks * 100) if total_parks > 0 else 0, 1),
            'website_percentage': round((parks_with_websites / total_parks * 100) if total_parks > 0 else 0, 1),
        })


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all().order_by('-created_at')
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 