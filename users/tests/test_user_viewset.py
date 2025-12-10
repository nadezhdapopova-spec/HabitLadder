from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import CustomUser


class CustomUserViewSetTests(APITestCase):

    def setUp(self):
        """Формирует тестовые данные"""
        super().setUp()

        self.superuser = CustomUser.objects.create_superuser(
            email="admin@test.com", username="admin", password="admin123", is_active=True
        )
        self.user1 = CustomUser.objects.create_user(
            email="user1@example.com", username="user1", password="pass123", is_active=True
        )
        self.user2 = CustomUser.objects.create_user(
            email="user2@example.com", username="user2", password="pass123", is_active=True
        )
        self.user3 = CustomUser.objects.create_user(
            email="user3@example.com", username="user3", password="pass123", is_active=True
        )
        self.stranger = CustomUser.objects.create_user(
            email="stranger@test.com", username="stranger", password="str123", is_active=True
        )

        self.client_super = APIClient()
        self.client_super.force_authenticate(user=self.superuser)

        self.client_user1 = APIClient()
        self.client_user1.force_authenticate(user=self.user1)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)

    def test_list_public_serializer_authenticated(self):
        """Проверяет, что авторизованному пользователю возвращается список публичных профилей пользователей"""
        url = reverse("users:users-list")
        response = self.client_stranger.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        users_list = response.data.get("results", response.data)

        self.assertIn("username", users_list[0])
        self.assertNotIn("password", users_list[0])

    def test_list_public_serializer_unauthenticated(self):
        """Проверяет, что неавторизованному пользователю не возвращается список публичных профилей пользователей"""
        url = reverse("users:users-list")
        client = APIClient()
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_superuser(self):
        """Проверяет, что суперпользователю возвращается список полных профилей пользователей"""
        url = reverse("users:users-list")
        response = self.client_super.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        users_list = response.data.get("results", response.data)
        self.assertIn("email", users_list[0])

    def test_retrieve_self_full_serializer(self):
        """Проверяет, что пользователь может просматривать свой полный профиль"""
        url = reverse("users:users-detail", args=[self.user1.id])
        response = self.client_user1.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertIn("email", data)

    def test_retrieve_superuser_full_serializer(self):
        """Проверяет, что суперпользователь может просматривать любые полные профили пользователей"""
        url = reverse("users:users-detail", args=[self.user1.id])
        response = self.client_super.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertIn("email", data)

    def test_retrieve_stranger_public_serializer(self):
        """Проверяет, что авторизованный пользователь может просматривать публичные профили пользователей"""
        url = reverse("users:users-detail", args=[self.user1.id])
        response = self.client_stranger.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertIn("username", data)
        self.assertNotIn("email", data)

    def test_retrieve_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь не может просматривать профили пользователей"""
        url = reverse("users:users-detail", args=[self.user1.id])
        client = APIClient()
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_self_allowed(self):
        """Проверяет, что пользователь может изменять свой профиль"""
        url = reverse("users:users-detail", args=[self.user1.id])

        response = self.client_user1.patch(url, {"email": "newmail@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_superuser_allowed(self):
        """Проверяет, что суперпользователь может изменять профили пользователей"""
        url = reverse("users:users-detail", args=[self.user1.id])

        response = self.client_super.patch(url, {"email": "newmail@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_forbidden(self):
        """Проверяет, что авторизованный пользователь не может изменять чужие профили"""
        url = reverse("users:users-detail", args=[self.user1.id])
        response = self.client_stranger.patch(url, {"email": "hack@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_self_allowed(self):
        """Проверяет, что пользователь может удалить свой профиль"""
        url = reverse("users:users-detail", args=[self.user1.id])
        response = self.client_user1.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(id=self.user1.id).exists())

    def test_delete_superuser_allowed(self):
        """Проверяет, что суперпользователь может удалить любой профиль пользователей"""
        url = reverse("users:users-detail", args=[self.user2.id])
        response = self.client_super.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(id=self.user2.id).exists())

    def test_delete_other_forbidden(self):
        """Проверяет, что авторизованный пользователь не может удалить чужой профиль"""
        url = reverse("users:users-detail", args=[self.user3.id])
        response = self.client_stranger.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
