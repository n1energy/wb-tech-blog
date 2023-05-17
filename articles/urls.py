from django.urls import include, path
from rest_framework.routers import DefaultRouter

from articles.views import ArticleViewSet, ReadArticleViewSet

router = DefaultRouter()

router.register("", ArticleViewSet, basename="articles")
router.register("read_articles", ReadArticleViewSet)

urlpatterns = [path("", include(router.urls))]
