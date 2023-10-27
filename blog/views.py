from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models.aggregates import Count

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Author, Category, Article, ArticleImage, ArticleLike, Comment
from .serializers import (
    AuthorSerializer,
    CategorySerializer,
    ArticleSerializer,
    ArticleCreateUpdateSerializer,
    ArticleImageSerializer,
    ArticleLikeSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .pagination import DefaultLimitOffsetPagination


class AuthorViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Author.objects.select_related("user").all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=current_user)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(articles_count=Count("articles")).all()
    serializer_class = CategorySerializer
    pagination_class = DefaultLimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]


class ArticleViewSet(ModelViewSet):
    queryset = (
        Article.objects.select_related("category").prefetch_related("images").all()
    )
    serializer_class = ArticleSerializer
    pagination_class = DefaultLimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, permission_classes=[IsAuthenticated])
    def comments(self, request, *args, **kwargs):
        article_id = self.kwargs["pk"]
        self.queryset = Comment.objects.filter(article_id=article_id, reply_to=None)
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "comments":
            self.serializer_class = CommentSerializer
        if self.action in ["create", "update", "partial_update"]:
            self.serializer_class = ArticleCreateUpdateSerializer
        return super().get_serializer_class()


class ArticleImageViewSet(ModelViewSet):
    queryset = ArticleImage.objects.all()
    serializer_class = ArticleImageSerializer
    pagination_class = DefaultLimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["article_id"] = self.kwargs["article_pk"]
        return context

    def get_queryset(self):
        return super().get_queryset().filter(article_id=self.kwargs["article_pk"])


class ArticleLikeViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = ArticleLike.objects.select_related("author").all()
    serializer_class = ArticleLikeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(article_id=self.kwargs["article_pk"]).all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["article_id"] = self.kwargs["article_pk"]
        return context

    @transaction.atomic
    def perform_create(self, serializer):
        article = get_object_or_404(Article, pk=self.kwargs["article_pk"])
        article.likes_count += 1
        article.save(update_fields=["likes_count"])
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        article = self.get_object().article
        article.likes_count -= 1
        article.save(update_fields=["likes_count"])
        return super().perform_destroy(instance)


class CommentViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    queryset = Comment.objects.select_related("author").all()
    serializer_class = CommentSerializer
    pagination_class = DefaultLimitOffsetPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = CommentCreateSerializer
        if self.action in ["update", "partial_update"]:
            self.serializer_class = CommentUpdateSerializer
        return super().get_serializer_class()

    @transaction.atomic
    def perform_create(self, serializer):
        article = serializer.validated_data["article"]
        article.comments_count += 1
        article.save(update_fields=["comments_count"])
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        article = self.get_object().article
        article.comments_count -= 1
        article.save(update_fields=["comments_count"])
        return super().perform_destroy(instance)
