from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('api/tutor/', views.tutor_chat_api, name='tutor_chat_api'),
    path('api/evaluate/', views.evaluate_development, name='evaluate_development'),
]