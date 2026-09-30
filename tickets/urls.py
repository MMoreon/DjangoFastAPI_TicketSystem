from django.urls import path
from .views import SpecialistUpdateTicketView, TicketCommentListCreateView, UserTicketListCreateView, UserTicketDetailView, UserConfirmTicketView

app_name = 'tickets'

urlpatterns = [
    # Создать тикет / Посмотреть свои тикеты
    path('', UserTicketListCreateView.as_view(), name='ticket_list_create'),
    path('<int:id>/', UserTicketDetailView.as_view(), name='ticket_detail'),
    path('<int:id>/confirm/', UserConfirmTicketView.as_view(), name='ticket_confirm'),
    
    path('<int:id>/spec/', SpecialistUpdateTicketView.as_view(), name='spec_ticket_update'),

    path('<int:ticket_id>/comments/', TicketCommentListCreateView.as_view(), name='ticket_comments'),
]
