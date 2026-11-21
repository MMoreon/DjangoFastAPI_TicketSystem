from django.contrib import admin

from .models import Comment, Screenshot, Ticket

admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Screenshot)
