from datetime import date
from ..models import PageStats
from ..services.facebook import (
    get_followers, get_likes, get_views
)

from django.utils import timezone


def fetch_daily_facebook_stats():
    today = timezone.now().date()

    try:
        followers = get_followers()
        likes = get_likes()
        views = get_views()
    except Exception as e:
        print("❌ Facebook fetch failed:", e)
        return

    PageStats.objects.update_or_create(
        date=today,
        defaults={
            "followers": followers,
            "likes": likes,
            "views": views,
        },
    )

    print("✅ Facebook stats saved/updated for", today)
