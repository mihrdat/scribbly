from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register("users", views.UserViewSet)

urlpatterns = [
    *router.urls,
    path("token/login/", views.TokenCreateView.as_view(), name="login"),
    path("token/logout/", views.TokenDestroyView.as_view(), name="logout"),
]
