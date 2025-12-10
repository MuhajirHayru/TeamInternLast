# teamworkapp/urls.py
from django.urls import path
from .views import (
    NewsListCreateView, NewsDetailView,
    EventListCreateView, EventDetailView,
    JobListCreateView, JobDetailView,
    ApprovalListView, ApprovalReviewView, ProductListCreateView, UserSignupView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProductListCreateView, ProductDetailView, ServiceListCreateView, ServiceDetailView

urlpatterns = [
    # JWT
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

# Products
    path('api/v1/products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('api/v1/products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

# Services
    path('api/v1/services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('api/v1/services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),

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
#below this the api for customer sighup
#i am adding thi just for use of 
    path('api/v1/signup/', UserSignupView.as_view(), name='user-signup'),

]
