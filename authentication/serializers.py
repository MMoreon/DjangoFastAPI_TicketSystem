from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        #стандартный токен
        token = super().get_token(user)

        # в тело токена кастомные claims
        token['name'] = user.name
        token['role'] = user.role  #ADM USR SPC
        token['email'] = user.email

        return token

class RegisterSerializer(serializers.ModelSerializer):
    # не вернется
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'role')

    def create(self, validated_data):
        #  create_user в core.models.UserManager
        # автоматически возьмет пароль, захеширует его и сохранит
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.USER)  # Если роль не прислали, будет обычный USER
        )
        return user

# для администратора, чтобы не мог менять пароли 
class ChangeUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role', 'is_active', 'is_staff')
