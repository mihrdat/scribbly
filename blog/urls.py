from rest_framework_nested import routers
from .views import (
    AuthorViewSet,
    CategoryViewSet,
    ArticleViewSet,
    ArticleImageViewSet,
    ArticleLikeViewSet,
)

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("categories", CategoryViewSet)
router.register("articles", ArticleViewSet)

articles_router = routers.NestedDefaultRouter(router, "articles", lookup="article")
articles_router.register("images", ArticleImageViewSet, basename="article-images")
articles_router.register("likes", ArticleLikeViewSet, basename="article-likes")

urlpatterns = router.urls + articles_router.urls
