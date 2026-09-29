from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Ticket, Comment, Screenshot


admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Screenshot)
