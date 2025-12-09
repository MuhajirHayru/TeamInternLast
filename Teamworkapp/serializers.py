# teamworkapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

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
#==============================================================my beke
class PostCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "content_type", "object_id", "user", "comment_text", "parent_comment", "created_at", "replies")
        read_only_fields = ("user", "created_at")

    def get_replies(self, obj):
        return PostCommentSerializer(obj.replies.all(), many=True).data

class PostReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostReaction
        fields = ("id", "content_type", "object_id", "user", "reaction_type", "reacted_at")
        read_only_fields = ("user", "reacted_at")

class PostShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostShare
        fields = ("id", "content_type", "object_id", "user", "shared_to", "shared_at")
        read_only_fields = ("user", "shared_at")

class PostRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostRating
        fields = ("id", "content_type", "object_id", "user", "rating", "rated_at")
        read_only_fields = ("user", "rated_at")

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class PostViewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostView
        fields = ("id", "content_type", "object_id", "user", "viewed_at")
        read_only_fields = ("user", "viewed_at")

class PostAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAnalytics
        fields = "__all__"
        
 #================ for view for ========>       
class youtubechannalser(serializers.ModelSerializer):
     class Meta:
       model =YouTubeChannel
       fields= "__all__"