from django.contrib.auth.models import User
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from requests import Response
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from articles.models import Article, ReadArticle
from articles.serializers import ArticleSerializer, ReadArticleSerializer
from users.models import SubscriptionUser


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created", "updated"]
    filterset_fields = ["readarticle__is_read"]
    ordering = ["-created"]

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=ArticleSerializer,
    )
    def feed(self, request, *args, **kwargs):
        queryset = Article.objects.filter(user__authors__subscriber=self.request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=ArticleSerializer,
    )
    def feed_read(self, request, *args, **kwargs):
        queryset = Article.objects.filter(
            Q(user__authors__subscriber=self.request.user, readarticle__is_read=False)
            | Q(user__authors__subscriber=self.request.user, readarticle__is_read=None)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class ReadArticleViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ReadArticle.objects.all()
    serializer_class = ReadArticleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "article"

    def get_object(self):
        obj, _ = ReadArticle.objects.get_or_create(
            user=self.request.user, article_id=self.kwargs["article"]
        )
        return obj
