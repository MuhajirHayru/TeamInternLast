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
#admin.site.register(YouTubeStats)
admin.site.register(TelegramChannel)
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
    # admin.py
from django.contrib import admin
from .models import TikTokProfile
from .scraper import scrape_tiktok_profile
import asyncio

@admin.register(TikTokProfile)
class TikTokProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "followers", "following", "likes", "videos", "last_updated")
    search_fields = ("username",)

    def save_model(self, request, obj, form, change):
        # always scrape on save (new or username changed)
        stats = asyncio.run(scrape_tiktok_profile(obj.username))
        obj.followers = stats["followers"]
        obj.following = stats["following"]
        obj.likes = stats["likes"]
        obj.videos = stats["videos"]
        super().save_model(request, obj, form, change)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # optional: refresh when opening the admin detail page
        obj = self.get_object(request, object_id)
        if obj:
            stats = asyncio.run(scrape_tiktok_profile(obj.username))
            obj.followers = stats["followers"]
            obj.following = stats["following"]
            obj.likes = stats["likes"]
            obj.videos = stats["videos"]
            obj.save()
        return super().change_view(request, object_id, form_url, extra_context)