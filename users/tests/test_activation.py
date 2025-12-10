from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


class ActivationViewTests(APITestCase):

    def setUp(self):
        """Формирует тестовые данные для авторизации пользователя"""
        self.user = CustomUser.objects.create(email="test@example.com", is_active=False)

    def test_activation_success(self):
        """Проверяет, что пользователь активен после подтверждения регистрации"""
        token = default_token_generator.make_token(self.user)
        url = reverse("users:activate", args=[self.user.id, token])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activation_wrong_token(self):
        """Проверяет активацию пользователя при указании некорректного токена"""
        url = reverse("users:activate", args=[self.user.id, "wrong-token"])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("detail"), "Неверный токен")

    def test_activation_user_not_found(self):
        """Проверяет активацию пользователя, незарегистрированного в системе"""
        url = reverse("users:activate", args=[9999, "token"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
