from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from habits.models import Habit
from users.models import CustomUser


class CustomUserViewSetTests(APITestCase):

    def setUp(self):
        """Формирует тестовые данные"""
        super().setUp()

        self.superuser = CustomUser.objects.create_superuser(
            email="admin@test.com",
            username="admin",
            password="admin123",
            is_active=True
        )
        self.user1 = CustomUser.objects.create_user(
            email="user1@example.com",
            username="user1",
            password="pass123",
            is_active=True
        )
        self.stranger = CustomUser.objects.create_user(
            email="stranger@test.com",
            username="stranger",
            password="str123",
            is_active=True
        )

        self.client_super = APIClient()
        self.client_super.force_authenticate(user=self.superuser)

        self.client_user1 = APIClient()
        self.client_user1.force_authenticate(user=self.user1)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)

        self.habit1 = Habit.objects.create(
            user=self.user1,
            action="test_action1",
            place="test_place1",
            habit_time="09:00",
            reward="test_reward1",
            is_public=True
        )
        self.habit2 = Habit.objects.create(
            user=self.user1,
            action="test_action2",
            place="test_place2",
            habit_time="10:00",
            reward="test_reward2"
        )
        self.habit3 = Habit.objects.create(
            user=self.user1,
            action="test_action3",
            place="test_place3",
            habit_time="11:00",
            reward="test_reward3"
        )
        self.habit4 = Habit.objects.create(
            user=self.user1,
            action="test_action4",
            place="test_place4",
            habit_time="12:00",
            reward="test_reward4"
        )

    def test_list_public_habits_authenticated(self):
        url = reverse("habits:habits-list")
        response = self.client_stranger.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habits_list = response.data.get("results", response.data)
        public_actions = [habit["action"] for habit in habits_list]

        for habit in habits_list:
            self.assertTrue(habit.get("is_public", False), "Найдена приватная привычка в списке!")
        self.assertIn("test_action1", public_actions)
        self.assertNotIn("test_action2", public_actions)

    def test_list_public_habits_unauthenticated(self):
        url = reverse("habits:habits-list")
        client = APIClient()
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_all_habits_superuser(self):
        url = reverse("habits:habits-list")
        response = self.client_super.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habits_list = response.data.get("results", response.data)
        habits_count = Habit.objects.all().count()
        self.assertIn("action", habits_list[0])
        self.assertEqual(len(habits_list), habits_count)

    def test_list_self_habits(self):
        url = reverse("habits:habits-list")
        response = self.client_user1.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habits_list = response.data.get("results", response.data)
        actions = [habit["action"] for habit in habits_list]
        self.assertIn("test_action1", actions)
        self.assertIn("test_action2", actions)

    def test_retrieve_self(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])
        response = self.client_user1.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        assert data.get("action") == "test_action1"

    def test_retrieve_superuser(self):
        url = reverse("habits:habits-detail", args=[self.habit2.id])
        response = self.client_super.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        assert data.get("action") == "test_action2"

    def test_retrieve_stranger(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])
        response = self.client_stranger.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_unauthenticated(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])
        client = APIClient()
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated(self):
        """Проверяет, что авторизованный пользователь может создавать привычку"""
        url = reverse("habits:habits-list")
        data = {
            "action": "test_action5",
            "place": "test_place5",
            "habit_time": "13:00",
            "reward": "test_reward5"
        }
        response = self.client_user1.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Habit.objects.filter(action="test_action5").exists())

    def test_create_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь не может создавать привычку"""
        url = reverse("habits:habits-list")
        data = {
            "action": "test_action6",
            "place": "test_place6",
            "habit_time": "13:30",
            "reward": "test_reward6"
        }
        client = APIClient()
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_superuser(self):
        """Проверяет, что суперпользователь может создавать привычку"""
        url = reverse("habits:habits-list")
        data = {
            "action": "test_action7",
            "place": "test_place7",
            "habit_time": "14:00",
            "reward": "test_reward7"
        }
        response = self.client_super.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Habit.objects.filter(reward="test_reward7").exists())

    def test_update_self_allowed(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])

        response = self.client_user1.patch(url, {"place": "test_place100", "reward": "test_reward2"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Habit.objects.filter(place="test_place100").exists())

    def test_update_superuser_allowed(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])

        response = self.client_super.patch(url, {"place": "test_place10", "reward": "test_reward2"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Habit.objects.filter(place="test_place10").exists())

    def test_update_other_forbidden(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])
        response = self.client_stranger.patch(url, {"place": "test_place1", "reward": "test_reward2"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь не может изменять привычку"""
        url = reverse("habits:habits-detail", args=[self.habit1.id])
        client = APIClient()
        response = client.patch(url, {"place": "test_place1", "reward": "test_reward2"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_self_allowed(self):
        url = reverse("habits:habits-detail", args=[self.habit1.id])
        response = self.client_user1.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit1.id).exists())

    def test_delete_superuser_allowed(self):
        url = reverse("habits:habits-detail", args=[self.habit2.id])
        response = self.client_super.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit2.id).exists())

    def test_delete_other_forbidden(self):
        url = reverse("habits:habits-detail", args=[self.habit3.id])
        response = self.client_stranger.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_unauthenticated(self):
        url = reverse("habits:habits-detail", args=[self.habit4.id])
        client = APIClient()
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
