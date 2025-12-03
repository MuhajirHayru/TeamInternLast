# teamworkapp/urls.py
from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'post-comments', PostCommentViewSet)
router.register(r'post-reactions', PostReactionViewSet)
router.register(r'post-shares', PostShareViewSet)
router.register(r'post-ratings', PostRatingViewSet)
router.register(r'post-views', PostViewViewSet)
router.register(r'post-analytics', PostAnalyticsViewSet)
urlpatterns = [
    # JWT
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # News
    path('api/v1/news/', NewsListCreateView.as_view(), name='news-list-create'),
    path('api/v1/news/<int:pk>/', NewsDetailView.as_view(), name='news-detail'),

    # Events
    path('api/v1/events/', EventListCreateView.as_view(), name='event-list-create'),
    path('api/v1/events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),

    # Jobs
    path('api/v1/jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('api/v1/jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),

    # Approvals (admin review)
    path('api/v1/approvals/', ApprovalListView.as_view(), name='approval-list'),
    path('api/v1/approvals/<int:pk>/review/', ApprovalReviewView.as_view(), name='approval-review'),
    path ('api/v1/feadback/',include(router.urls))
]
