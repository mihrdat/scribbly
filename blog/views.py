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
    SimpleCommentSerializer,
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

    def get_queryset(self):
        if self.action == "comments":
            return Comment.objects.select_related("author").filter(
                article_id=self.kwargs["pk"], parent=None
            )
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "comments":
            self.serializer_class = CommentSerializer
        if self.action in ["create", "update", "partial_update"]:
            self.serializer_class = ArticleCreateUpdateSerializer
        return super().get_serializer_class()

    @action(detail=True, permission_classes=[IsAuthenticated])
    def comments(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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


class CommentViewSet(ModelViewSet):
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


class CommentReplyViewSet(ModelViewSet):
    queryset = Comment.objects.select_related("author").all()
    serializer_class = SimpleCommentSerializer
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(parent=self.kwargs["comment_pk"])

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            self.serializer_class = CommentReplySerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        parent_id = self.kwargs["comment_pk"]
        article = Comment.objects.get(pk=parent_id).article
        context["article"] = article
        context["parent_id"] = parent_id
        return context
