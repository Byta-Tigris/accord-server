from datetime import datetime
import string
from typing import Any, Dict, List, Union
import pandas as pd
from utils import YOUTUBE_RESPONSE_DATE_FORMAT, get_datetime_from_youtube_response, get_tag_from_youtube_topics


class YTChannel:
    def __init__(self,id : str, snippet: Dict = None,statistics: Dict = None, topicDetails: Dict = None,auditDetails: Dict = None,**kwargs) -> None:
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
                self.created_on = get_datetime_from_youtube_response(self.published_at)
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
            self.meta_data["overall_goog_standing"] = auditDetails.get("overallGoodStanding", False)
            self.meta_data["community_guideline_good_standing"] = auditDetails.get("communityGuidelinesGoodStanding", False)
            self.meta_data["copyright_strikes_good_standing"] = auditDetails.get("copyrightStrikesGoodStanding", False)
            self.meta_data["content_id_claims_good_standing"] = auditDetails.get("contentIdClaimsGoodStanding", False)

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
                self.published_at = get_datetime_from_youtube_response(published_at)
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
            likes, dislikes, favorites, comments = statistics.get("likeCount", 0), statistics.get("dislikeCount", 0), statistics.get("favoriteCount", 0), statistics.get("commentCount", 0)
            self.engagement = likes + dislikes + comments + favorites
            self.positive_engagement = likes + favorites + comments
            self.negative_engagement = dislikes
        if not self.is_topic_details_none and "topicCategories" in topicDetails:
            self.tags = []
            for topic in topicDetails["topicCategories"]:
                self.tags.append(get_tag_from_youtube_topics(topic))
            self.meta_data["tags"] = self.tags


class YTMetrics:

    DATE_TIME_FORMAT = YOUTUBE_RESPONSE_DATE_FORMAT

    def __init__(self, columnHeaders: List[Dict[str,str]], rows: List[List]) -> None:
        self.views = None
        self.comments = None
        self.likes = None
        self.dislikes = None
        self.shares = None
        self.estimated_minutes_watched = None
        self.average_view_duration = None
        self.average_view_percentage = None
        self.subscribers_gained = None
        self.subscribers_lost = None
        self.viewer_percentage = None
        self.audience_watch_ratio = None
        self.relative_retention_performance = None
        self.card_impressions = None
        self.card_clicks = None
        self.card_click_rate = None
        self.card_teaser_impressions = None
        self.card_teaser_clicks = None
        self.card_teaser_click_rate = None
        self.annotation_impressions = None
        self.annotation_clickable_impressions = None
        self.annotation_clicks = None
        self.annotation_click_through_rate = None
        self.annotation_closable_impressions = None
        self.annotation_closes = None
        self.annotation_close_rate = None

        self.__columns = list(map(lambda column: self.format_argument(column["name"]), columnHeaders))

        for row in rows:
            self.digest_row_data(row)

    @staticmethod
    def format_argument(argument_name: str) -> str:
        chunks = []
        last_splice_index = 0
        for index in range(len(argument_name)):
            if argument_name[index] in string.ascii_uppercase:
                chunks.append(argument_name[last_splice_index: index].lower())
                last_splice_index = index
            elif index +1 == len(argument_name):
                chunks.append(argument_name[last_splice_index: ].lower())
        if len(chunks) == 0:
            return argument_name
        return '_'.join(chunks)
    
        
    def digest_row_data(self, data: List[Union[str, int, float]]) ->None:
        allowed_metrics = vars(self)
        meta = {}
        for index, datapoint in enumerate(data):     
            argument_name = self.__columns[index]
            if argument_name not in allowed_metrics.keys():
                meta[argument_name] = datapoint if argument_name != "day" else datetime.strptime(datapoint, self.DATE_TIME_FORMAT)
            else:
                argument = getattr(self, argument_name, None)
                if argument == None:
                    argument = []
                meta["value"] = datapoint
                argument.append(meta)
                setattr(self, argument_name, argument)




class MetricRecord(object):

    """
    Dict based Datastructure to contain record of data inside a record

    MetricRecord({
        "day_1": {
            "M": {
                "age18_24": 0.38,
                "age36-50": 0.36
            },
            "F": {
                "age36_50": 0.8
            }
        },
        "day_2": {
            "F": {
                "age18_24": 0.5
            }
        }
    })
    Thus the weeky metric [JSOnField] will store these data making it easy to query and update
    for e.g 
        - '2020-10-07__M__age18_24' will return 0.38 
        - '2020-10-07__F' will return {"age36_50": 0.8}

    """

    def __init__(self, key_name: str, value_name: str, dimensions: List[str]) -> None:
        self.key_name = key_name
        self.value_name = value_name
        self.dimensions = dimensions
        self.columns = self.dimensions + [self.key_name, self.value_name]
        self._df = pd.DataFrame([], columns=self.columns)
        self._data = {}
    
    def convert_kwargs_to_row(self, **kwargs) -> List:
        data = []
        for dimension_name in self.columns:
            data.append(kwargs[dimension_name])
        return data
    
    def add_data_to_df(self, **kwargs) -> None:
        row = self.convert_kwargs_to_row(**kwargs)
        self._df.loc[len(self._df.index)] = row
    
    @property
    def df(self) -> pd.DataFrame:
        return self._df
    

    def format_kwarg(self, **kwargs) -> Dict:
        data = {kwargs[self.key_name]: kwargs[self.value_name]}
        for dimension_name in reversed(self.dimensions):
            data = {kwargs[dimension_name]: data}
        return data
    
    
    def _add(self, **kwargs) -> Dict:
        traced_path = []
        traced_data = []
        data = self._data
        prototype_data = self.format_kwarg(**kwargs)
        for dimension_name in self.dimensions:
            if dimension_name in kwargs and kwargs[dimension_name] in data:
                traced_path.append(kwargs[dimension_name])
                traced_data.append(data[kwargs[dimension_name]])
                data = data[kwargs[dimension_name]]
                prototype_data = prototype_data[kwargs[dimension_name]]
        data = prototype_data
        for i, _d in enumerate(reversed(traced_data)):
            index = len(traced_data) - (i +1)
            data = {traced_path[index]: _d | data}
        return data
    
    def add(self,in_df: bool = False, **kwargs) -> None:
        self._data |= self._add(**kwargs)
        if in_df:
            self.add_data_to_df(**kwargs)
    
    @property
    def data(self) -> Dict:
        return self._data
    
    def __contains__(self, name: str) -> bool:
        data = self._data
        for chunk in name.split("__"):
            if data != None and chunk in data:
                data = data.get(chunk, None)
            else:
                return False
        return True
        
    
    def __getitem__(self, items) -> Dict:
        if isinstance(items, (list, tuple)):
            return self.get("__".join(items))
        return self.get(items)
    
    def get(self, name:str) -> Any:
        data = self._data
        visited_chunk = []
        for chunk in name.split("__"):
            visited_chunk.append(chunk)
            if data != None and  chunk in data and  (value := data.get(chunk, None)) != None:
                data = value
            else:
                raise KeyError(f"{'__'.join(visited_chunk)} does not exists")
        return data

    


class YTMetricRecord(MetricRecord):
    
    def __init__(self, key_name = "metric", value_name = "value", dimensions = ["day"]) -> None:
        super().__init__(key_name, value_name, dimensions)




        

        

        
            




        
        
        