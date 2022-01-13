from typing import Dict, List, Tuple, Union
from rest_framework.serializers import ModelSerializer
from django.db.models import QuerySet
from accounts.models import SocialMediaHandle
from linktree.models import LinkClickCounterModel, LinkwallViewCounterModel
from utils import time_to_string


class SocialMediaHandleSerializer(ModelSerializer):

    class Meta:
        model = SocialMediaHandle
        fields = ("platform", "handle_url", "username", "handle_uid", "avatar",
                  "follower_count", "media_count", "meta_data", "rates", "is_publish_permission_valid")


class LinkwallInsightsSerializer:
    """
    
    Return
     insights: Struct{
         columns: (day, views, clicks)
         rows: List[day_str, views, clicks]
         totals: {}
     },
     link_insights: Struct{
         columns: (link, clicks)
         rows: List[link_name, clicks]
         totals: {}
     }
    
    """

    def __init__(self, views: QuerySet[LinkwallViewCounterModel], clicks: QuerySet[LinkClickCounterModel]) -> None:
        self.views = views
        self.clicks = clicks
    
    @property
    def data(self) -> Dict[str, Dict[str, Union[str, List, Tuple]]]:
        return self._serialize()
    
    def _serialize(self):
        insight_record: Dict[str, int] = {}
        insights_rows: List[List[Union[str, int]]] = []
        link_insight_record: Dict[str, int] = {}
        link_insight_rows: List[List[Union[str, int]]] = []

        for view_counter in self.views:
            date_str = time_to_string(view_counter.created_on)
            if date_str not in insight_record:
                insights_rows.append([date_str, 0, 0])
                insight_record[date_str] = len(insights_rows) - 1
            index = insight_record[date_str]
            insights_rows[index][1] += 1

        
        for click_counter in self.clicks:
            date_str = time_to_string(click_counter.created_on)
            if date_str not in insight_record:
                insights_rows.append([date_str, 0, 0])
                insight_record[date_str] = len(insights_rows) - 1
            index = insight_record[date_str]
            insights_rows[index][2] += 1

            if click_counter.link not in link_insight_record:
                link_insight_rows.append([click_counter.link, 0])
                link_insight_record[date_str] = len(link_insight_rows)  - 1
            index = link_insight_record[click_counter.link]
            link_insight_rows[index][1] += 1

        return {
            "insights": {"columns": ("day", "views", "clicks"), "totals": {}, "rows": insights_rows },
            "link_insights": {"columns": ("link", "clicks"), "totals": {}, "rows": link_insight_rows}
        }

