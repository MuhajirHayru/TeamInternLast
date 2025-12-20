from django.core.management.base import BaseCommand
from Teamworkapp.tasks.facebook_tasks import fetch_daily_facebook_stats

class Command(BaseCommand):
    help = "Fetch Facebook Page statistics"

    def handle(self, *args, **kwargs):
        fetch_daily_facebook_stats()
        self.stdout.write(self.style.SUCCESS("Facebook stats saved"))
