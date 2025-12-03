# teamworkapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

admin.site.register(Pictures)
admin.site.register(Approval)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(News)
admin.site.register(Event)
admin.site.register(CompetitionDetail)
admin.site.register(JobAnnouncement)
admin.site.register(PostComment)
admin.site.register(PostAnalytics)
admin.site.register(PostReaction)
admin.site.register(PostRating)