from rest_framework import serializers
from .models import Movie, Genre, Review, Theater
from django.contrib.auth import get_user_model

User = get_user_model()

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    genre_ids = GenreSerializer(many=True, read_only=True)
    like_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    
    class Meta:
        model = Movie
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    movie__title = serializers.CharField(source='movie.title', read_only=True)
    movie__id = serializers.IntegerField(source='movie.id', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'content', 'rating', 'created_at', 'updated_at', 'movie__title', 'movie__id', 'user', 'user_username')
        read_only_fields = ('user', 'movie')

class GenreStatsSerializer(serializers.Serializer):
    genre = serializers.CharField()
    count = serializers.IntegerField()

class LikedMoviesWithGenreStatsSerializer(serializers.Serializer):
    movies = MovieSerializer(many=True)
    genre_stats = serializers.SerializerMethodField()

    def get_genre_stats(self, obj):
        genre_stats = {}
        for movie in obj['movies']:
            for genre in movie.genre_ids.all():
                genre_name = genre.name
                if genre_name in genre_stats:
                    genre_stats[genre_name] += 1
                else:
                    genre_stats[genre_name] = 1
        return [{'genre': genre, 'count': count} for genre, count in genre_stats.items()]

class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = '__all__'

class MovieWithTheatersSerializer(serializers.ModelSerializer):
    genre_ids = GenreSerializer(many=True, read_only=True)
    like_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    theaters = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = '__all__'
    
    def get_theaters(self, obj):
        theaters = Theater.objects.filter(movie_id=obj.id)
        return TheaterSerializer(theaters, many=True).data