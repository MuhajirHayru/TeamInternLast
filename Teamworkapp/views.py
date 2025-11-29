# teamworkapp/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import News, Event, JobAnnouncement, Approval
from .serializers import NewsSerializer, EventSerializer, JobAnnouncementSerializer, ApprovalSerializer

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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return Approval.objects.all().order_by("-submitted_at")
        return Approval.objects.filter(submitted_by=user).order_by("-submitted_at")

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
