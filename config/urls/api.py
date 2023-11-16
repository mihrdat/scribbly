from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("auth/", include("config.urls.jwt")),
    path("auth/", include("Oauth.google.urls")),
    path("blog/", include("blog.urls")),
]
