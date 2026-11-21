from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from auth_service import settings
from tickets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tickets/', include('tickets.urls', namespace='tickets')),
    path('auth/', include('authentication.urls', namespace='authentication')),
    path('', include('django_prometheus.urls'))  # /metrics
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)