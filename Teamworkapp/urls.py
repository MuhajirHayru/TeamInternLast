# teamworkapp/urls.py
from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'feedback/comments', PostCommentViewSet)
router.register(r'feedback/reactions', PostReactionViewSet)
router.register(r'feedback/shares', PostShareViewSet)
router.register(r'feedback/ratings', PostRatingViewSet)
router.register(r'feedback/views', PostViewViewSet)
router.register(r'feedback/analytics', PostAnalyticsViewSet)
router.register(r'stats/youtube/create', youtubeviewset)
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
    path ('api/v1/',include(router.urls)),
    #for scial media view
    path("api/v1/stats/youtube/", YouTubeStatsView.as_view(), name="youtube-stats"),
   
    #for individual post analaytics
    path('api/v1/products/<int:pk>/analytics/', ProductAnalyticsView.as_view(), name='product-analytics'),
    path('api/v1/news/<int:pk>/analytics/', NewsAnalyticsView.as_view(), name='news-analytics'),
    path('api/v1/jobs/<int:pk>/analytics/', JobAnalyticsView.as_view(), name='job-analytics'),
    path('api/v1/events/<int:pk>/analytics/', EventAnalyticsView.as_view(), name='event-analytics'),
    path('api/v1/services/<int:pk>/analytics/', ServiceAnalyticsView.as_view(), name='service-analytics'),
    path('api/v1/brands/<int:pk>/analytics/', BrandAnalyticsView.as_view(), name='brand-analytics'),
]
