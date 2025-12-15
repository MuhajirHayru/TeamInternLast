# teamworkapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

# from rest_framework import serializers
# from .models import User
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
       
       
#======= mohajir>
#  Product Serializer
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    media = PicturesSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "features", "benefits", "product_url",
            "created_at", "expires_at", "status", "media"
        )
        read_only_fields = ("status", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        # If you want to attach author as a foreign key, uncomment this line
        # validated_data['author'] = user
        return Product.objects.create(**validated_data)


# -----------------------------
# Service Serializer
# -----------------------------
class ServiceSerializer(serializers.ModelSerializer):
    media = PicturesSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = (
            "id", "name", "description", "duration", "price_range",
            "service_type", "phone_number", "created_at", "status", "media"
        )
        read_only_fields = ("status", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        # If you want to attach author as a foreign key, uncomment this line
        # validated_data['author'] = user
        return Service.objects.create(**validated_data)
#below this there is api for creating user sighuppages ok 
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password2')

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
            role=User.ROLE_CUSTOMER  # assign normal user role
        )
        return user

class ITOfficerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name"]

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
#this is serializer for changing passwords for IT_officers
class ITOfficerPasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6)

    def save(self, user):
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


