from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class CoursesAdmin(admin.ModelAdmin):
    """Добавляет привычки в админ-панель"""

    list_display = (
        "id",
        "user",
        "action",
        "place",
        "habit_time",
        "periodicity",
        "duration",
        "is_pleasant",
        "related_habit",
        "is_public",
        "created_at",
        "updated_at",
    )
    search_fields = ("id", "action")
