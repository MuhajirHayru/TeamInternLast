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
admin.site.register(YouTubeChannel)
admin.site.register(YouTubeStats)
admin.site.register(FacebookToken1)
from django.utils.html import format_html
from .models import PageStats

@admin.register(PageStats)
class PageStatsAdmin(admin.ModelAdmin):
    list_display = ("date", "views", "followers", "likes")

    def changelist_view(self, request, extra_context=None):
        qs = PageStats.objects.all().order_by("date")
        dates = [obj.date.strftime("%Y-%m-%d") for obj in qs]
        views = [obj.views for obj in qs]
        followers = [obj.followers for obj in qs]
        likes = [obj.likes for obj in qs]

        extra_context = extra_context or {}
        extra_context["chart_data"] = {
            "labels": dates,
            "datasets": [
                {"label": "Views", "data": views},
                {"label": "Followers", "data": followers},
                {"label": "Likes", "data": likes},
            ]
        }
        return super().changelist_view(request, extra_context=extra_context)
    
@admin.register(FacebookConfig)
class FacebookConfigAdmin(admin.ModelAdmin):
    list_display = ("page_id", "updated_at")