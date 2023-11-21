from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from .serializers import TokenSerializer, TokenCreateSerializer
from rest_framework.authtoken.models import Token

User = get_user_model()


class TokenCreateView(GenericAPIView):
    serializer_class = TokenCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        (token, created) = Token.objects.get_or_create(user=serializer.user)

        serializer = TokenSerializer(token)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TokenDestroyView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Token.objects.get(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
