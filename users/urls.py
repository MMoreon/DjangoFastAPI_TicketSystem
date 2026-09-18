from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth, name='auth'),
    path('home/', views.home),
    path('register/', views.register, name='register'),
]