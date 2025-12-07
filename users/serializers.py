from rest_framework import serializers

from users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "phone_number", "city", "avatar")

    def create(self, validated_data):
        """Создает объект пользователя"""

        return CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            is_active=True,
        )


class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного профиля пользователя"""

    # public_habits = HabitSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "city", "avatar")


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для полного профиля пользователя"""

    # habits = HabitSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "city", "phone_number", "avatar")
