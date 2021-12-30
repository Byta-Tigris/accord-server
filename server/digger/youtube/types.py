from datetime import datetime
import string
from typing import Any, Dict, List, Tuple, Union
import pandas as pd
from utils import DATE_FORMAT, date_to_string, get_current_time, get_datetime_from_youtube_response, get_tag_from_youtube_topics


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

    def __init__(self, key_name: str, value_name: str, dimensions: List[str], key_default: str = "TOTAL") -> None:
        self.key_name = key_name
        self.value_name = value_name
        self.dimensions = dimensions
        self.key_default = key_default
        self.columns = self.dimensions + [self.key_name, self.value_name]
        self._data = {}
    
    @classmethod
    def from_dict(cls, config, data) -> 'MetricRecord':
        record = cls(**config)
        record.set_data(data)
        return record


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
        day = kwargs["day"]
        cols.remove("day")
        if self.key_name not in kwargs:
            kwargs[self.key_name] = self.key_default
        key_arg = []
        for col in cols:
            key_arg.append(kwargs[col])
        return day, {".".join(key_arg): kwargs[self.value_name]}


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



MetricFieldType = Dict[str, Dict[str, Union[int, float]]]

class YTMetrics:

    DATE_TIME_FORMAT = DATE_FORMAT
    subscribed_status_fields = ["views", "likes", "dislikes", "shares", "estimated_minutes_watched",
                                "average_view_duration", "average_view_percentage", "annotation_click_through_rate",
                                "annotation_close_rate", "annotation_impressions", "annotation_clickable_impressions",
                                "annotation_closable_impressions", "annotation_clicks", "annotation_closes", "card_click_rate",
                                "card_teaser_click_rate", "card_impressions", "card_teaser_impressions", "card_clicks", "card_teaser_clicks"
                                ]
    sharing_service_configs = {"key_name": "sharing_service", "value_name": "value", "dimensions": ["day"]}
    age_gender_configs = {"key_name": "age_group", "value_name": "value", "dimensions": ["day", "gender"]}
    normal_configs = {"key_name": "metric", "value_name": "value", "dimensions": ["day"]}
    subscribed_configs = {"key_name": "subscribed_status", "value_name": 'value', "dimensions": ["day"]}

    def get_configs(self, prop_name) -> Dict[str, str]:
        """
        Metric record has different init kwargs for different types of metrics\n
        Method helps in selecting the matching configs according to their dimensions\n

        @param prop_name - Name of the metric
        @return Metric record configurations for each metric
        """
        if prop_name == "viewer_percentage":
            return self.age_gender_configs
        elif prop_name == "shares":
            return self.sharing_service_configs
        elif prop_name in self.subscribed_status_fields:
            return self.subscribed_configs
        return self.normal_configs
    
    def get_metric_record(self, name, value) -> MetricRecord:
        """
        Shorthand wrapper to create metric record using name and value
        """
        if value is None:
            value = {}
        return MetricRecord.from_dict(self.get_configs(name), value)

    def __init__(self, views: MetricFieldType  = None, comments :MetricFieldType  = None, likes: MetricFieldType  = None, 
                dislikes: MetricFieldType  = None, shares: MetricFieldType  = None, estimated_minutes_watched: MetricFieldType = None,
                average_view_duration: MetricFieldType  = None,average_view_percentage: MetricFieldType  = None,subscribers_gained: MetricFieldType  = None,
                subscribers_lost: MetricFieldType  = None,viewer_percentage: MetricFieldType  = None,audience_watch_ratio: MetricFieldType  = None,
                relative_retention_performance: MetricFieldType  = None,card_impressions: MetricFieldType  = None,card_clicks: MetricFieldType  = None,
                card_click_rate: MetricFieldType  = None,card_teaser_impressions: MetricFieldType  = None,card_teaser_clicks: MetricFieldType  = None,
                card_teaser_click_rate: MetricFieldType  = None,annotation_impressions: MetricFieldType  = None,annotation_clickable_impressions: MetricFieldType  = None,
                annotation_clicks: MetricFieldType  = None,annotation_click_through_rate: MetricFieldType  = None,annotation_closable_impressions: MetricFieldType  = None,
                annotation_closes: MetricFieldType  = None,annotation_close_rate: MetricFieldType  = None, **kwargs
    ) -> None:
        self.__dimensions = []
        self.__columns = []
        self.views = self.get_metric_record("views", views).data
        self.comments = self.get_metric_record("comments",comments).data
        self.likes = self.get_metric_record("likes",likes).data
        self.dislikes = self.get_metric_record("dislikes",dislikes).data
        self.shares = self.get_metric_record("shares", shares).data
        self.estimated_minutes_watched = self.get_metric_record("estimated_minutes_watched",estimated_minutes_watched).data
        self.average_view_duration = self.get_metric_record("average_view_duration",average_view_duration).data
        self.average_view_percentage = self.get_metric_record("average_view_percentage", average_view_percentage).data
        self.subscribers_gained = self.get_metric_record("subscribers_gained", subscribers_gained).data
        self.subscribers_lost = self.get_metric_record("subscribers_lost", subscribers_lost).data
        self.viewer_percentage = self.get_metric_record("viewer_percentage", viewer_percentage).data
        self.audience_watch_ratio = self.get_metric_record("audience_watch_ratio", audience_watch_ratio).data
        self.relative_retention_performance = self.get_metric_record("relative_retention_performance", relative_retention_performance).data
        self.card_impressions = self.get_metric_record("card_impressions", card_impressions).data
        self.card_clicks = self.get_metric_record("card_clicks", card_clicks).data
        self.card_click_rate = self.get_metric_record("card_click_rate", card_click_rate).data
        self.card_teaser_impressions = self.get_metric_record("card_teaser_impressions", card_teaser_impressions).data
        self.card_teaser_clicks = self.get_metric_record("card_teaser_clicks", card_teaser_clicks).data
        self.card_teaser_click_rate = self.get_metric_record("card_teaser_click_rate", card_teaser_click_rate).data
        self.annotation_impressions = self.get_metric_record("annotation_impressions", annotation_impressions).data
        self.annotation_clickable_impressions = self.get_metric_record("annotation_clickable_impressions", annotation_clickable_impressions).data
        self.annotation_clicks = self.get_metric_record("annotation_clicks", annotation_clicks).data
        self.annotation_click_through_rate = self.get_metric_record("annotation_click_through_rate", annotation_click_through_rate).data
        self.annotation_closable_impressions = self.get_metric_record("annotation_closable_impressions", annotation_closable_impressions).data
        self.annotation_closes = self.get_metric_record("annotation_closes", annotation_closes).data
        self.annotation_close_rate = self.get_metric_record("annotation_close_rate", annotation_close_rate).data
    

    def add_dimension(self, value: str) -> None:
        self.__dimensions.append(value)
    
    def add_column(self, value: str) -> None:
        self.__columns.append(value)
    
    @classmethod
    def from_yt_response(cls, columnHeaders: List[Dict[str, str]], rows: List[List]) -> 'YTMetrics':
        """
        Convert normal Youtube response to YTMetrics by using columnHeaders and rows provided
        in the response

        @param columHeaders - The {List[Dict[str,str]]} with information about the column it is representing
                              columnHeader['columnType'] defines whether the column is a metric or dimension
        @param rows - {List[List[Union[str, int , float]]]} each row contains data same in the sequence as the columns
        """
        metrics: 'YTMetrics' = cls()
        for column_header in columnHeaders:
            name = metrics.format_argument(column_header["name"])
            if column_header["columnType"] == "DIMENSION":
                metrics.add_dimension(name)
            metrics.add_column(name)
        for row in rows:
            metrics.consume_row(row)
        return metrics
    
    @staticmethod
    def format_argument(argument_name: str) -> str:
        """
        Formats argument name from camelCase to snake_case
        """
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
        """
        Converts each row into dict, which is later added to the metrics.
        Each time the metric is converted into MetricRecord from dict and again to dict for setting
        If any of the column is dimension then it will be same for all the metric values in the row, thus
        we needed to create dimensions dict

        @params data - {List[Union[str,int, float]]} row with data arranged according to column
        @return None

        """
        dimensions = {}
        for index, value in enumerate(data):
            column = self.__columns[index]
            if column in self.__dimensions:
                if column == "day":
                    dimensions[column] = date_to_string(value) if isinstance(value, datetime) else value
                else:
                    dimensions[column] = value
            else:
                argument: MetricRecord = self.get_metric_record(column, getattr(self, column, None))
                data = dimensions | {"value": value}
                if "day" not in data:
                    data["day"] = date_to_string(get_current_time())
                argument.add(**data)
                setattr(self, column, argument.data)
    
    def to_dict(self) -> Dict[str, MetricFieldType]:
        kwargs = {}
        for key, value in vars(self).items():
            if "_YTMetrics" not in key and key[0] != "_":
                kwargs[key] = value
        return kwargs
    
    def __add__(self, other: 'YTMetrics') -> 'YTMetrics':
        other_kwargs = other.to_dict()
        my_kwargs = self.to_dict()
        for key, value in other_kwargs.items():
            for day, data in value.items():
                if day not in my_kwargs[key]:
                    my_kwargs[key][day] = {}
                my_kwargs[key][day] |= data
        return YTMetrics(**my_kwargs)

