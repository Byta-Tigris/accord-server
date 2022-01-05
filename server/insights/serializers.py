from rest_framework.serializers import ModelSerializer

from accounts.models import SocialMediaHandle


class SocialMediaHandleSerializer(ModelSerializer):

    class Meta:
        model = SocialMediaHandle
        fields = ("platform", "handle_url", "username", "handle_uid", "avatar",
                  "follower_count", "media_count", "meta_data", "rates", "is_publish_permission_valid")
