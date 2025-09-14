from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/mypage/', views.my_page),
    path('<str:username>/follow/', views.follow),
    path('<str:username>/profile/image/', views.update_profile_image),
    # path('reviews/<int:review_id>/update/', views.update_review, name='update_review'),
    # path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('survey/', views.save_survey, name='save_survey'),
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
]