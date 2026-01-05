# teamworkapp/views.py
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.contenttypes.models import ContentType
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .models import *
from .serializers import *
from .permissions import IsAdminUserRole

# -----------------------
# Helper function: public_filter
# -----------------------
def public_filter(qs, date_field=None, datetime_field=None):
    """
    Filter queryset for approved items and not expired.
    """
    now = timezone.now()
    qs = qs.filter(status__iexact="APPROVED") 
    if datetime_field:
        return qs.filter(
            models.Q(**{f"{datetime_field}__isnull": True}) |
            models.Q(**{f"{datetime_field}__gt": now})
        )
    if date_field:
        today = timezone.now().date()
        return qs.filter(
            models.Q(**{f"{date_field}__isnull": True}) |
            models.Q(**{f"{date_field}__gt": today})
        )
    return qs

User = get_user_model()

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

# -----------------------
# NEWS
# -----------------------
class NewsListCreateView(generics.ListCreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = NewsSerializer

    def get_queryset(self):
        qs = News.objects.all().order_by("-published_date")
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            return qs
        return public_filter(qs, datetime_field="expires_at").order_by("-published_date")

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not (user.is_superuser or getattr(user, "role", None) == "it_officer"):
            raise permissions.PermissionDenied("Only IT officers can create news posts.")
        serializer.save(author=user)

class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"] or instance.author == user):
            raise permissions.PermissionDenied("Not allowed to edit this news post.")
        serializer.save()

# -----------------------
# EVENTS
# -----------------------
class EventListCreateView(generics.ListCreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = EventSerializer

    def get_queryset(self):
        qs = Event.objects.all().order_by("-created_at")
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            return qs
        return public_filter(qs, datetime_field="deadline").order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not (user.is_superuser or getattr(user, "role", None) == "it_officer"):
            raise permissions.PermissionDenied("Only IT officers can create events.")
        serializer.save(author=user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"] or instance.author == user):
            raise permissions.PermissionDenied("Not allowed to edit this event.")
        serializer.save()

# -----------------------
# JOBS
# -----------------------
class JobListCreateView(generics.ListCreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = JobAnnouncementSerializer

    def get_queryset(self):
        qs = JobAnnouncement.objects.all().order_by("-posted_at")
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            return qs
        return public_filter(qs, date_field="expires_at").order_by("-posted_at")

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not (user.is_superuser or getattr(user, "role", None) == "it_officer"):
            raise permissions.PermissionDenied("Only IT officers can create job posts.")
        serializer.save(author=user)

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = JobAnnouncement.objects.all()
    serializer_class = JobAnnouncementSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"] or instance.author == user):
            raise permissions.PermissionDenied("Not allowed to edit this job post.")
        serializer.save()

# -----------------------
# APPROVALS
# -----------------------
class ApprovalListView(generics.ListAPIView):
    serializer_class = ApprovalSerializer
    queryset = Approval.objects.all().order_by("-submitted_at")

class ApprovalReviewView(generics.UpdateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApprovalSerializer
    queryset = Approval.objects.all()

    def update(self, request, *args, **kwargs):
        approval = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        if not (user.is_superuser or getattr(user, "role", None) == "admin"):
            return Response({"detail": "Only admins or superusers can review approvals."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        review_comment = request.data.get("review_comment", "")
        valid_statuses = [Approval.STATUS_PENDING, Approval.STATUS_APPROVED, Approval.STATUS_REJECTED]
        if new_status not in valid_statuses:
            return Response({"detail": f"Invalid status. Must be one of {valid_statuses}."}, status=status.HTTP_400_BAD_REQUEST)

        approval.status = new_status
        approval.reviewed_by = user
        approval.reviewed_at = timezone.now()
        approval.review_comment = review_comment
        approval.save()

        ct = approval.content_type
        model_class = ct.model_class()
        try:
            obj = model_class.objects.get(pk=approval.object_id)
            if hasattr(obj, "status"):
                obj.status = new_status
                obj.save()
        except model_class.DoesNotExist:
            pass

        return Response(ApprovalSerializer(approval).data, status=status.HTTP_200_OK)

class ApprovedViews(generics.ListAPIView):
    queryset = Approval.objects.filter(status='APPROVED')
    serializer_class = ApprovalSerializer

class PendingViews(generics.ListAPIView):
    queryset = Approval.objects.filter(status='PENDING')
    serializer_class = ApprovalSerializer

class RejectedViews(generics.ListAPIView):
    queryset = Approval.objects.filter(status='REJECTED')
    serializer_class = ApprovalSerializer

# -----------------------
# SOCIAL POSTS - LIKE & COMMENT FULLY WORKING
# -----------------------
class PostCommentViewSet(viewsets.ModelViewSet):
    queryset = PostComment.objects.all().order_by("-created_at")
    serializer_class = PostCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        ct_id = self.request.query_params.get('content_type')
        obj_id = self.request.query_params.get('object_id')
        if ct_id and obj_id:
            return queryset.filter(content_type_id=ct_id, object_id=obj_id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

class PostReactionViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = PostReaction.objects.all().order_by("-reacted_at")
    serializer_class = PostReactionSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        ct_id = request.data.get("content_type")
        obj_id = request.data.get("object_id")
        reaction_type = request.data.get("reaction_type", "like")

        existing = PostReaction.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
            user=user
        ).first()

        if existing:
            existing.delete()
            action = "unliked"
            user_reacted = False
        else:
            obj, created = PostReaction.objects.update_or_create(
                content_type_id=ct_id,
                object_id=obj_id,
                user=user,
                defaults={"reaction_type": reaction_type}
            )
            action = "liked"
            user_reacted = True

        total_count = PostReaction.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id
        ).count()

        return Response({
            "action": action,
            "count": total_count,
            "user_reacted": user_reacted
        }, status=status.HTTP_200_OK)

class PostShareViewSet(viewsets.ModelViewSet):
    queryset = PostShare.objects.all().order_by("-shared_at")
    serializer_class = PostShareSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostRatingViewSet(viewsets.ModelViewSet):
    queryset = PostRating.objects.all().order_by("-rated_at")
    serializer_class = PostRatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj, created = PostRating.objects.update_or_create(
            content_type=serializer.validated_data["content_type"],
            object_id=serializer.validated_data["object_id"],
            user=self.request.user,
            defaults={"rating": serializer.validated_data["rating"]}
        )
        serializer.instance = obj

class PostViewViewSet(viewsets.ModelViewSet):
    queryset = PostView.objects.all().order_by("-viewed_at")
    serializer_class = PostViewSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

class PostAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostAnalyticsSerializer
    queryset = PostAnalytics.objects.all()

    def get_queryset(self):
        qs = PostAnalytics.objects.all()
        object_id = self.request.query_params.get("object_id")
        content_type = self.request.query_params.get("content_type")
        if object_id:
            qs = qs.filter(object_id=object_id)
        if content_type:
            qs = qs.filter(content_type_id=content_type)
        return qs

# -----------------------
# ANALYTICS VIEWS
# -----------------------
class ProductAnalyticsView(APIView):
    def get(self, request, pk):
        ct = ContentType.objects.get_for_model(Product)
        analytics = PostAnalytics.objects.filter(content_type=ct, object_id=pk).first()
        if not analytics:
            return Response({"detail": "No analytics found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostAnalyticsSerializer(analytics).data)

class NewsAnalyticsView(APIView):
    def get(self, request, pk):
        ct = ContentType.objects.get_for_model(News)
        analytics = PostAnalytics.objects.filter(content_type=ct, object_id=pk).first()
        if not analytics:
            return Response({"detail": "No analytics found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostAnalyticsSerializer(analytics).data)

class JobAnalyticsView(APIView):
    def get(self, request, pk):
        ct = ContentType.objects.get_for_model(JobAnnouncement)
        analytics = PostAnalytics.objects.filter(content_type=ct, object_id=pk).first()
        if not analytics:
            return Response({"detail": "No analytics found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostAnalyticsSerializer(analytics).data)

class EventAnalyticsView(APIView):
    def get(self, request, pk):
        ct = ContentType.objects.get_for_model(Event)
        analytics = PostAnalytics.objects.filter(content_type=ct, object_id=pk).first()
        if not analytics:
            return Response({"detail": "No analytics found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostAnalyticsSerializer(analytics).data)

class ServiceAnalyticsView(APIView):
    def get(self, request, pk):
        ct = ContentType.objects.get_for_model(Service)
        analytics = PostAnalytics.objects.filter(content_type=ct, object_id=pk).first()
        if not analytics:
            return Response({"detail": "No analytics found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostAnalyticsSerializer(analytics).data)

class BrandAnalyticsView(APIView):
    def get(self, request, pk):
        ct = ContentType.objects.get_for_model(Brand)
        analytics = PostAnalytics.objects.filter(content_type=ct, object_id=pk).first()
        if not analytics:
            return Response({"detail": "No analytics found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostAnalyticsSerializer(analytics).data)

# -----------------------
# YOUTUBE CHANNELS
# -----------------------


class YouTubeStatsView(APIView):

    def get(self, request):
        channels = YouTubeChannel.objects.all()
        if not channels.exists():
            return Response({"error": "No channels configured"}, status=400)

        results = []

        for channel in channels:
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "statistics",
                "id": channel.channel_id,
                "key": settings.YOUTUBE_API_KEY
            }

            r = requests.get(url, params=params)
            data = r.json()

            if "items" in data and data["items"]:
                stats = data["items"][0]["statistics"]

                # Save snapshot tied to channel
                # YouTubeStats.objects.update_or_create(
                #     channel_id=channel.channel_id,
                #     view_count=stats.get("viewCount", 0),
                #     subscriber_count=stats.get("subscriberCount", 0),
                #     video_count=stats.get("videoCount", 0),
                # )

                results.append({
                    "channel_name": channel.name,
                    "channel_id": channel.channel_id,
                    "view_count": stats.get("viewCount", 0),
                    "subscriber_count": stats.get("subscriberCount", 0),
                    "video_count": stats.get("videoCount", 0),
                })
            else:
                results.append({
                    "channel_name": channel.name,
                    "channel_id": channel.channel_id,
                    "error": "No statistics found"
                })

        return Response(results, status=200)

class youtubeviewset(viewsets.ModelViewSet):
    queryset = YouTubeChannel.objects.all()
    serializer_class = youtubechannalser

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import FacebookToken1, PageStats
def get_valid_facebook_page_token():
    token = FacebookToken1.objects.first()

    if not token:
        raise Exception("Facebook token not configured")

    # if token still valid → use it
    if token.expires_at and token.expires_at > timezone.now():
        return token.page_token

    # 🔁 refresh token if expired
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": settings.FACEBOOK_APP_ID,
        "client_secret": settings.FACEBOOK_APP_SECRET,
        "fb_exchange_token": token.user_access_token,
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "access_token" not in data:
        raise Exception(f"Token refresh failed: {data}")

    token.user_access_token = data["access_token"]
    token.expires_at = timezone.now() + timezone.timedelta(days=60)
    token.save()

    return token.page_token
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from Teamworkapp.models import FacebookToken1


GRAPH_URL = "https://graph.facebook.com/v24.0"


class FacebookStatsView(APIView):
    def get(self, request):
        try:
            # 1️⃣ Get stored page token & page id
            fb = FacebookToken1.objects.first()
            if not fb:
                return Response(
                    {"error": "Facebook page token not configured"},
                    status=400,
                )

            page_id = fb.page_id
            access_token = fb.page_token

            # 2️⃣ Get followers & likes
            page_res = requests.get(
                f"{GRAPH_URL}/{page_id}",
                params={
                    "fields": "followers_count,fan_count",
                    "access_token": access_token,
                },
            ).json()

            followers = page_res.get("followers_count", 0)
            likes = page_res.get("fan_count", 0)

            # 3️⃣ Get page views (CORRECT endpoint)
            insights_res = requests.get(
                f"{GRAPH_URL}/{page_id}/insights",
                params={
                    "metric": "page_views_total",
                    "period": "days_28",
                    "access_token": access_token,
                },
            ).json()

            views = 0
            if insights_res.get("data"):
                values = insights_res["data"][0].get("values", [])
                if values:
                    views = values[-1].get("value", 0)

            return Response(
                {
                    "date": timezone.now().date(),
                    "followers": followers,
                    "likes": likes,
                    "views": views,
                },
                status=200,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)
class facebookviewset(viewsets.ModelViewSet):
    queryset = FacebookConfig.objects.all()
    serializer_class = facebookchannalser
    permission_classes = [AllowAny]

# -----------------------
# PRODUCTS - FIXED (no author=user)
# -----------------------
class ProductListCreateView(generics.ListCreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all().order_by("-created_at")
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            return qs
        return qs.filter(status="APPROVED")

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not getattr(user, "role", None) == "it_officer":
            raise permissions.PermissionDenied("Only IT officers can create products.")
        serializer.save()  # No author=user

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"] or instance.author == user):
            raise permissions.PermissionDenied("Not allowed to edit this product.")
        serializer.save()

# -----------------------
# SERVICES - FIXED (no author=user)
# -----------------------
class ServiceListCreateView(generics.ListCreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ServiceSerializer

    def get_queryset(self):
        qs = Service.objects.all().order_by("-created_at")
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            return qs
        return qs.filter(status="APPROVED")

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not getattr(user, "role", None) == "it_officer":
            raise permissions.PermissionDenied("Only IT officers can create services.")
        serializer.save()  # No author=user

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"] or instance.author == user):
            raise permissions.PermissionDenied("Not allowed to edit this service.")
        serializer.save()

# -----------------------
# CUSTOMER SIGNUP
# -----------------------
class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

# -----------------------
# IT OFFICER MANAGEMENT
# -----------------------
class CreateITOfficerView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request):
        serializer = ITOfficerCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "IT Officer created successfully",
                "id": user.id,
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangeITOfficerPasswordView(APIView):
    permission_classes = [IsAdminUserRole]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=User.ROLE_IT)
        serializer = ITOfficerPasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user)
            return Response({"message": "Password updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------
# NOTIFICATION API - ONLY UNREAD (THE ONLY CHANGE YOU REQUESTED)
# -----------------------
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread_count": count})

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save()
        return Response({"success": True})

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
import logging

from .models import PasswordResetOTP
from .utils import generate_otp

logger = logging.getLogger(__name__)
User = get_user_model()


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

        # Avoid MultipleObjectsReturned by picking a single user (prefer active)
        user = User.objects.filter(email__iexact=email, is_active=True).order_by("id").first()
        if not user:
            user = User.objects.filter(email__iexact=email).order_by("id").first()
        if not user:
            # Keep response generic for security
            return Response({"message": "If an account with that email exists, a reset code has been sent."}, status=status.HTTP_200_OK)

        try:
            otp = generate_otp()
            PasswordResetOTP.objects.create(user=user, otp=otp)
        except Exception as e:
            logger.exception("Failed creating OTP object")
            return Response({"error": "Server error creating OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost")

        try:
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is {otp}. It expires in 10 minutes.",
                from_email=from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception("Failed sending password reset email")
            # Clean up OTP if email failed
            try:
                PasswordResetOTP.objects.filter(user=user, otp=otp).delete()
            except Exception:
                pass
            return Response({"error": "Failed to send email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # DEBUG convenience: return otp in response only when DEBUG True
        if getattr(settings, "DEBUG", False):
            return Response({"message": "OTP sent to email (console).", "otp": otp}, status=status.HTTP_200_OK)

        return Response({"message": "If an account with that email exists, a reset code has been sent."}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not all([email, otp, new_password]):
            return Response({"error": "All fields required"}, status=status.HTTP_400_BAD_REQUEST)

        # Select a user safely (prefer active)
        user = User.objects.filter(email__iexact=email, is_active=True).order_by("-id").first()
        if not user:
            user = User.objects.filter(email__iexact=email).order_by("-id").first()
        if not user:
            return Response({"error": "Invalid OTP or user"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by("-created_at").first()
        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            otp_obj.delete()
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.password = make_password(new_password)
            user.save()
            otp_obj.delete()
        except Exception as e:
            logger.exception("Failed to reset password")
            return Response({"error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        
from rest_framework import generics, status
from rest_framework.response import Response
from .models import TikTokProfile
from .serializers import TikTokProfileSerializer
from .scraper import scrape_tiktok_profile
import asyncio

class TikTokProfileListCreate(generics.ListCreateAPIView):
    queryset = TikTokProfile.objects.all()
    serializer_class = TikTokProfileSerializer

    def perform_create(self, serializer):
        # user provides username; we scrape and save stats
        username = serializer.validated_data["username"]
        stats = asyncio.run(scrape_tiktok_profile(username))
        serializer.save(
            followers=stats["followers"],
            following=stats["following"],
            likes=stats["likes"],
            videos=stats["videos"],
        )

class TikTokProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TikTokProfile.objects.all()
    serializer_class = TikTokProfileSerializer

    def perform_update(self, serializer):
        # if username changed, re-scrape; if not, keep existing stats (optional)
        instance = self.get_object()
        old_username = instance.username

        updated_instance = serializer.save()  # temporarily save username change
        new_username = updated_instance.username

        if new_username != old_username:
            stats = asyncio.run(scrape_tiktok_profile(new_username))
            updated_instance.followers = stats["followers"]
            updated_instance.following = stats["following"]
            updated_instance.likes = stats["likes"]
            updated_instance.videos = stats["videos"]
            updated_instance.save()

    # Optional: real-time refresh on every GET of a single profile
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Real-time refresh when client requests details
        stats = asyncio.run(scrape_tiktok_profile(instance.username))
        instance.followers = stats["followers"]
        instance.following = stats["following"]
        instance.likes = stats["likes"]
        instance.videos = stats["videos"]
        instance.save()
        return super().retrieve(request, *args, **kwargs)
# views.py (add this)
from rest_framework.views import APIView

class TikTokProfileRefresh(APIView):
    def post(self, request, pk):
        profile = TikTokProfile.objects.get(pk=pk)
        stats = asyncio.run(scrape_tiktok_profile(profile.username))
        profile.followers = stats["followers"]
        profile.following = stats["following"]
        profile.likes = stats["likes"]
        profile.videos = stats["videos"]
        profile.save()
        return Response(TikTokProfileSerializer(profile).data, status=status.HTTP_200_OK)
    
    #below this i want to develop the api for telegram
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .telegram_utils import get_followers, get_admins, promote_user, revoke_admin
from .models import TelegramChannel
from .serializers import TelegramChannelSerializer
import requests

def get_channel(bot_token=None, channel_id=None):
    """
    Retrieve a TelegramChannel object from the DB.
    """
    if bot_token and channel_id:
        try:
            return TelegramChannel.objects.get(bot_token=bot_token, channel_id=channel_id)
        except TelegramChannel.DoesNotExist:
            return None
    return TelegramChannel.objects.first()  # fallback to first channel

@api_view(['GET'])
def followers_view(request):
    channel = get_channel()
    if not channel:
        return Response({"error": "Channel not configured"}, status=400)
    try:
        followers = get_followers(channel.bot_token, channel.channel_id)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Telegram API unreachable: {str(e)}"}, status=503)
    return Response({"channel_id": channel.channel_id, "followers": followers})

@api_view(['GET'])
def admins_view(request):
    channel = get_channel()
    if not channel:
        return Response({"error": "Channel not configured"}, status=400)
    try:
        admins = get_admins(channel.bot_token, channel.channel_id)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Telegram API unreachable: {str(e)}"}, status=503)
    return Response({"channel_id": channel.channel_id, "admins": admins})

@api_view(['POST'])
def promote_view(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username required"}, status=400)
    channel = get_channel()
    if not channel:
        return Response({"error": "Channel not configured"}, status=400)
    try:
        result = promote_user(channel.bot_token, channel.channel_id, username)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Telegram API unreachable: {str(e)}"}, status=503)
    return Response(result)

@api_view(['POST'])
def revoke_view(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username required"}, status=400)
    channel = get_channel()
    if not channel:
        return Response({"error": "Channel not configured"}, status=400)
    try:
        result = revoke_admin(channel.bot_token, channel.channel_id, username)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Telegram API unreachable: {str(e)}"}, status=503)
    return Response(result)

# List all channels or create a new channel
class TelegramChannelListCreate(generics.ListCreateAPIView):
    queryset = TelegramChannel.objects.all()
    serializer_class = TelegramChannelSerializer

# Retrieve, update, or delete a channel by ID
class TelegramChannelRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = TelegramChannel.objects.all()
    serializer_class = TelegramChannelSerializer
    lookup_field = 'id'  # or use 'channel_id' if preferred
