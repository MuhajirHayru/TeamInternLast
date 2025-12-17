from django.core.management.base import BaseCommand
from Teamworkapp.services.facebook_auth import refresh_page_access_token

class Command(BaseCommand):
    help = "Refresh Facebook Page Access Token safely"

    def handle(self, *args, **kwargs):
        token = refresh_page_access_token()
        self.stdout.write(self.style.SUCCESS("Facebook Page Token refreshed"))
