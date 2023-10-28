from rest_framework_nested import routers
from .views import (
    AuthorViewSet,
    CategoryViewSet,
    ArticleViewSet,
    ArticleImageViewSet,
    ArticleLikeViewSet,
    CommentViewSet,
    CommentReplyViewSet,
)

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("categories", CategoryViewSet)
router.register("articles", ArticleViewSet)
router.register("comments", CommentViewSet)

articles_router = routers.NestedDefaultRouter(router, "articles", lookup="article")
articles_router.register("images", ArticleImageViewSet, basename="article-images")
articles_router.register("likes", ArticleLikeViewSet, basename="article-likes")

comments_router = routers.NestedDefaultRouter(router, "comments", lookup="comment")
comments_router.register("replies", CommentReplyViewSet, basename="comment-replies")

urlpatterns = router.urls + articles_router.urls + comments_router.urls
