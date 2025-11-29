# teamworkapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Pictures, News, Event, JobAnnouncement, Approval

User = get_user_model()

# -----------------------------
# User Serializer
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "role")

# -----------------------------
# Media Serializer
# -----------------------------
class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pictures
        fields = ("id", "file", "uploaded_at")

# -----------------------------
# News Serializer
# -----------------------------
class NewsSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    media = PicturesSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = (
            "id", "title", "summary", "content", "source", "published_date",
            "author", "status", "expires_at", "media"
        )
        read_only_fields = ("status", "published_date", "author")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data.pop('author', None)
        return News.objects.create(author=user, **validated_data)

# -----------------------------
# Event Serializer
# -----------------------------
class EventSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    media = PicturesSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "title", "event_type", "description", "start_date", "deadline",
            "target_audience", "location", "registration_link", "created_at",
            "author", "status", "media"
        )
        read_only_fields = ("status", "created_at", "author")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data.pop('author', None)
        return Event.objects.create(author=user, **validated_data)

# -----------------------------
# Job Announcement Serializer
# -----------------------------
class JobAnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    media = PicturesSerializer(many=True, read_only=True)

    class Meta:
        model = JobAnnouncement
        fields = (
            "id", "title", "department", "job_type", "description", "requirements",
            "no_of_vacancies", "gender", "position", "salary", "location", "application_link",
            "expires_at", "posted_at", "author", "status", "media"
        )
        read_only_fields = ("status", "posted_at", "author")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data.pop('author', None)
        return JobAnnouncement.objects.create(author=user, **validated_data)

# -----------------------------
# Approval Serializer
# -----------------------------
class ApprovalSerializer(serializers.ModelSerializer):
    # Show users as strings
    submitted_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    content_type = serializers.StringRelatedField(read_only=True)
    content_object = serializers.SerializerMethodField()

    # Use ChoiceField to validate against model constants
    status = serializers.ChoiceField(choices=Approval.STATUS_CHOICES)

    class Meta:
        model = Approval
        fields = (
            "id", "content_type", "object_id", "content_object",
            "submitted_by", "submitted_at", "status",
            "reviewed_by", "reviewed_at", "review_comment"
        )
        read_only_fields = ("submitted_by", "submitted_at", "content_object")

    def get_content_object(self, obj):
        """
        Return minimal info about the related object
        """
        related = obj.content_object
        if related is None:
            return None
        if hasattr(related, "title"):
            return {"id": related.pk, "title": getattr(related, "title")}
        if hasattr(related, "name"):
            return {"id": related.pk, "name": getattr(related, "name")}
        return {"id": related.pk}
