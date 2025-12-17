import requests
from datetime import timedelta
from django.utils import timezone
from .facebook_config import get_facebook_config
from Teamworkapp.models import FacebookToken1

GRAPH_URL = "https://graph.facebook.com/v24.0"

def refresh_page_access_token():
    config = get_facebook_config()
    token_obj = FacebookToken1.objects.first()

    if not token_obj:
        raise Exception("FacebookToken row not found")

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": config.app_id,
        "client_secret": config.app_secret,
        "fb_exchange_token": config.long_lived_user_token,
    }

    res = requests.get(f"{GRAPH_URL}/oauth/access_token", params=params).json()

    if "access_token" not in res:
        raise Exception(f"Token refresh failed: {res}")

    user_token = res["access_token"]
    expires_in = res.get("expires_in", 60 * 60 * 24 * 60)

    pages = requests.get(
        f"{GRAPH_URL}/me/accounts",
        params={"access_token": user_token},
    ).json()

    for page in pages.get("data", []):
        if page["id"] == config.page_id:
            token_obj.page_token = page["access_token"]
            token_obj.expires_at = timezone.now() + timedelta(seconds=expires_in)
            token_obj.save()
            return token_obj.page_token

    raise Exception("Configured page not found for this user")
