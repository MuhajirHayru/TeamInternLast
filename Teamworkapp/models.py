# teamworkapp/models.py
from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q  # ← Added for filtering admins/IT officers

# =====================================================
# CUSTOM USER MODEL
# =====================================================
class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_IT = "it_officer"
    ROLE_CUSTOMER = "customer"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_IT, "IT Officer"),
        (ROLE_CUSTOMER, "Customer"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_it_officer(self):
        return self.role == self.ROLE_IT

    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    def __str__(self):
        return self.username


# =====================================================
# MEDIA MODEL
# =====================================================
class Pictures(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    attached_to = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.file.name


# =====================================================
# APPROVAL MODEL
# =====================================================
class Approval(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="submitted_approvals")
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_approvals")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.content_type.model}:{self.object_id} - {self.status}"


# =====================================================
# BRAND
# =====================================================
class Brand(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField(unique=True, region="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return self.name or "Brand"


# =====================================================
# PRODUCT
# =====================================================
class Product(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    media = GenericRelation(Pictures)

    name = models.CharField(max_length=200)
    features = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    product_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return self.name

    @property
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at


# =====================================================
# SERVICE
# =====================================================
class Service(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    media = GenericRelation(Pictures)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    price_range = models.CharField(max_length=100, blank=True, null=True)
    service_type = models.CharField(max_length=100, blank=True, null=True)
    phone_number = PhoneNumberField(unique=True, region="", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return self.name


# =====================================================
# NEWS
# =====================================================
class News(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    media = GenericRelation(Pictures)

    title = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="news_posts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    # expiration for news
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title or "News"

    @property
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at


# =====================================================
# EVENT
# =====================================================
class Event(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    EVENT_TYPES = [
        ('workshop', 'Workshop'),
        ('hackathon', 'Hackathon'),
        ('recognition', 'Recognition Program'),
    ]

    media = GenericRelation(Pictures)
    title = models.CharField(max_length=255, blank=True, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(null=True)
    deadline = models.DateTimeField(null=True, blank=True)  # acts as expiry
    target_audience = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    registration_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # store who posted it (optional but helpful)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="events")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"{self.title or 'Event'} ({self.event_type})"

    @property
    def is_expired(self):
        return self.deadline and timezone.now() > self.deadline


# =====================================================
# COMPETITION DETAIL
# =====================================================
class CompetitionDetail(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='competition_detail')
    judging_criteria = models.TextField(blank=True)
    prize = models.CharField(max_length=255, blank=True, null=True)
    winner_name = models.CharField(max_length=255, blank=True, null=True)
    winner_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    winner_picture = models.ImageField(upload_to='winner_picture', blank=True, null=True)

    def __str__(self):
        return f"Competition Details - {self.event.title or 'Event'}"


# =====================================================
# JOB ANNOUNCEMENT
# =====================================================
class JobAnnouncement(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    media = GenericRelation(Pictures)

    title = models.CharField(max_length=255)
    department = models.CharField(max_length=150, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
    ], default='full_time')
    description = models.TextField()
    requirements = models.TextField()
    no_of_vacancies = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=50, default='both')
    position = models.TextField(blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    application_link = models.URLField(blank=True, null=True)
    # expiration for job (date)
    expires_at = models.DateField(blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    # store who posted it
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="job_posts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return self.title or "Job"

    @property
    def is_expired(self):
        return self.expires_at and timezone.now().date() > self.expires_at


# =====================================================
# SIGNAL: auto-create Approval AND Notification on new pending instances
# =====================================================
APPROVABLE_MODELS = (News, Event, JobAnnouncement, Product, Service, Brand)

@receiver(post_save)
def create_approval_and_notification(sender, instance, created, **kwargs):
    if not created:
        return
    if sender in APPROVABLE_MODELS:
        status = getattr(instance, "status", None)
        if status and status == sender.STATUS_PENDING:
            # Create Approval
            submitted_by = None
            if hasattr(instance, "author"):
                submitted_by = getattr(instance, "author")
            Approval.objects.create(
                content_type=ContentType.objects.get_for_model(sender),
                object_id=instance.pk,
                submitted_by=submitted_by
            )

            # Create Notification for all admins and IT officers
            model_name = sender._meta.model_name  # e.g., "news", "product"
            title = str(instance)
            if hasattr(instance, "title") and instance.title:
                title = instance.title
            elif hasattr(instance, "name") and instance.name:
                title = instance.name

            message = f"New {model_name.title()} pending approval: {title}"

            # Get all admins and IT officers
            recipients = User.objects.filter(
                Q(role=User.ROLE_ADMIN) | Q(role=User.ROLE_IT)
            )

            # Create notification for each
            notifications_to_create = [
                Notification(
                    recipient=recipient,
                    message=message,
                    action_type="APPROVAL",
                    content_type=ContentType.objects.get_for_model(sender),
                    object_id=instance.pk
                )
                for recipient in recipients
            ]
            Notification.objects.bulk_create(notifications_to_create)


class PostComment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey("Teamworkapp.User", on_delete=models.SET_NULL, null=True)
    comment_text = models.TextField()
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.content_object}"

# -------------------
# REACTIONS
# -------------------
class PostReaction(models.Model):
    REACTION_TYPES = [
        ("like", "Like"),
        ("love", "Love"),
        ("insightful", "Insightful"),
        ("celebrate", "Celebrate"),
        ("dislike", "Dislike"),
    ]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES, default="like")
    reacted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("content_type", "object_id", "user")  # one reaction per user per item

    def __str__(self):
        return f"{self.user} reacted {self.reaction_type} on {self.content_object}"

# -------------------
# SHARES
# -------------------
class PostShare(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    shared_to = models.CharField(max_length=100, blank=True, null=True)  # e.g. Facebook, Telegram
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} shared {self.content_object} to {self.shared_to or 'Internal'}"

# -------------------
# RATINGS
# -------------------
class PostRating(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1–5 stars
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("content_type", "object_id", "user")

    def __str__(self):
        return f"{self.user} rated {self.content_object} - {self.rating}★"

# -------------------
# VIEWS
# -------------------
class PostView(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View on {self.content_object} by {self.user or 'Anonymous'}"
class PostAnalytics(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    total_views = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_reactions = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ("content_type", "object_id") 

    def update_stats(self):
        self.total_views = PostView.objects.filter(content_type=self.content_type, object_id=self.object_id).count()
        self.total_comments = PostComment.objects.filter(content_type=self.content_type, object_id=self.object_id).count()
        self.total_reactions = PostReaction.objects.filter(content_type=self.content_type, object_id=self.object_id).count()
        self.total_shares = PostShare.objects.filter(content_type=self.content_type, object_id=self.object_id).count()
        self.total_ratings = PostRating.objects.filter(content_type=self.content_type, object_id=self.object_id).count()

        ratings = PostRating.objects.filter(content_type=self.content_type, object_id=self.object_id).values_list("rating", flat=True)
        self.average_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        self.engagement_score = (
            (self.total_reactions * 2)
            + self.total_comments
            + (self.total_shares * 3)
            + (self.average_rating * 10)
        )
        self.save()

    def __str__(self):
        return f"Analytics for {self.content_object}"
    
 #===========================social==========================   

# models.py
from django.db import models

class YouTubeChannel(models.Model):
    name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
  
    
class FacebookConfig(models.Model):
    app_id = models.CharField(max_length=255)
    app_secret = models.CharField(max_length=255)
    page_id = models.CharField(max_length=100)
    long_lived_user_token = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Facebook Config (Page {self.page_id})"

    class Meta:
        verbose_name = "Facebook Configuration"
        verbose_name_plural = "Facebook Configuration"


class PageStats(models.Model):
    date = models.DateField(unique=True)
    followers = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date}: {self.views} views, {self.followers} followers, {self.likes} likes"


class FacebookToken1(models.Model):
    page_id = models.CharField(max_length=50)
    page_token = models.TextField()
    expires_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"FacebookToken (expires {self.expires_at})"


#below this the notification api presented 
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    action_type = models.CharField(max_length=50, default="INFO")  # APPROVAL, INFO, ALERT
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.message[:20]}"
# Teamworkapp/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
 
class TikTokProfile(models.Model):
    username = models.CharField(max_length=255, unique=True)
    followers = models.IntegerField(null=True,blank=True)
    following = models.IntegerField(null=True,blank=True)
    likes = models.IntegerField(null=True,blank=True)
    videos = models.IntegerField(null=True,blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
# below this i am doing perfectlly the api for the telegram 
class TelegramChannel(models.Model):
    name = models.CharField(max_length=255, blank=True)
    bot_token = models.CharField(max_length=255)  # your bot token
    channel_id = models.BigIntegerField(unique=True)  # e.g., -1001970249942
    username = models.CharField(max_length=255, blank=True)  # optional username

    def __str__(self):
        return self.name or str(self.channel_id)   
