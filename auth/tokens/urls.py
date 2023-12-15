from django.urls import path
from . import views

urlpatterns = [
    path("token/login/", views.LoginView.as_view(), name="login"),
    path("token/logout/", views.LogoutView.as_view(), name="logout"),
]
