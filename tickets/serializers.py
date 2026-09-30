from rest_framework import serializers
from .models import Comment, Ticket


# пользователь
class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'title', 'description', 'status', 'created_at', 'updated_at')

        read_only_fields = ('id', 'status', 'created_at', 'updated_at')

class UserConfirmTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('status',)

    def validate_status(self, value):
        if value != Ticket.Status.CLOSED:
            raise serializers.ValidationError("Вы можете только закрыть решенный тикет.")
        
        if self.instance.status != Ticket.Status.RESOLVED:
            raise serializers.ValidationError("Нельзя закрыть тикет, пока он не переведен в статус 'решена'.")
            
        return value

# спец
class SpecialistUpdateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('status',)

    def validate_status(self, value):
        current_status = self.instance.status

        if current_status == Ticket.Status.OPEN and value != Ticket.Status.IN_PROGRESS:
            raise serializers.ValidationError("Открытый тикет нужно сначала взять в работу PRG.")

        if current_status == Ticket.Status.IN_PROGRESS and value != Ticket.Status.RESOLVED:
            raise serializers.ValidationError("Вы можете только перевести задачу в статус решена.")

        if value == Ticket.Status.CLOSED:
            raise serializers.ValidationError("Специалист не может закрыть тикет. Это должен сделать пользователь.")

        return value

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'user_name', 'user_email')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        # ID из параметров URL
        ticket_id = self.context['view'].kwargs.get('ticket_id')
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Указанный тикет не существует.")

        if ticket.status == Ticket.Status.CLOSED:
            raise serializers.ValidationError("Нельзя оставлять комментарии в закрытом тикете.")

        # cохраняем объект тикета в валидированные данные чтобы использовать в perform_create
        attrs['ticket'] = ticket
        return attrs