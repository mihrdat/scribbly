from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("auth/", include("auth.tokens.urls")),
    path("auth/", include("auth.Oauth.google.urls")),
    path("blog/", include("blog.urls")),
    path("chat/", include("chat.urls")),
]
