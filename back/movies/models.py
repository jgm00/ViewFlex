from django.db import models
from django.conf import settings

# Create your models here.

class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    genre_ids = models.ManyToManyField(Genre, related_name='movies')
    runtime = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100)
    release_date = models.DateField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.TextField(null=True, blank=True)
    vote_average = models.FloatField(null=True)
    backdrop_path = models.TextField(null=True, blank=True)
    adult = models.BooleanField(null=True, blank=True)
    original_language = models.TextField(null=True, blank=True)
    is_playing = models.BooleanField(null=True, blank=True)
    youtube_url = models.TextField(null=True, blank=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_movies", blank=True)
    actors = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title
    
# class Playing_Movie(models.Model):
#     id = models.IntegerField(primary_key=True)
#     genre_ids = models.ManyToManyField(Genre, related_name='now_movies')
#     runtime = models.IntegerField(null=True, blank=True)
#     title = models.CharField(max_length=100)
#     release_date = models.DateField(null=True, blank=True)
#     overview = models.TextField(null=True, blank=True)
#     poster_path = models.TextField(null=True, blank=True)
#     vote_average = models.FloatField(null=True)
#     backdrop_path = models.TextField(null=True, blank=True)
#     adult = models.BooleanField(null=True, blank=True)
#     original_language = models.TextField(null=True, blank=True)
#     like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_now_movies")

#     def __str__(self):
#         return self.title
    
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='movie_reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    # now_movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='now_reviews')
    content = models.CharField(max_length=100)
    rating = models.FloatField(
        choices=[(i/2, str(i/2)) for i in range(1, 11)],  # 1, 1.5, 2, 2.5, ..., 5
        default=5
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
    
class Theater(models.Model):
    movie_id = models.IntegerField()
    movie_name = models.CharField(max_length=100, null=True, blank=True)
    chain = models.CharField(max_length=50, null=True, blank=True)  # 메가박스, CGV 등
    area = models.CharField(max_length=50, null=True, blank=True)  # 서울, 부산/대구/경상 등
    theater = models.CharField(max_length=100, null=True, blank=True) # 극장명
    screen = models.CharField(max_length=100, null=True, blank=True)   # 상영관
    showing_times = models.JSONField()  # ["10:30", "13:30"] 형식의 시간 배열
    movie_type = models.CharField(max_length=50, null=True, blank=True)# 2D(자막), 2D 등
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True) 

    class Meta:
        db_table = 'movies_theater'

    def __str__(self):
        return f"{self.chain} {self.theater} - {self.movie_name}"
    

