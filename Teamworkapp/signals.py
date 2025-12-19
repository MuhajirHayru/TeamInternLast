# core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import (
    PostComment, PostReaction, PostShare,
    PostRating, PostView, PostAnalytics,
    Notification, Approval, User,
    News, Event, Product, Service, Brand, JobAnnouncement
)

# =====================================================
# ANALYTICS SIGNALS
# =====================================================

def ensure_analytics(instance):
    """
    Ensure PostAnalytics exists and update stats
    """
    analytics, _ = PostAnalytics.objects.get_or_create(
        content_type=instance.content_type,
        object_id=instance.object_id
    )
    analytics.update_stats()


@receiver(post_save, sender=PostComment)
@receiver(post_delete, sender=PostComment)
@receiver(post_save, sender=PostReaction)
@receiver(post_delete, sender=PostReaction)
@receiver(post_save, sender=PostShare)
@receiver(post_delete, sender=PostShare)
@receiver(post_save, sender=PostRating)
@receiver(post_delete, sender=PostRating)
@receiver(post_save, sender=PostView)
@receiver(post_delete, sender=PostView)
def update_analytics(sender, instance, **kwargs):
    ensure_analytics(instance)


# =====================================================
# NOTIFICATION SIGNALS
# =====================================================

APPROVABLE_MODELS = (News, Event, Product, Service, Brand, JobAnnouncement)


@receiver(post_save)
def create_notifications(sender, instance, created, **kwargs):
    """
    Notifications system:
    1. Admins are notified when IT officers create new approvable content
    2. IT Officers are notified when their content is approved/rejected
    3. Customers are notified when new approved content is available
    """

    channel_layer = get_channel_layer()

    # -----------------------------
    # 1️⃣ Notify admins on new content
    # -----------------------------
    if created and sender in APPROVABLE_MODELS and hasattr(instance, "author") and getattr(instance.author, "role", None) == "it_officer":
        admins = User.objects.filter(role="admin")
        ct = ContentType.objects.get_for_model(instance)
        for admin in admins:
            notif = Notification.objects.create(
                recipient=admin,
                message=f"New {sender.__name__} by {instance.author.username} requires approval",
                action_type="APPROVAL",
                content_type=ct,
                object_id=instance.id
            )

            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"user_{admin.id}",
                    {
                        "type": "send_notification",
                        "message": notif.message,
                    }
                )

    # -----------------------------
    # 2️⃣ Notify IT officer on approval/rejection
    # -----------------------------
    if sender == Approval and instance.status in ["APPROVED", "REJECTED"] and instance.submitted_by:
        notif = Notification.objects.create(
            recipient=instance.submitted_by,
            message=f"Your post was {instance.status.lower()} by admin",
            action_type="INFO",
            content_type=instance.content_type,
            object_id=instance.object_id
        )
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.submitted_by.id}",
                {
                    "type": "send_notification",
                    "message": notif.message,
                }
            )

        # -----------------------------
        # 3️⃣ Notify customers if approved
        # -----------------------------
        if instance.status == "APPROVED":
            ct_model = instance.content_type.model_class()
            try:
                content_instance = ct_model.objects.get(pk=instance.object_id)
            except ct_model.DoesNotExist:
                return

            customers = User.objects.filter(role="customer")
            for customer in customers:
                notif = Notification.objects.create(
                    recipient=customer,
                    message=f"New {instance.content_type} is now available: {content_instance}",
                    action_type="INFO",
                    content_type=instance.content_type,
                    object_id=instance.object_id
                )
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f"user_{customer.id}",
                        {
                            "type": "send_notification",
                            "message": notif.message,
                        }
                    )
