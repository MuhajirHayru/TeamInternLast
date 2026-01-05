# teamworkapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import *

User = get_user_model()

# -----------------------------
# User Serializer (Only one definition — fixed duplicate)
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "role"]

# -----------------------------
# Media Serializer (READ ONLY)
# -----------------------------
class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pictures
        fields = ("id", "file", "uploaded_at")

# =====================================================
# MEDIA CREATE MIXIN (HANDLE FILE UPLOAD)
# =====================================================
class MediaCreateMixin(serializers.Serializer):
    uploads = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    def _save_media(self, instance, files):
        for f in files:
            Pictures.objects.create(
                file=f,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.pk
            )

# -----------------------------
# News Serializer
# -----------------------------
class NewsSerializer(MediaCreateMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    media = PicturesSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    is_expired=serializers.ReadOnlyField()

    class Meta:
        model = News
        fields = (
            "id", "title", "summary", "content", "source", "published_date",
            "author", "status", "expires_at","is_expired",
            "media", "uploads",
            "likes_count", "user_liked",
        )
        read_only_fields = ("status", "published_date", "author")

    def create(self, validated_data):
        files = validated_data.pop("uploads", [])
        obj = News.objects.create(**validated_data)
        self._save_media(obj, files)
        return obj

    def get_likes_count(self, obj):
        ct = ContentType.objects.get_for_model(News)
        return PostReaction.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_user_liked(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(News)
        return PostReaction.objects.filter(content_type=ct, object_id=obj.id, user=user).exists()

class EventSerializer(MediaCreateMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    media = PicturesSerializer(many=True, read_only=True)

    # NEW FIELDS: Add these
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id", "title", "event_type", "description", "start_date", "deadline",
            "target_audience", "location", "registration_link", "created_at",
            "author", "status", "media", "uploads",
            "likes_count", "user_liked",  # Add these two
        )
        read_only_fields = ("status", "created_at", "author")

    def create(self, validated_data):
        files = validated_data.pop("uploads", [])
        obj = Event.objects.create(**validated_data)
        self._save_media(obj, files)
        return obj

    # NEW METHODS: Add these two methods
    def get_likes_count(self, obj):
        ct = ContentType.objects.get_for_model(Event)
        return PostReaction.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_user_liked(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(Event)
        return PostReaction.objects.filter(
            content_type=ct,
            object_id=obj.id,
            user=user
        ).exists()


# -----------------------------
# Job Announcement Serializer
# -----------------------------
class JobAnnouncementSerializer(MediaCreateMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    media = PicturesSerializer(many=True, read_only=True)

    # THESE TWO LINES ARE THE FIX
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = JobAnnouncement
        fields = (
            "id", "title", "department", "job_type", "description", "requirements",
            "no_of_vacancies", "gender", "position", "salary", "location",
            "application_link", "expires_at", "posted_at",
            "author", "status",
            "media", "uploads",
            "likes_count", "user_liked",   # ADD THESE TWO
        )
        read_only_fields = ("status", "posted_at", "author")

    def create(self, validated_data):
        files = validated_data.pop("uploads", [])
        obj = JobAnnouncement.objects.create(**validated_data)
        self._save_media(obj, files)
        return obj

    # ADD THESE TWO METHODS EXACTLY
    def get_likes_count(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from .models import PostReaction
        ct = ContentType.objects.get_for_model(JobAnnouncement)
        return PostReaction.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_user_liked(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from .models import PostReaction
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(JobAnnouncement)
        return PostReaction.objects.filter(
            content_type=ct,
            object_id=obj.id,
            user=user
        ).exists()
# -----------------------------
# Approval Serializer
# -----------------------------
class ApprovalSerializer(serializers.ModelSerializer):
    submitted_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    content_type = serializers.StringRelatedField(read_only=True)
    content_object = serializers.SerializerMethodField()
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
        related = obj.content_object
        if not related:
            return None
        if hasattr(related, "title"):
            return {"id": related.pk, "title": related.title}
        if hasattr(related, "name"):
            return {"id": related.pk, "name": related.name}
        return {"id": related.pk}

# =====================================================
# Post Interactions
# =====================================================
class PostCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = (
            "id", "content_type", "object_id", "user",
            "comment_text", "parent_comment", "created_at", "replies"
        )
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
        if not 1 <= value <= 5:
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

# -----------------------------
# YouTube & Facebook Serializers
# -----------------------------
class youtubechannalser(serializers.ModelSerializer):
    class Meta:
        model = YouTubeChannel
        fields = "__all__"

class facebookchannalser(serializers.ModelSerializer):
    class Meta:
        model = FacebookConfig
        fields = "__all__"

# -----------------------------
# Product Serializer
# -----------------------------
class ProductSerializer(MediaCreateMixin, serializers.ModelSerializer):
    media = PicturesSerializer(many=True, read_only=True)

    # ADD THESE TWO FIELDS - SAME AS EVENT/JOB/NEWS
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id", "name", "features", "benefits", "product_url",
            "created_at", "expires_at", "status",
            "media", "uploads",
            "likes_count", "user_liked",  # ← ADD THESE
        )
        read_only_fields = ("status", "created_at")

    def create(self, validated_data):
        files = validated_data.pop("uploads", [])
        obj = Product.objects.create(**validated_data)  # author removed as per your code
        self._save_media(obj, files)
        return obj

    # ADD THESE TWO METHODS - IDENTICAL TO EVENT/JOB/NEWS
    def get_likes_count(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from .models import PostReaction
        ct = ContentType.objects.get_for_model(Product)
        return PostReaction.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_user_liked(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from .models import PostReaction
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(Product)
        return PostReaction.objects.filter(
            content_type=ct,
            object_id=obj.id,
            user=user
        ).exists()


# -----------------------------
# Service Serializer
# -----------------------------
class ServiceSerializer(MediaCreateMixin, serializers.ModelSerializer):
    media = PicturesSerializer(many=True, read_only=True)

    # ADD THESE TWO FIELDS - SAME AS OTHERS
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id", "name", "description", "duration", "price_range",
            "service_type", "phone_number", "created_at", "status",
            "media", "uploads",
            "likes_count", "user_liked",  # ← ADD THESE
        )
        read_only_fields = ("status", "created_at")

    def create(self, validated_data):
        files = validated_data.pop("uploads", [])
        obj = Service.objects.create(**validated_data)  # author removed as per your code
        self._save_media(obj, files)
        return obj

    # ADD THESE TWO METHODS - IDENTICAL TO OTHERS
    def get_likes_count(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from .models import PostReaction
        ct = ContentType.objects.get_for_model(Service)
        return PostReaction.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_user_liked(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from .models import PostReaction
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(Service)
        return PostReaction.objects.filter(
            content_type=ct,
            object_id=obj.id,
            user=user
        ).exists()

# =====================================================
# User Signup / IT Officer
# =====================================================
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(
            role=User.ROLE_CUSTOMER,
            **validated_data
        )

class ITOfficerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=User.ROLE_IT
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class ITOfficerPasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)

    def save(self, user):
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

# -----------------------------
# Notification Serializer
# -----------------------------
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "is_read", "created_at", "action_type"]


from rest_framework import serializers
from .models import TikTokProfile
class TikTokProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TikTokProfile
        fields = ["id", "username", "followers", "following", "likes", "videos", "last_updated"]
        read_only_fields = ["followers", "following", "likes", "videos", "last_updated"]
# here is just for inserting the channel names for telegram and also the channel ids ok
# channels/serializers.py
from rest_framework import serializers
from .models import TelegramChannel

class TelegramChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChannel
        fields = ['id', 'name', 'bot_token', 'channel_id', 'username']
