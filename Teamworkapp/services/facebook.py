
import requests
from .facebook_token_manager import get_valid_page_token
from .facebook_config import get_facebook_config

GRAPH_URL = "https://graph.facebook.com/v24.0"

def get_followers():
    token = get_valid_page_token()
    page_id = get_facebook_config().page_id

    res = requests.get(
        f"{GRAPH_URL}/{page_id}",
        params={"fields": "followers_count", "access_token": token},
    ).json()

    return res.get("followers_count", 0)


def get_likes():
    token = get_valid_page_token()
    page_id = get_facebook_config().page_id
    res = requests.get(
        f"{GRAPH_URL}/{page_id}",
        params={"fields": "fan_count", "access_token": token},
    ).json()
    return res.get("fan_count", 0)

def get_views():
    token = get_valid_page_token()
    page_id = get_facebook_config().page_id
    res = requests.get(
        f"{GRAPH_URL}/{page_id}/insights",
        params={
            "metric": "page_views_total",
            "period": "week",
            "access_token": token,
        },
    )

    if res.status_code != 200:
        raise Exception(f"Facebook Insights Error: {res.text}")

    data = res.json().get("data", [])
    if not data:
        raise Exception("No insights data returned")

    return data[0]["values"][-1]["value"]



