from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('submit/', views.submit_quiz, name='submit_quiz'),
    path('api/tutor/', views.chat_api, name='chat_api'),
]