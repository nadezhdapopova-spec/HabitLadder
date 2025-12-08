from django.urls import path

from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from users.apps import UsersConfig
from users.views import (
    CustomUserViewSet,
    RegisterAPIView, ActivationView,
)

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="user_register"),
    path("activate/<int:user_id>/<str:token>/", ActivationView.as_view(), name="activate"),
    path(
        "token/",
        TokenObtainPairView.as_view(permission_classes=[AllowAny]),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(
            permission_classes=[
                AllowAny,
            ]
        ),
        name="token_refresh",
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns += router.urls
