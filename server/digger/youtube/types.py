from datetime import datetime
import string
from typing import Any, Dict, List, Tuple, Union
import pandas as pd
from utils import YOUTUBE_RESPONSE_DATE_FORMAT, get_datetime_from_youtube_response, get_tag_from_youtube_topics, time_to_string


class YTChannel:
    def __init__(self, id: str, snippet: Dict = None, statistics: Dict = None, topicDetails: Dict = None, auditDetails: Dict = None, **kwargs) -> None:
        self.id = id
        self.handle_url = f"https://www.youtube.com/channel/{self.id}"
        self.is_snippet_none = snippet == None
        self.is_statistics_none = statistics == None
        self.is_topic_details_none = topicDetails == None
        self.is_audit_details_none = auditDetails == None
        self.meta_data = {}
        if not self.is_snippet_none:
            self.title = snippet.get("title", None)
            self.description = snippet.get("description", "")
            self.published_at = snippet.get("publishedAt", None)
            if self.published_at != None:
                self.created_on = get_datetime_from_youtube_response(
                    self.published_at)
            thumbnails = snippet.get("thumbnails", None)
            if thumbnails != None:
                if "high" in thumbnails:
                    self.avatar = thumbnails["high"]["url"]
                elif "medium" in thumbnails:
                    self.avatar = thumbnails["medium"]["url"]
                elif "default" in thumbnails:
                    self.avatar = thumbnails["default"]["url"]
        if not self.is_statistics_none:
            self.followers_count = statistics.get("subscriberCount", 0)
            self.medias_count = statistics.get("videoCount")
        if not self.is_topic_details_none and "topicCategories" in topicDetails:
            self.tags = []
            for topic in topicDetails["topicCategories"]:
                self.tags.append(get_tag_from_youtube_topics(topic))
            self.meta_data["tags"] = self.tags
        if not self.is_audit_details_none:
            self.meta_data["overall_goog_standing"] = auditDetails.get(
                "overallGoodStanding", False)
            self.meta_data["community_guideline_good_standing"] = auditDetails.get(
                "communityGuidelinesGoodStanding", False)
            self.meta_data["copyright_strikes_good_standing"] = auditDetails.get(
                "copyrightStrikesGoodStanding", False)
            self.meta_data["content_id_claims_good_standing"] = auditDetails.get(
                "contentIdClaimsGoodStanding", False)


class YTVideo:

    def __init__(self, id: str, snippet: Dict = None, status: Dict = None, statistics: Dict = None,
                 topicDetails: Dict = None, **kwargs) -> None:
        self.id = id
        self.is_snippet_none = snippet == None
        self.is_status_none = status == None
        self.is_statistics_none = statistics == None
        self.is_topic_details_none = topicDetails == None
        self.meta_data = {"tags": []}
        if not self.is_snippet_none:
            self.title = snippet.get("title", "")
            published_at = snippet.get("publishedAt", None)
            self.channel_id = snippet.get("channelId", None)
            if published_at:
                self.published_at = get_datetime_from_youtube_response(
                    published_at)
            self.description = snippet.get("description", "")
            thumbnails = snippet.get("thumbnails", None)
            if thumbnails != None:
                if "high" in thumbnails:
                    self.thumbnail = thumbnails["high"]["url"]
                elif "medium" in thumbnails:
                    self.thumbnail = thumbnails["medium"]["url"]
                elif "default" in thumbnails:
                    self.thumbnail = thumbnails["default"]["url"]
            self.meta_data["tags"] += snippet.get("tags", [])
        if not self.is_status_none:
            self.meta_data["upload_status"] = status.get("upload_status", None)
            self.meta_data["made_for_kids"] = status.get("madeForKids", False)
        if not self.is_statistics_none:
            self.impressions = statistics.get("viewCount", 0)
            likes, dislikes, favorites, comments = statistics.get("likeCount", 0), statistics.get(
                "dislikeCount", 0), statistics.get("favoriteCount", 0), statistics.get("commentCount", 0)
            self.engagement = likes + dislikes + comments + favorites
            self.positive_engagement = likes + favorites + comments
            self.negative_engagement = dislikes
        if not self.is_topic_details_none and "topicCategories" in topicDetails:
            self.tags = []
            for topic in topicDetails["topicCategories"]:
                self.tags.append(get_tag_from_youtube_topics(topic))
            self.meta_data["tags"] = self.tags


class MetricRecord(object):

    """
    Dict based Datastructure to contain record of data inside a record
    Thus the weeky metric [JSOnField] will store these data making it easy to query and update
    for e.g 
        - '2020-10-07__M__age18_24' will return 0.38 
        - '2020-10-07__F' will return {"age36_50": 0.8}

    """

    def __init__(self, key_name: str, value_name: str, dimensions: List[str], key_default: str = None) -> None:
        self.key_name = key_name
        self.value_name = value_name
        self.dimensions = dimensions
        self.key_default = key_default
        self.columns = self.dimensions + [self.key_name, self.value_name]
        self._data = {}


    def set_data(self, data) -> None:
        self._data = data
    
    def __contains__(self, substr: str) -> bool:
        
        if "." in substr:
            patterns = substr.split(".")
            first_key, rest_key = patterns[0], ".".join(patterns[1:])
            return first_key in self._data and (value := self._data[first_key]) != None and rest_key in value
        return substr in self._data
    

    def __getitem__(self, key: str) -> Any:
        if "." in key:
            patterns = key.split(".")
            first_key, rest_key = patterns[0], ".".join(patterns[1:])
            return self._data[first_key][rest_key]
        return self._data[key]

    def format_kwarg(self, **kwargs) -> Dict:
        data = {kwargs[self.key_name]: kwargs[self.value_name]}
        for dimension_name in reversed(self.dimensions):
            data = {kwargs[dimension_name]: data}
        return data

    def _convert(self, **kwargs) -> Tuple[str, Dict]:
        cols = self.columns.copy()
        cols.remove(self.value_name)
        cols.remove("day")
        if self.key_default is not None:
            kwargs[self.key_name] = self.key_default
        key_arg = []
        for col in cols:
            key_arg.append(kwargs[col])
        return kwargs["day"], {".".join(key_arg): kwargs[self.value_name]}


    def add(self, **kwargs) -> None:
        day, value = self._convert(**kwargs)
        if day in self._data:
            self._data[day] |= value
        else:
            self._data[day] = value

    def extend(self, ls: List[Dict]) -> None:
        for data in ls:
            self.add(**data)

    @property
    def data(self) -> Dict:
        return self._data



class YTMetrics:

    DATE_TIME_FORMAT = YOUTUBE_RESPONSE_DATE_FORMAT
    subscribed_status_fields = ["views", "likes", "dislikes", "shares", "estimated_minutes_watched",
                                "average_view_duration", "average_view_percentage", "annotation_click_through_rate",
                                "annotation_close_rate", "annotation_impressions", "annotation_clickable_impressions",
                                "annotation_closable_impressions", "annotation_clicks", "annotation_closes", "card_click_rate",
                                "card_teaser_click_rate", "card_impressions", "card_teaser_impressions", "card_clicks", "card_teaser_clicks"
                                ]

    def __init__(self, columnHeaders: List[Dict[str, str]], rows: List[List]) -> None:
        self.views: List[Dict] = None
        self.comments: List[Dict] = None
        self.likes: List[Dict] = None
        self.dislikes: List[Dict] = None
        self.shares: List[Dict] = None
        self.estimated_minutes_watched: List[Dict] = None
        self.average_view_duration: List[Dict] = None
        self.average_view_percentage: List[Dict] = None
        self.subscribers_gained: List[Dict] = None
        self.subscribers_lost: List[Dict] = None
        self.viewer_percentage: List[Dict] = None
        self.audience_watch_ratio: List[Dict] = None
        self.relative_retention_performance: List[Dict] = None
        self.card_impressions: List[Dict] = None
        self.card_clicks: List[Dict] = None
        self.card_click_rate: List[Dict] = None
        self.card_teaser_impressions: List[Dict] = None
        self.card_teaser_clicks: List[Dict] = None
        self.card_teaser_click_rate: List[Dict] = None
        self.annotation_impressions: List[Dict] = None
        self.annotation_clickable_impressions: List[Dict] = None
        self.annotation_clicks: List[Dict] = None
        self.annotation_click_through_rate: List[Dict] = None
        self.annotation_closable_impressions: List[Dict] = None
        self.annotation_closes: List[Dict] = None
        self.annotation_close_rate: List[Dict] = None

        self.__dimensions = []
        self.__columns = []

        for column_header in columnHeaders:
            name = self.format_argument(column_header["name"])
            if column_header["columnType"] == "DIMENSION":
                self.__dimensions.append(name)
            self.__columns.append(name)

        for row in rows:
            self.consume_row(row)

    @staticmethod
    def format_argument(argument_name: str) -> str:
        chunks = []
        last_splice_index = 0
        for index in range(len(argument_name)):
            if argument_name[index] in string.ascii_uppercase:
                chunks.append(argument_name[last_splice_index: index].lower())
                last_splice_index = index
            elif index + 1 == len(argument_name):
                chunks.append(argument_name[last_splice_index:].lower())
        if len(chunks) == 0:
            return argument_name
        return '_'.join(chunks)

    def consume_row(self, data: List[Union[str, int, float]]) -> None:
        dimensions = {}
        for index, value in enumerate(data):
            column = self.__columns[index]
            if column in self.__dimensions:
                if column == "day":
                    dimensions[column] = time_to_string(value)
                else:
                    dimensions[column] = value
            else:
                argument = getattr(self, column)
                if argument is None:
                    argument = []
                argument.append(dimensions | {"value": value})
                setattr(self, column, argument)
