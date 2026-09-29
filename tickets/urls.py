from django.urls import path
from tickets import views

app_name = 'tikets'

urlpatterns = [
    path('', views.auth, name='auth'),
    path('home/', views.home),
    path('register/', views.register, name='register'),
]