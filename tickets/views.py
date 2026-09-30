from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Ticket
from .serializers import TicketCreateSerializer, UserConfirmTicketSerializer, SpecialistUpdateTicketSerializer
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
            serializer.save(specialist=self.request.user, status=Ticket.Status.IN_PROGRESS)
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)