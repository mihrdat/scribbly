from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count

from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Author, Category, Article, ArticleImage, ArticleLike, Comment
from .serializers import (
    AuthorSerializer,
    CategorySerializer,
    ArticleSerializer,
    ArticleCreateUpdateSerializer,
    ArticleImageSerializer,
    ArticleLikeSerializer,
    CommentSerializer,
    CommentReplyCreateSerializer,
    CommentReplySerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .pagination import DefaultLimitOffsetPagination


class AuthorViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Author.objects.select_related("user").all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=["GET", "PUT", "PATCH"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_current_author
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    def get_current_author(self):
        return self.request.user.author


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

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(comments_count=Count("comments", distinct=True))
            .annotate(likes_count=Count("likes", distinct=True))
        )

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

    def get_queryset(self):
        return super().get_queryset().filter(article_id=self.kwargs["article_pk"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["article_id"] = self.kwargs["article_pk"]
        return context


class ArticleLikeViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = ArticleLike.objects.select_related("author").all()
    serializer_class = ArticleLikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(article_id=self.kwargs["article_pk"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["article_id"] = self.kwargs["article_pk"]
        return context

    @action(methods=["DELETE"], detail=False)
    def dislike(self, request, *args, **kwargs):
        get_object_or_404(
            ArticleLike,
            article_id=self.kwargs.get("article_pk"),
            author=self.request.user.author,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    queryset = (
        Comment.objects.select_related("author__user")
        .select_related("reply_to__user")
        .annotate(replies_count=Count("replies"))
    )
    serializer_class = CommentSerializer
    pagination_class = DefaultLimitOffsetPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "retrieve":
            return queryset.filter(article_id=self.kwargs["article_pk"])
        if self.action == "replies":
            return queryset.filter(parent=self.kwargs["pk"]).order_by("created_at")

        return queryset.filter(article_id=self.kwargs["article_pk"], parent=None)

    def get_serializer_class(self):
        if self.action == "replies":
            if self.request.method == "POST":
                self.serializer_class = CommentReplyCreateSerializer
            elif self.request.method == "GET":
                self.serializer_class = CommentReplySerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["article_id"] = self.kwargs["article_pk"]

        if self.action == "replies":
            context["parent_id"] = self.kwargs["pk"]

        return context

    @action(methods=["GET", "POST"], detail=True)
    def replies(self, request, *args, **kwargs):
        if request.method == "POST":
            return self.create(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
