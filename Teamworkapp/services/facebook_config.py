from Teamworkapp.models import FacebookConfig

def get_facebook_config():
    config = FacebookConfig.objects.first()
    if not config:
        raise Exception("Facebook configuration not set in admin")
    return config
