from django.contrib import admin
from .models import User, Ticket, Comment, Screenshot

admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Screenshot)
