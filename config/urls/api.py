from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("auth/", include("users.urls.token")),
    path("auth/", include("users.urls.google")),
    path("blog/", include("blog.urls")),
    path("chat/", include("chat.urls")),
]
