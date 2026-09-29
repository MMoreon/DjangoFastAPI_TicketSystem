from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, ChangeUserRoleSerializer
from .permissions import IsAdminUserRole


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    
class DeleteUserView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)  # для авторизованных пользователей

    def get_object(self):
        # возвращает объект пользователя, чтобы удалить самого себя
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Пользователь успешно удален."}, 
            status=status.HTTP_200_OK
        )


class AdminDeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUserRole,)  #проверка на админа
    lookup_field = 'id'  # Django будет искать пользователя по id из url

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # админ не должен случайно удалить себя через этот эндпоинт
        if instance == request.user:
            return Response(
                {"detail": "Вы не можете удалить самого себя через этот эндпоинт."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Пользователь {instance.email} успешно удален администратором."}, 
            status=status.HTTP_200_OK
        )

class AdminChangeUserRoleView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangeUserRoleSerializer
    permission_classes = (IsAdminUserRole,)
    lookup_field = 'id'