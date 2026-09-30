from django.db import models
from django.conf import settings
    
class Ticket(models.Model):
    
    class Status(models.TextChoices):
        OPEN = 'OPN', 'открыта'
        IN_PROGRESS = 'PRG', 'в рабооте'
        RESOLVED = 'RSL', 'решена'
        CLOSED = 'CLS', 'закрыта'
    
    title = models.CharField(max_length=255, verbose_name='Краткое описание')
    description = models.TextField(verbose_name="Детальное описание проблемы")
    
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='статус задачи'
    )

    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        verbose_name="Назначенный специалист"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE, 
        related_name="tickets", 
        verbose_name="Автор тикета"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

class Comment(models.Model):
    content = models.TextField(verbose_name='текст сообщения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="comments", 
        verbose_name="Автор комментария"
    )
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name="comments", 
        verbose_name="Связанный тикет"
    )
    
class Screenshot(models.Model):
    # file_path представлен через FileField/ImageField, либо CharField, если пишется чистый путь
    file_path = models.FileField(upload_to='tickets/screenshots/', verbose_name="Путь к файлу на сервере")

    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name="screenshots", 
        verbose_name="К какому тикету относится"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время загрузки")
