from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User
from tickets.models import Ticket

class TicketBusinessLogicTests(APITestCase):

    def setUp(self):
        self.client_user = User.objects.create_user(
            email="client@example.com", name="Клиент", password="password123", role="USR"
        )
        self.spec_user = User.objects.create_user(
            email="spec@example.com", name="Спец", password="password123", role="SPC"
        )
        
        self.client_ticket = Ticket.objects.create(
            title="Сломался ПК",
            description="Не включается монитор",
            user=self.client_user,
            status=Ticket.Status.OPEN
        )
        
        self.list_url = reverse('tickets:ticket_list_create')
        self.detail_url = reverse('tickets:ticket_detail', kwargs={'id': self.client_ticket.id})

    def test_client_can_see_only_their_tickets(self):
        other_user = User.objects.create_user(
            email="other@example.com", name="Чужой", password="password123", role="USR"
        )
        Ticket.objects.create(title="Чужая проблема", description="...", user=other_user)

        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Сломался ПК")

    def test_specialist_can_see_open_tickets(self):
        self.client.force_authenticate(user=self.spec_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_cannot_access_tickets(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
