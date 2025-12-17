from django.utils import timezone
from datetime import timedelta
from Teamworkapp.models import FacebookToken1
from .facebook_auth import refresh_page_access_token


def get_valid_page_token():
    token_obj = FacebookToken1.objects.first()

    if not token_obj:
        raise Exception("FacebookToken not configured")

    # Debug (safe)
    print("USING PAGE TOKEN:", token_obj.page_token[:15])

    # Refresh if expired OR about to expire (within 5 days)
    if not token_obj.expires_at or token_obj.expires_at <= timezone.now() + timedelta(days=5):
        print("🔄 Page token expired or expiring soon → refreshing")
        return refresh_page_access_token()

    return token_obj.page_token
