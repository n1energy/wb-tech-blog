from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import SubscriptionUser


class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionUser
        fields = ("id", "subscriber")


class SubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionUser
        fields = ("id", "user")


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=150,min_length=5, write_only=True)
    email = serializers.EmailField(max_length=20, min_length=6)
    username = serializers.CharField(max_length=20, min_length=3)
    num_articles = serializers.IntegerField(read_only=True)
    authors = serializers.SerializerMethodField()
    subscribers = serializers.SerializerMethodField()

    def get_authors(self, obj):
        return AuthorsSerializer(obj.authors.all(), many=True).data

    def get_subscribers(self, obj):
        return SubscribersSerializer(obj.subscribers.all(), many=True).data

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "num_articles",
            "authors",
            "subscribers",
        )

    def validate(self, args):
        email = args.get("email", None)
        username = args.get("username", None)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": ("email already exists")})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": ("username already exists")})

        return super().validate(args)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        return token


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50, min_length=6)
    username = serializers.CharField(max_length=50, min_length=3)
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "username", "password")

    def validate(self, args):
        email = args.get("email", None)
        username = args.get("username", None)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": ("user with this email already exists")}
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": ("user with this username already exists")}
            )

        return super().validate(args)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SubscriptionUserSerializer(serializers.ModelSerializer):
    # user = serializers.IntegerField(source='user.id')
    # subscriber = serializers.IntegerField(source='subscriber.id', read_only=True)

    class Meta:
        model = SubscriptionUser
        read_only_fields = ["subscriber"]
        fields = ["user", "subscriber"]

    def validate(self, args):
        user = args.get('user', None)
        subscriber = args.get('subscriber', None)
        if user == subscriber:
            raise serializers.ValidationError({'error': ('cant subscribe to yourself')})
        if SubscriptionUser.objects.filter(user=user, subscriber=subscriber).exists():
            raise serializers.ValidationError({'error': ('already subscribed')})
        return super().validate(args)

    # def create(self, validated_data):
    #     return SubscribtionUser.objects.create_user(**validated_data)


class UserFollowingSerializer(serializers.ModelSerializer):
    # subscriber = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    # subscriber = serializers.CharField(source='subscriber.username', read_only=True)
    # user = serializers.CharField(source='user.username')

    # user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = SubscriptionUser
        fields = ["id", "user", "subscriber"]
        read_only_fields = ["subscriber"]
        validators = [
            UniqueTogetherValidator(
                queryset=SubscriptionUser.objects.all(),
                fields=["user", "subscriber"],
            )]

    def validate(self, args):
        user = args.get("user", None)
        subscriber = self.initial_data.get("subscriber", None)
        if user == subscriber:
            raise serializers.ValidationError({"error": ("cant subscribe to yourself")})
        if SubscriptionUser.objects.filter(user=user, subscriber=subscriber).exists():
            raise serializers.ValidationError({"error": ("already subscribed")})
        return super().validate(args)

    def create(self, validated_data):
        instance = SubscriptionUser(
            **validated_data,
            user=self.context['kwargs']['pk'],
            subscriber=self.context['request']['user'],
        )
        return instance
