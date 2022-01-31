"""
All Celery task are defined here
"""

from celery import shared_task
from django.db.models import QuerySet
from accounts.models import SocialMediaHandle
from digger.base.digger import Digger
from digger.instagram.digger import InstagramDigger
from digger.youtube.digger import YoutubeDigger
from utils.types import Platform
from log_engine.log import logger




def update_handle_analytics(digger: Digger, social_media_handle: SocialMediaHandle) -> None:
    digger.update_handle_data(social_media_handle)
    digger.update_handle_insights(social_media_handle)


@shared_task
def update_analytics() -> None:
    instagram_digger = InstagramDigger()
    youtube_digger = YoutubeDigger()
    social_media_handle_queryset: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(is_disabled=False)
    try:
        for social_media_handle in social_media_handle_queryset:
            if social_media_handle.platform == Platform.Instagram:
                update_handle_analytics(instagram_digger, social_media_handle)
            elif social_media_handle.platform == Platform.Youtube:
                update_handle_analytics(youtube_digger, social_media_handle)
    except Exception as exc:
        logger.error(exc)


