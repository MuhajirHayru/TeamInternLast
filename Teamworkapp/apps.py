from django.apps import AppConfig
import os

class TeamworkappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Teamworkapp'

    def ready(self):
        from.  import signals
      
        # Avoid double execution by autoreloader
        if os.environ.get("RUN_MAIN") != "true":
            return

        from Teamworkapp.tasks.facebook_tasks import fetch_daily_facebook_stats

        try:
            print("🚀 Server started → updating Facebook stats")
            fetch_daily_facebook_stats()
        except Exception as e:
            print("❌ Failed to update Facebook stats on startup:", e)