import json

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status
from rest_framework_simplejwt.tokens import RefreshToken

from articles.models import Article, ReadArticle
from articles.serializers import ArticleSerializer
from users.models import SubscriptionUser
from users.serializers import UserSerializer


class ArticlesApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(username="alex", password="wbblog")
        self.user_2 = User.objects.create_user(username="murfy", password="wbblog")

        self.article_1 = Article.objects.create(
            title="Test_article_1", body="hello_1", user=self.user_1
        )
        self.article_2 = Article.objects.create(
            title="Test_article_2", body="hello_2", user=self.user_1
        )
        self.article_3 = Article.objects.create(
            title="Test_article_3", body="hello_3", user=self.user_2
        )
        self.subscription = SubscriptionUser.objects.create(
            user=self.user_1, subscriber=self.user_2
        )

    def test_get(self):
        url = reverse("articles-list")
        response = self.client.get(url)
        articles = Article.objects.all().order_by("-created")
        serializer_data = ArticleSerializer(articles, many=True).data
        self.assertEqual(serializer_data, response.data.get("results"))
        self.assertEqual(3, Article.objects.all().count())
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create(self):
        self.assertEqual(3, Article.objects.all().count())
        url = reverse("articles-list")
        data = {"title": "Python 310", "body": "new release!"}
        json_data = json.dumps(data)
        refresh = RefreshToken.for_user(self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Article.objects.all().count())

    def test_update(self):
        url = reverse("articles-detail", args=(self.article_1.id,))
        data = {"title": self.article_1.title, "body": "new release!"}
        json_data = json.dumps(data)
        refresh = RefreshToken.for_user(self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.article_1.refresh_from_db()
        self.assertEqual("new release!", self.article_1.body)

    def test_delete(self):
        self.assertEqual(3, Article.objects.all().count())
        url = reverse("articles-detail", args=(self.article_1.id,))
        refresh = RefreshToken.for_user(self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.delete(url, content_type="application/json")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Article.objects.all().count())

    def test_mark_read(self):
        url = "/api/articles/read_articles/1/"
        data = {"is_read": True}
        json_data = json.dumps(data)
        refresh = RefreshToken.for_user(self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        read_article = ReadArticle.objects.get(
            article_id=self.article_1.id, user=self.user_1
        )
        self.assertTrue(read_article.is_read)

    def test_feed(self):
        url = reverse("articles-feed")
        refresh = RefreshToken.for_user(self.user_2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.get(url, content_type="application/json")
        articles = Article.objects.filter(user__authors__subscriber=self.user_2).order_by("-created")
        serializer_data = ArticleSerializer(articles, many=True).data
        self.assertEqual(serializer_data, response.data.get("results"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_feed_read(self):
        url = reverse("articles-feed-read")
        refresh = RefreshToken.for_user(self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.get(url, content_type="application/json")
        articles = Article.objects.filter(
            Q(user__authors__subscriber=self.user_1, readarticle__is_read=False)
            | Q(user__authors__subscriber=self.user_1, readarticle__is_read=None)
        )
        serializer_data = ArticleSerializer(articles, many=True).data
        self.assertEqual(serializer_data, response.data.get("results"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_list_users(self):
        url = reverse("user-list")
        response = self.client.get(url)
        users = (
            User.objects.all()
            .annotate(num_articles=Count("article"))
            .order_by("-num_articles")
        )
        serializer_data = UserSerializer(users, many=True).data
        self.assertEqual(serializer_data, response.data.get("results"))
        self.assertEqual(2, User.objects.all().count())
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_subscribe(self):
        url = reverse("subscriptionuser-list")
        data = {"user": 2}
        json_data = json.dumps(data)
        self.assertEqual(1, SubscriptionUser.objects.all().count())
        refresh = RefreshToken.for_user(self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, SubscriptionUser.objects.all().count())

    def test_unsubscribe(self):
        url = reverse("subscriptionuser-detail", args=(self.subscription.id,))
        self.assertEqual(1, SubscriptionUser.objects.all().count())
        refresh = RefreshToken.for_user(self.user_2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.delete(url, content_type="application/json")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, SubscriptionUser.objects.all().count())
