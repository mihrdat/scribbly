from django.db import transaction
from django.utils import timezone
from django.shortcuts import redirect
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordConfirmSerializer,
    TokenSerializer,
    ResendActivationSerializer,
    ActivationConfirmSerializer,
    DeactivateUserSerializer,
    ActivateUserSerializer,
    LoginSerializer,
    GoogleAuthSerializer,
    GoogleLoginOutputSerializer,
)
from .pagination import DefaultLimitOffsetPagination
from .email import PasswordResetEmail, ActivationEmail
from .utils import generate_random_code
from .constants import CacheTimeouts
from .services import GoogleLoginService

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    @action(methods=["GET", "PUT", "PATCH"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_current_user
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    @transaction.atomic
    @action(methods=["POST"], detail=False)
    def change_password(self, request, *args, **kwargs):
        user = self.get_current_user()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        # Log out user from other systems
        Token.objects.filter(user=user).delete()

        new_token = Token.objects.create(user=user)
        serializer = TokenSerializer(new_token)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        context = {"user": user}

        PasswordResetEmail(request, context).send(to=[user.email])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        user.set_password(serializer.validated_data["new_password"])
        user.last_login = timezone.now()
        user.save(update_fields=["password", "last_login"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        code = generate_random_code()
        cache.set(key=user.email, value=code, timeout=CacheTimeouts.WEEK)

        context = {"username": user.username, "code": code}
        ActivationEmail(request, context).send(to=[user.email])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    @action(methods=["POST"], detail=False)
    def activation_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        user.is_active = True
        user.save(update_fields=["is_active"])

        cache.delete(key=email)

        token = Token.objects.create(user=user)
        serializer = TokenSerializer(token)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(methods=["POST"], detail=True)
    def deactivate(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        context = self.get_serializer_context()
        context["user"] = user

        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        user.is_active = False
        user.set_unusable_password()
        user.save(update_fields=["is_active", "password"])

        Token.objects.filter(user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=True)
    def activate(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        context = self.get_serializer_context()
        context["user"] = user

        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_current_user(self):
        return self.request.user

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(pk=user.pk)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "me":
            if self.request.method in ["PUT", "PATCH"]:
                self.serializer_class = UserUpdateSerializer
        elif self.action == "create":
            self.serializer_class = UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            self.serializer_class = UserUpdateSerializer
        elif self.action == "change_password":
            self.serializer_class = ChangePasswordSerializer
        elif self.action == "reset_password":
            self.serializer_class = ResetPasswordSerializer
        elif self.action == "reset_password_confirm":
            self.serializer_class = ResetPasswordConfirmSerializer
        elif self.action == "resend_activation":
            self.serializer_class = ResendActivationSerializer
        elif self.action == "activation_confirm":
            self.serializer_class = ActivationConfirmSerializer
        elif self.action == "deactivate":
            self.serializer_class = DeactivateUserSerializer
        elif self.action == "activate":
            self.serializer_class = ActivateUserSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in [
            "create",
            "reset_password",
            "reset_password_confirm",
            "resend_activation",
            "activation_confirm",
        ]:
            self.permission_classes = [AllowAny]
        if self.action in ["deactivate", "activate"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleLoginRedirectApi(APIView):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleLoginService()
        authorization_url, state = google_login_flow.get_authorization_url()
        request.session["google_oauth2_state"] = state
        return redirect(authorization_url)


class GoogleLoginApi(APIView):
    @transaction.atomic
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

        email = user_info["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email, is_active=True)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        serializer = GoogleLoginOutputSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
