# <<<<<<< HEAD
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'feedback/comments', PostCommentViewSet)
router.register(r'feedback/reactions', PostReactionViewSet)
router.register(r'feedback/shares', PostShareViewSet)
router.register(r'feedback/ratings', PostRatingViewSet)
router.register(r'feedback/views', PostViewViewSet)
router.register(r'feedback/analytics', PostAnalyticsViewSet)
router.register(r'stats/youtube/create', youtubeviewset)
router.register(r'stats/facebook/create', facebookviewset)

# =======
# teamworkapp/urls.py


# >>>>>>> 6b98ccc71aaaa698815f782692e09f9cfb922a3a
urlpatterns = [
    # User
    #  path('profile/', UserProfileView.as_view(), name='user-profile'),
    #  path('me/', UserProfileView.as_view(), name='me'),

# Products
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

# Services
    path('services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),

    # News
    path('news/', NewsListCreateView.as_view(), name='news-list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news-detail'),

    # Events
    path('events/', EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),

    # Jobs
    path('jobs/', JobListCreateView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    #bellow this i have the endpoints for the creations of the it__officers and changing the password
    
    path("it-officers/create/", CreateITOfficerView.as_view()),
    path("officers/<int:pk>/change-password/", ChangeITOfficerPasswordView.as_view()),

    # Approvals
    path('approvals/', ApprovalListView.as_view(), name='approval-list'),
    path('approvals/<int:pk>/review/', ApprovalReviewView.as_view(), name='approval-review'),
    #api for the notifications
    # path("notifications/count/", NotificationCountView.as_view()),
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/count/", NotificationCountView.as_view(), name="notifications-count"),
    path("notifications/<int:pk>/mark_read/", NotificationMarkReadView.as_view(), name="notifications-mark-read"),
    # Router URLs
    path('set/', include(router.urls)),

    # Social Media Views
    path("stats/youtube/", YouTubeStatsView.as_view(), name="youtube-stats"),
    path("stats/facebook/", FacebookStatsAPI.as_view()),

    # Analytics by post type
    path('products/<int:pk>/analytics/', ProductAnalyticsView.as_view(), name='product-analytics'),
    path('news/<int:pk>/analytics/', NewsAnalyticsView.as_view(), name='news-analytics'),
    path('jobs/<int:pk>/analytics/', JobAnalyticsView.as_view(), name='job-analytics'),
    path('events/<int:pk>/analytics/', EventAnalyticsView.as_view(), name='event-analytics'),
    path('services/<int:pk>/analytics/', ServiceAnalyticsView.as_view(), name='service-analytics'),
    path('brands/<int:pk>/analytics/', BrandAnalyticsView.as_view(), name='brand-analytics'),
    # Approvals (admin review)
    path('approvals/', ApprovalListView.as_view(), name='approval-list'),
    path('approvals/<int:pk>/review/', ApprovalReviewView.as_view(), name='approval-review'),
    #iam adding this just for use of api for customer sighup
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    #   again g=here there is the api for aproved views only
    path('Approved_views/', ApprovedViews.as_view(), name='approved-lists'),
    path('Pending_views/', PendingViews.as_view(), name='Pending-lists'),
    path('Rejected_views/', RejectedViews.as_view(), name='Rejected-lists'),
    path("auth/forgot-password/", ForgotPasswordAPIView.as_view()),
    path("auth/reset-password/", ResetPasswordAPIView.as_view()),
    ]

# >>>>>>> 6b98ccc71aaaa698815f782692e09f9cfb922a3a