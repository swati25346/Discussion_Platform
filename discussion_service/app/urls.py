from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiscussionViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'discussions', DiscussionViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
