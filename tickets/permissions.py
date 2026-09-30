from rest_framework import permissions

class IsTicketAuthorOrStaff(permissions.BasePermission):
# просмотр и изменение конкретного тикета сам автор автор, закрепленный спец либо администратор
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADM':
            return True
        if request.user.role == 'SPC':
            return obj.status == 'OPN' or obj.specialist == request.user
        
        # пользователь, только если он автор тикета
        return obj.user == request.user
