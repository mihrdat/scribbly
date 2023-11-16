from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserSerializer,
    GoogleAuthSerializer,
)
from .services import GoogleLoginService

User = get_user_model()


class GoogleLoginRedirectApi(APIView):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleLoginService()
        authorization_url, state = google_login_flow.get_authorization_url()
        request.session["google_oauth2_state"] = state
        return redirect(authorization_url)


class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        serializer = GoogleAuthSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get("code")
        state = serializer.validated_data.get("state")

        session_state = request.session.get("google_oauth2_state")

        if (session_state is None) or (state != session_state):
            return Response(
                {"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST
            )

        del request.session["google_oauth2_state"]

        service = GoogleLoginService()
        google_tokens = service.get_google_tokens(code=code)
        user_info = service.get_user_info(google_tokens=google_tokens)

        try:
            user = User.objects.get(email=user_info["email"])
        except User.DoesNotExist:
            user = (
                User.objects.create_user(
                    email=user_info["email"],
                    username=user_info["name"],
                    password=make_password(None),
                ),
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
