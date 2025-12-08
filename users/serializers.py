from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from users.models import CustomUser
from users.tasks import send_activation_email


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "phone_number", "city", "avatar")

    def create(self, validated_data):
        """Создает объект пользователя"""

        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            is_active=False,
        )
        token = default_token_generator.make_token(user)
        activation_link = reverse("users:activate", args=[user.pk, token])
        send_activation_email.delay(user.email, activation_link)

        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного профиля пользователя"""

    pleasant_public_habits = serializers.SerializerMethodField()
    useful_public_habits = serializers.SerializerMethodField()

    @staticmethod
    def get_pleasant_public_habits(user):
        """Возвращает список публичных приятных привычек для публичного профиля пользователя"""
        habits = user.habits.filter(is_pleasant=True, is_public=True)
        return [str(h) for h in habits]

    @staticmethod
    def get_useful_public_habits(user):
        """Возвращает список публичных полезных привычек для публичного профиля пользователя"""
        habits = user.habits.filter(is_pleasant=False, is_public=True)
        return [str(h) for h in habits]

    class Meta:
        model = CustomUser
        fields = ("id", "username", "city", "avatar", "pleasant_public_habits", "useful_public_habits")


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для полного профиля пользователя"""

    pleasant_habits = serializers.SerializerMethodField()
    useful_habits = serializers.SerializerMethodField()

    @staticmethod
    def get_pleasant_public_habits(user):
        """Возвращает список приятных привычек для профиля пользователя"""
        habits = user.habits.filter(is_pleasant=True)
        return [str(h) for h in habits]

    @staticmethod
    def get_useful_public_habits(user):
        """Возвращает список полезных привычек для профиля пользователя"""
        habits = user.habits.filter(is_pleasant=False)
        return [str(h) for h in habits]

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "city", "phone_number", "avatar", "pleasant_habits", "useful_habits")
