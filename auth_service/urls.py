from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tickets/", include("tickets.urls", namespace="tickets")),
    path("auth/", include("authentication.urls", namespace="authentication")),
    path("", include("django_prometheus.urls")),  # /metrics
]

