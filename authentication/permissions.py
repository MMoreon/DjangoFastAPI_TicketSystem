from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
# проверка на роль 'ADM'
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADM'  # Или User.Role.ADMIN, если импортировать модель
        )
