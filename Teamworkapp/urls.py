from django.urls import path
from .views import (
    NewsListCreateView, NewsDetailView,
    EventListCreateView, EventDetailView,
    JobListCreateView, JobDetailView,
    ApprovalListView, ApprovalReviewView,
    UserProfileView   # Make sure to import this!
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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

    # User Profile
    path('api/v1/me/', UserProfileView.as_view(), name='user-profile'),
]