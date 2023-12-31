from django.urls import path
from users.views import GoogleLoginRedirectApi, GoogleLoginApi

urlpatterns = [
    path("google/redirect/", GoogleLoginRedirectApi.as_view(), name="google-redirect"),
    path("google/callback/", GoogleLoginApi.as_view(), name="google-callback"),
]
