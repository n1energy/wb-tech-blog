from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserFollowingViewSet, UsersViewSet, UserTokenObtainPairView

router = SimpleRouter()

router.register("profile", UsersViewSet)
router.register("subscribe", UserFollowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("login/", UserTokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
]
