from django.apps import AppConfig
import threading

class TeamworkappConfig(AppConfig):
    name = "Teamworkapp"

    def ready(self):
      
        def run():
            try:
                from Teamworkapp.services.youtube_service import fetch_youtube_stats
                from Teamworkapp.tasks.facebook_tasks import fetch_daily_facebook_stats

                fetch_youtube_stats()
                fetch_daily_facebook_stats()

            except Exception as e:
                print("❌ Failed to update stats on startup:", e)

        threading.Thread(target=run).start()
