from rest_framework import serializers
from .models import Park, Rating


class RatingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'park', 'user', 'user_username', 'score', 'comment', 'created_at']
        read_only_fields = ['user']


class ParkSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta:
        model = Park
        fields = ['id', 'name', 'description', 'location', 'country', 'region', 'official_website', 'image', 'average_rating', 'ratings_count']

    def get_average_rating(self, obj):
        ratings_qs = obj.ratings.all()
        if not ratings_qs.exists():
            return None
        avg = sum(r.score for r in ratings_qs) / ratings_qs.count()
        return round(avg, 2)

    def get_ratings_count(self, obj):
        return obj.ratings.count() 