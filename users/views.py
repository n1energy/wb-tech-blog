from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import SubscriptionUser
from users.serializers import (
    RegistrationSerializer,
    SubscriptionUserSerializer,
    UserFollowingSerializer,
    UserSerializer,
    UserTokenObtainPairSerializer,
)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().annotate(num_articles=Count("article"))
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter]

    def get_object(self):
        pk = self.kwargs.get("pk")

        if pk == "current":
            return self.request.user

        return super(UsersViewSet, self).get_object()

    # @action(detail=True)#, permission_classes=[IsAuthenticated])
    # def Subscribe(self, request, *args, **kwargs):
    #     serializer = SubscriptionUserSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)
    @action(
        detail=True,
        methods=["POST"],
        serializer_class=SubscriptionUserSerializer,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        queryset = User.objects.filter(pk=self.kwargs["pk"])
        if queryset:
            serializer = SubscriptionUserSerializer(
                data=dict(subscriber=self.kwargs["pk"], user=request.user.id),
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "This pk is not valid!"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["POST"], serializer_class=UserFollowingSerializer)
    def sub(self, request, *args, **kwargs):
        request.data["user"] = self.kwargs["pk"]
        request.data["subscriber"] = self.request.user
        serializer = UserFollowingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    # def perform_create(self, serializer):
    #     serializer.save(subscriber=self.request.user)


class UserFollowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserFollowingSerializer
    queryset = SubscriptionUser.objects.all()

    # @action(detail=True, methods=["POST"])
    # def suby(self, request, *args, **kwargs):
    #     # serializer = UserFollowingSerializer(data=dict(subscriber=self.kwargs['pk'], user=request.user.id),
    #     #                                context={'request': request},
    #     #                                partial=True)
    #     serializer = UserFollowingSerializer(data=request.data)
    #     request.data["user"] = request.user.id
    #     request.data["subscriber"] = kwargs['pk']
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     return Response(
    #         data=serializer.data,
    #         status=status.HTTP_201_CREATED
    # )

    def create(self, request, *args, **kwargs):
        request_data = request.data
        # request_data["user"] = self.kwargs['pk']
        request_data["subscriber"] = request.user.id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(subscriber=self.request.user)

    # def perform_create(self, serializer):
    #     serializer.validated_data['subscriber'] = self.request.user
    #     serializer.save()


class UsersAPIView(APIView):
    def get(self, request):
        users = User.objects.all().annotate(num_articles=Count("article"))
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
