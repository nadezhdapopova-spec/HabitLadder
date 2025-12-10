from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit
from habits.paginators import HabitsPaginator
from habits.serializers import HabitsSerializer
from users.permissions import IsOwner


class HabitsViewSet(viewsets.ModelViewSet):
    """Вьюсет привычки"""

    queryset = Habit.objects.all()
    serializer_class = HabitsSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["periodicity", "habit_time"]
    pagination_class = HabitsPaginator

    def get_queryset(self):
        """
        Возвращает только привычки текущего пользователя.
        Суперпользователь видит все привычки
        """
        user = self.request.user
        if user.is_superuser:
            return Habit.objects.all()
        if user.is_authenticated:
            return Habit.objects.filter(Q(user=user) | Q(is_public=True))
        return Habit.objects.none()

    @action(detail=False, methods=["get"], url_path="public", permission_classes=[IsAuthenticated])
    def public_habits(self, request):
        """Возвращает список публичных привычек всех пользователей для авторизованных пользователей"""

        queryset = Habit.objects.filter(is_public=True).order_by("action", "habit_time", "place")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HabitsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = HabitsSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def perform_create(self, serializer):
        """При создании привычки устанавливает пользователя как владельца"""

        serializer.save(user=self.request.user)

    def get_permissions(self):
        """Определяет права на действия с привычками для разных уровней пользователей:
        - авторизованный суперпользователь - все права;
        - авторизованный пользователь - просмотр списка публичных привычек, создание своих привычек;
        - авторизованный владелец - просмотр, изменение, удаление своих привычек;
        """

        if self.request.user.is_superuser:
            return []
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]
