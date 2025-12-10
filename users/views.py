from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from users.permissions import IsProfileOwner
from users.serializers import (
    CustomUserSerializer,
    PublicUserSerializer,
    RegisterSerializer,
)

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    """Представление для регистрации пользователя"""

    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [
        AllowAny,
    ]
    authentication_classes = []


class ActivationView(APIView):
    """Подтверждение email, активация аккаунта пользователя после регистрации"""

    permission_classes = [AllowAny]

    def get(self, request, user_id, token):
        """Активирует аккаунт пользователя по email после регистрации"""
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({"detail": "Пользователь не найден"}, status=404)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Аккаунт активирован"}, status=200)

        return Response({"detail": "Неверный токен"}, status=400)


class CustomUserViewSet(viewsets.ModelViewSet):
    """Представление для модели пользователя"""

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    filter_backends = [OrderingFilter]
    ordering_fields = ("id",)
    permission_classes = [
        IsAuthenticated,
    ]

    def get_serializer_class(self):
        """
        Возвращает публичный или полный сериализатор в зависимости от прав пользователя:
        если пользователь владелец - полный сериализатор, если нет - публичный
        """

        if self.action == "retrieve":
            user = self.get_object()
            if self.request.user.is_superuser or user.id == self.request.user.id:
                return CustomUserSerializer
            return PublicUserSerializer

        if self.action in ["update", "partial_update"]:
            return CustomUserSerializer

        if self.action == "list":
            if self.request.user.is_superuser:
                return CustomUserSerializer
            return PublicUserSerializer

        return CustomUserSerializer

    def get_permissions(self):
        """
        Определяет права владельца профиля на изменение и удаление своего профиля, если владелец авторизован.
        Остальные действия доступны для всех авторизованных пользователей
        """
        if self.request.user.is_superuser:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProfileOwner()]
        return [IsAuthenticated()]
