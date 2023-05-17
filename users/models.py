from django.contrib.auth.models import User
from django.db import models


class SubscriptionUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authors")
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscriber"], name="unique subscriber"
            )
        ]
