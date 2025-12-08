from django.urls import include, path

from rest_framework.routers import DefaultRouter

from habits.apps import HabitsConfig
from habits.views import HabitsViewSet

app_name = HabitsConfig.name

router = DefaultRouter()
router.register(r"habits", HabitsViewSet, basename="habits")

urlpatterns = [
    path("", include(router.urls)),
]
