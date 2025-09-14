from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list), 
    path('<int:movie_id>/', views.movie_detail),  
    path('<int:movie_id>/reviews/', views.review), 
    path('reviews/<int:review_id>/', views.review_detail),
    path('<int:movie_id>/likes/', views.movie_like),
    path('liked/', views.liked), 
    path('liked_genre/', views.liked_genre),
    path('liked_genre/<str:username>/', views.liked_genre_by_username),
    path('recommended/genre/', views.recommended_with_genre),
    path('recommended/following/', views.recommended_with_following),
    path('recommended/box_office/', views.recommended_with_box_office),
    path('recommended/reviewed_actors/', views.recommended_with_reviewed_actors),
    path('recommended/release_date/', views.recommended_with_release_date),
    path('theaters/', views.theater_list),
    path('<int:movie_id>/theaters/', views.movie_theaters),
    path('<int:movie_id>/with_theaters/', views.movie_detail_with_theaters),
    path('playing_movies/', views.playing_movies),
    path('search/', views.search_movies),
    path('filter/', views.filter_movies),
]