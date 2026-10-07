from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from .services import send_ticket_update_to_queue

from .models import (
    Comment,
    Screenshot,
    Ticket
    )
from .serializers import (
    CommentSerializer,
    ScreenshotSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    UserConfirmTicketSerializer,
    SpecialistUpdateTicketSerializer
    )
from .permissions import IsTicketAuthorOrStaff


class UserTicketListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TicketCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADM':
            return Ticket.objects.all().order_by('-created_at')
        
        if user.role == 'SPC':
            return Ticket.objects.filter(
                Q(status=Ticket.Status.OPEN) | Q(specialist=user)
            ).order_by('-created_at')
        
        return Ticket.objects.filter(user=user).order_by('-created_at')
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserTicketDetailView(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    permission_classes = (IsAuthenticated, IsTicketAuthorOrStaff)
    serializer_class = TicketCreateSerializer
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TicketDetailSerializer
        return TicketCreateSerializer


class UserConfirmTicketView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    permission_classes = (IsAuthenticated, IsTicketAuthorOrStaff)
    serializer_class = UserConfirmTicketSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        # PATCH запрос
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class SpecialistUpdateTicketView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    permission_classes = (IsAuthenticated, IsTicketAuthorOrStaff)
    serializer_class = SpecialistUpdateTicketSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        # записывает спеца в тикет
        if self.get_object().status == Ticket.Status.OPEN:
            ticket = serializer.save(specialist=self.request.user, status=Ticket.Status.IN_PROGRESS)
            
            send_ticket_update_to_queue(
            ticket_id=ticket.id,
            title=ticket.title,
            status=ticket.status,
            client_email=ticket.user.email,

            specialist_name=ticket.specialist.name, 
            specialist_email=ticket.specialist.email
        )
        
        else:
            ticket = serializer.save()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
class TicketCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsTicketAuthorOrStaff)

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return Comment.objects.filter(ticket_id=ticket_id).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class TicketScreenshotListCreateView(generics.ListCreateAPIView):
    serializer_class = ScreenshotSerializer
    permission_classes = (IsAuthenticated, IsTicketAuthorOrStaff)
    parser_classes = (MultiPartParser, FormParser)  # Включаем поддержку загрузки файлов

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return Screenshot.objects.filter(ticket_id=ticket_id).order_by('-uploaded_at')

    def perform_create(self, serializer):
        serializer.save()