from django.urls import include, path
from rest_framework.routers import SimpleRouter

from articles.views import ArticleViewSet, ReadArticleViewSet

router = SimpleRouter()

router.register("", ArticleViewSet, basename="articles")
router.register("read_articles", ReadArticleViewSet)

urlpatterns = [
    path("", include(router.urls))
]
