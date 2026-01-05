from django.apps import AppConfig
import os

class TeamworkappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Teamworkapp'

    def ready(self):
        from.  import signals