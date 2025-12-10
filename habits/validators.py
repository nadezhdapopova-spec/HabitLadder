from rest_framework import serializers


class HabitsValidator:
    """Класс-валидатор привычек"""

    def validate_reward(self, attrs):
        """Проверяет, что заполнено только одно поле из двух - или вознаграждение, или связанная привычка"""
        if bool(attrs.get("reward")) == bool(attrs.get("related_habit")):
            raise serializers.ValidationError("Нельзя указывать и вознаграждение, и связанную привычку одновременно")

    def validate_related_habit(self, attrs):
        """Проверяет, что связанная привычка является приятной"""
        related = attrs.get("related_habit")
        if related and not related.is_pleasant:
            raise serializers.ValidationError("Связанная привычка должна быть приятной")

    def validate_pleasant_habit(self, attrs):
        """Проверяет, что приятная привычка не имеет вознаграждение или связанную привычку"""
        if bool(attrs.get("is_pleasant")):
            if attrs.get("reward") or attrs.get("related_habit"):
                raise serializers.ValidationError(
                    "Приятная привычка не может иметь вознаграждение или связанную привычку"
                )

    def validate_habit_duration(self, attrs):
        """Проверяет, что время выполнения действия не превышает 120 секунд"""
        time_success = attrs.get("time_success")
        if time_success and time_success > 120:
            raise serializers.ValidationError("Время выполнения не должно превышать 120 секунд")

    def validate_habit_periodicity(self, attrs):
        """Проверяет, что периодичность выполнения привычки от 1 до 7 дней"""
        periodicity = attrs.get("periodicity")
        if periodicity and not (1 <= periodicity <= 7):
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней")

    def __call__(self, attrs):
        """Вызывает все валидаторы"""
        self.validate_reward(attrs)
        self.validate_related_habit(attrs)
        self.validate_pleasant_habit(attrs)
        self.validate_habit_duration(attrs)
        self.validate_habit_periodicity(attrs)
        return attrs
