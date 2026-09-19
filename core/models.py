from django.db import models

class User(models.Model):

    class Role(models.TextChoices):
        USER = 'USR', 'Пользователь'
        ADMIN = 'ADM', 'Администратор'
        SPECIALIS = 'SPC', 'Специалист'
    
    name = models.CharField(max_length=20, verbose_name="Имя пользователя")
    email = models.EmailField(max_length=254, unique=True)
    hashed_pass = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True, verbose_name="Флаг активности пользователя")
    
    role = models.CharField(
        max_length=3,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль в системе'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время регистрации")
    
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

    user = models.ForeignKey(
        User, 
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
        User, 
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
