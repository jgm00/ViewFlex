from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/mypage/', views.my_page),
    path('<str:username>/follow/', views.follow),
    path('<str:username>/profile/image/', views.update_profile_image),
    path('survey/', views.save_survey, name='save_survey'),
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
]