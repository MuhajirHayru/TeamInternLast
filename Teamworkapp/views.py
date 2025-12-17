# teamworkapp/views.py - FULL UPDATED FILE

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import * # Make sure your serializers (PostReactionSerializer, etc.) are imported
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import requests 
from django.conf import settings 

User = get_user_model()

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the currently logged-in user
        return self.request.user

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

# -----------------------
# APPROVALS
# -----------------------
class ApprovalListView(generics.ListAPIView):
    serializer_class = ApprovalSerializer
    queryset=Approval.objects.filter(status='REJECTED')
    
class ApprovalReviewView(generics.UpdateAPIView):
    """
    API endpoint to allow admins or superusers to review and approve/reject submissions.
    Accepts PATCH requests with 'status' and optional 'review_comment'.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApprovalSerializer
    queryset = Approval.objects.all()

    def update(self, request, *args, **kwargs):
        approval = self.get_object()
        user = request.user

        # Only superuser or admin can review
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        if not (user.is_superuser or getattr(user, "role", None) == "admin"):
            return Response({"detail": "Only admins or superusers can review approvals."}, status=status.HTTP_403_FORBIDDEN)

        # Get status and comment
        new_status = request.data.get("status")
        review_comment = request.data.get("review_comment", "")

        # Validate status strictly against model constants
        valid_statuses = [Approval.STATUS_PENDING, Approval.STATUS_APPROVED, Approval.STATUS_REJECTED]
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Invalid status. Must be one of {valid_statuses}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update approval record
        approval.status = new_status
        approval.reviewed_by = user
        approval.reviewed_at = timezone.now()
        approval.review_comment = review_comment
        approval.save()

        # Update the underlying object if it has a 'status' field
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
#bellow this I want to develop the the api for the approved alone
class ApprovedViews(generics.ListAPIView):
    queryset=Approval.objects.filter(status='APPROVED')
    serializer_class=ApprovalSerializer

#bellow this I want to develop the the api for the pending alone
class PendingViews(generics.ListAPIView):
    queryset=Approval.objects.filter(status='PENDING')
    serializer_class=ApprovalSerializer
#bellow this I want to develop the the api for the rejected alone
class RejectedViews(generics.ListAPIView):
    queryset=Approval.objects.filter(status='REJECTED')
    serializer_class=ApprovalSerializer


# =================================================================
# POST FEEDBACK VIEWSETS
# =================================================================
class PostCommentViewSet(viewsets.ModelViewSet):
    # Publicly accessible comments, ordered by newest first
    queryset = PostComment.objects.all().order_by("-created_at") 
    serializer_class = PostCommentSerializer
    # Allow viewing for all, but creation/edit/delete only for authenticated users
    permission_classes = [IsAuthenticatedOrReadOnly] 

    # CRITICAL FIX: get_queryset to filter comments by post ID 
    def get_queryset(self):
        # 1. Start with the default queryset (all comments)
        queryset = super().get_queryset()

        # 2. Extract the filter parameters from the request URL (sent by the React component)
        content_type_id = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        # 3. Apply the necessary filter
        if content_type_id and object_id:
            # Filter the queryset to include ONLY comments for that specific post
            queryset = queryset.filter(
                content_type_id=content_type_id,
                object_id=object_id
            ).order_by('created_at') # Order ensures comments display chronologically
        
        # Optional: Prevent listing all comments if no specific post is requested
        elif self.action == 'list':
            return queryset.none()
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        # Ensure only authenticated users can comment
        if not user.is_authenticated:
            raise permissions.PermissionDenied("You must be logged in to comment.")
            
        serializer.save(user=user) # Associate the comment with the logged-in user


class PostReactionViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,) 
    queryset = PostReaction.objects.all().order_by("-reacted_at")
    serializer_class = PostReactionSerializer
    
    # 🛑 FINAL FIX: Direct ORM for Guaranteed Persistence 🛑
    def perform_create(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data

        content_type = validated_data["content_type"] # This is the ContentType object now
        object_id = validated_data["object_id"]
        reaction_type = validated_data.get("reaction_type", "like")
        
        reaction_qs = PostReaction.objects.filter(
            content_type=content_type,
            object_id=object_id,
            user=user
        )
        
        if reaction_qs.exists():
            # UNLIKE (Delete the existing reaction)
            reaction_qs.delete()
            # Set a temporary instance for the response
            serializer.instance = PostReaction(
                content_type=content_type, 
                object_id=object_id, 
                user=user, 
                reaction_type='unliked'
            )
        else:
            # LIKE (Create a new reaction using ORM to guarantee save)
            obj = PostReaction.objects.create(
                user=user,
                content_type=content_type,
                object_id=object_id,
                reaction_type=reaction_type
            )
            serializer.instance = obj

        
# -----------------------------------------------------------------
# POST REACTION COUNT VIEW
# -----------------------------------------------------------------
class PostReactionCountView(APIView):
    """
    Returns the total count of reactions for a specific post and checks if the current user has reacted.
    """
    permission_classes = [AllowAny] 

    def get(self, request, *args, **kwargs):
        content_type_id = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        reaction_type = request.query_params.get('reaction_type', 'like') 

        if not content_type_id or not object_id:
            return Response(
                {"detail": "Missing content_type or object_id query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter the PostReaction model
        count = PostReaction.objects.filter(
            content_type_id=content_type_id,
            object_id=object_id,
            reaction_type__iexact=reaction_type 
        ).count()

        # Check if the currently logged-in user has reacted to this post
        user_reacted = False
        if request.user.is_authenticated:
            user_reacted = PostReaction.objects.filter(
                content_type_id=content_type_id,
                object_id=object_id,
                user=request.user
            ).exists()

        return Response({
            "object_id": object_id,
            "content_type_id": content_type_id,
            "reaction_type": reaction_type,
            "count": count,
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
#====================social views======>
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
                # NOTE: You must have 'settings.YOUTUBE_API_KEY' defined in your Django settings
                "key": settings.YOUTUBE_API_KEY 
            }

            r = requests.get(url, params=params)
            data = r.json()

            if "items" in data and data["items"]:
                stats = data["items"][0]["statistics"]

                # Save snapshot tied to channel
                YouTubeStats.objects.create(
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
    # NOTE: Assuming youtubechannalser is defined in .serializers
    queryset= YouTubeChannel.objects.all()
    serializer_class= youtubechannalser
    
    
    
    
    #mohajir ++++===================>
    # PRODUCT
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
        # Public users see only approved, not expired
        return qs.filter(status="APPROVED")

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not getattr(user, "role", None) == "it_officer":
            raise permissions.PermissionDenied("Only IT officers can create products.")
        serializer.save()

# -----------------------
# SERVICE
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
        serializer.save()
#bello this the detailed views of the product and the service presented ok
# -----------------------
# PRODUCT DETAIL VIEW
# -----------------------
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific Product.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            raise permissions.PermissionDenied("Only admins or IT officers can edit this product.")
        serializer.save()

# -----------------------
# SERVICE DETAIL VIEW
# -----------------------
class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific Service.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if not (user.is_superuser or getattr(user, "role", None) in ["admin", "it_officer"]):
            raise permissions.PermissionDenied("Only admins or IT officers can edit this service.")
        serializer.save()
    #below this the code is for developing the api for customeruser ok 
from rest_framework import generics, permissions
# NOTE: UserSignupSerializer must be imported from .serializers if it's not in the main block
# from .serializers import UserSignupSerializer 

class UserSignupView(generics.CreateAPIView):
    """
    API endpoint for normal user signup (role='customer').
    """
    # NOTE: Assuming UserSignupSerializer is correctly defined
    serializer_class = UserSignupSerializer 
    permission_classes = [permissions.AllowAny]   # anyone can signup