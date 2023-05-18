from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import SubscriptionUser
from users.serializers import (SubscriptionUserSerializer,
                               UserFollowingSerializer, UserSerializer,
                               UserTokenObtainPairSerializer)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().annotate(num_articles=Count("article"))
    serializer_class = UserSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["num_articles"]

    def get_object(self):
        pk = self.kwargs.get("pk")
        if pk == "current":
            return self.request.user
        return super(UsersViewSet, self).get_object()


class UserFollowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = SubscriptionUserSerializer
    queryset = SubscriptionUser.objects.all()

    def perform_create(self, serializer):
        try:
            serializer.save(subscriber=self.request.user)
        except IntegrityError:
            raise ValidationError('This subscription is already exists.')


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
