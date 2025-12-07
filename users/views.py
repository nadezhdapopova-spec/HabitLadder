from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import CustomUser
from users.permissions import IsProfileOwner
from users.serializers import (
    CustomUserSerializer,
    PublicUserSerializer,
    RegisterSerializer,
)


class RegisterAPIView(CreateAPIView):
    """Представление для регистрации пользователя"""

    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [
        AllowAny,
    ]
    authentication_classes = []


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
            if user.id != self.request.user.id:
                return PublicUserSerializer
            return CustomUserSerializer

        if self.action in ["update", "partial_update"]:
            return CustomUserSerializer

        if self.action == "list":
            return PublicUserSerializer

        return CustomUserSerializer

    def get_permissions(self):
        """
        Определяет права владельца профиля на изменение и удаление своего профиля, если владелец авторизован.
        Остальные действия доступны для всех авторизованных пользователей
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProfileOwner()]
        return [IsAuthenticated()]
