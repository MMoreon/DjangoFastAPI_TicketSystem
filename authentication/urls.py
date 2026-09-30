from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView

from .views import (
    AdminChangeUserRoleView,
    AdminDeleteUserView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    RegisterView,
    DeleteUserView
)

app_name = 'authentication'

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    # для logout фронтенд должен отправить POST запрос с рефреш-токеном в теле
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # управление
    path('register/', RegisterView.as_view(), name='register'),
    path('delete/', DeleteUserView.as_view(), name='delete_user'),
    
    # админ
    path('users/<int:id>/delete/', AdminDeleteUserView.as_view(), name='admin_delete_user'),
    path('users/<int:id>/role/', AdminChangeUserRoleView.as_view(), name='admin_change_role'),
]
