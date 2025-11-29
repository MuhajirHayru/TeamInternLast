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
# SIGNAL: auto-create Approval on new instances created by IT
# =====================================================
APPROVABLE_MODELS = (News, Event, JobAnnouncement, Product, Service, Brand)

@receiver(post_save)
def create_approval_on_create(sender, instance, created, **kwargs):
    if not created:
        return
    if sender in APPROVABLE_MODELS:
        status = getattr(instance, "status", None)
        if status and status == sender.STATUS_PENDING:
            submitted_by = None
            if hasattr(instance, "author"):
                submitted_by = getattr(instance, "author")
            elif hasattr(instance, "submitted_by"):
                submitted_by = getattr(instance, "submitted_by")
            Approval.objects.create(
                content_type=ContentType.objects.get_for_model(sender),
                object_id=instance.pk,
                submitted_by=submitted_by
            )
