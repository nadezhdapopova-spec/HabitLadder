from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from users.models import CustomUser


class RegisterAPIViewTests(APITestCase):

    @patch("users.serializers.send_activation_email.delay")
    def test_register_user(self, mock_send):
        """Проверяет регистрацию пользователя с тестовыми данными
        и что пользователь не активен до подтверждения регистрации"""
        url = reverse("users:user_register")

        data = {
            "email": "test@example.com",
            "username": "test",
            "password": "Qwerty123!",
            "password2": "Qwerty123!",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email="test@example.com").exists())

        user = CustomUser.objects.get(email="test@example.com")
        self.assertFalse(user.is_active)
        mock_send.assert_called_once()
