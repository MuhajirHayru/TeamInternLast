# core/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PostComment, PostReaction, PostShare, PostRating, PostView, PostAnalytics

def ensure_analytics(instance):
    ct = instance.content_type
    obj_id = instance.object_id
    analytics, _ = PostAnalytics.objects.get_or_create(content_type=ct, object_id=obj_id)
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