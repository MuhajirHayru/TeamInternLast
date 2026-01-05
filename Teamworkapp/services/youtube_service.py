# import requests
# from django.conf import settings
# from django.utils import timezone
# from Teamworkapp.models import YouTubeChannel, YouTubeStats

# def fetch_youtube_stats():
#     channels = YouTubeChannel.objects.all()

#     if not channels.exists():
#         return "No YouTube channels configured"

#     today = timezone.now().date()
#     saved = 0

#     for channel in channels:
#         url = "https://www.googleapis.com/youtube/v3/channels"
#         params = {
#             "part": "statistics",
#             "id": channel.channel_id,
#             "key": settings.YOUTUBE_API_KEY,
#         }

#         r = requests.get(url, params=params)
#         data = r.json()

#         if "items" not in data or not data["items"]:
#             continue

#         stats = data["items"][0]["statistics"]

#         YouTubeStats.objects.update_or_create(
#             channel_id=channel.channel_id,
#             date=today,
#             defaults={
#                 "view_count": int(stats.get("viewCount", 0)),
#                 "subscriber_count": int(stats.get("subscriberCount", 0)),
#                 "video_count": int(stats.get("videoCount", 0)),
#             },
#         )

#         saved += 1

#     if saved == 0:
#         return "No stats fetched (API returned no data)"

#     return f"{saved} channel(s) stats saved for {today}"
