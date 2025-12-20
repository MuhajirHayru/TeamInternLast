from django.core.management.base import BaseCommand
from Teamworkapp.services.youtube_service import fetch_youtube_stats

class Command(BaseCommand):
    help = "Fetch daily YouTube channel statistics"

    def handle(self, *args, **kwargs):
        self.stdout.write("📡 Fetching YouTube stats...")
        result = fetch_youtube_stats()
        self.stdout.write(self.style.SUCCESS(f"✅ {result}"))

