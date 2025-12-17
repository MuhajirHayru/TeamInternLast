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
# SOCIAL POSTS
# -----------------------
class PostCommentViewSet(viewsets.ModelViewSet):
    queryset = PostComment.objects.all().order_by("-created_at")
    serializer_class = PostCommentSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

class PostReactionViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = PostReaction.objects.all().order_by("-reacted_at")
    serializer_class = PostReactionSerializer

    def perform_create(self, serializer):
        obj, created = PostReaction.objects.update_or_create(
            content_type=serializer.validated_data["content_type"],
            object_id=serializer.validated_data["object_id"],
            user=self.request.user,
            defaults={"reaction_type": serializer.validated_data["reaction_type"]}
        )
        serializer.instance = obj

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
                YouTubeStats.objects.update_or_create(
                    channel_id=channel.channel_id,
                    view_count=stats.get("viewCount", 0),
                    subscriber_count=stats.get("subscriberCount", 0),
                    video_count=stats.get("videoCount", 0),
                )
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
class FacebookStatsAPI(APIView):
    def get(self, request):
        stat = PageStats.objects.order_by("-date").first()

        if not stat:
            return Response({
                "followers": 0,
                "likes": 0,
                "views": 0,
                "last_updated": None
            })

        return Response({
            "followers": stat.followers,
            "likes": stat.likes,
            "views": stat.views,
            
        })
# -----------------------
# PRODUCTS
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
        serializer.save(author=user)

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
# SERVICES
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
        serializer.save(author=user)

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
