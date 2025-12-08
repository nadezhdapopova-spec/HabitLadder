from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitsValidator


class HabitsSerializer(serializers.ModelSerializer):
    """Сериализатор привычек"""

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)
        validators = [HabitsValidator()]
