from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Article(models.Model):
    """Model for articles(posts)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    readers = models.ManyToManyField(
        User, through="ReadArticle", related_name="read_articles"
    )

    def __str__(self):
        return f"id {self.id} {self.title}"

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["created"]


class ReadArticle(models.Model):
    """Model for managing user-articles relations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.article.title}, read: {self.is_read}"
