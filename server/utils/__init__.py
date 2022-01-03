from hashlib import sha256
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, Tuple, Union
from django.http.request import QueryDict
from utils.errors import PasswordValidationError
import os


def account_id_generator(email: str, entity_type: str) -> str:
    """Generate account hash using email and entity_type [Returns string]"""
    hash_algo = sha256()
    hash_algo.update(f"{email}__{entity_type}".encode())
    return hash_algo.hexdigest()


def validate_password(password: str) -> bool:
    """Password must be greater than 8 characters and less than 20, must have alphabets and numbers.\n
    special symbols are allowed are only allowed special characters\n
    raises PasswordValidationError if wrong\n
    Returns True"""
    if (
        5 < len(password) < 21
        and any(char.isdigit() for char in password)
        and any(char.isalpha() for char in password)
    ):
        return True
    raise PasswordValidationError(password)


# DATE-MONTH-YEAR-HOUR-MINUTE-SECOND-MICROSECOND ---- UTC_OFFSET = 0
# EG: 20-11-2021T07-09-44-915637 ;; ALL TIMES IN UTC
DATE_TIME_FORMAT = "%d-%m-%YT%I:%M:%S"
DATE_FORMAT = "%d-%m-%Y"
FACEBOOK_RESPONSE_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
YOUTUBE_RESPONSE_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
YOUTUBE_RESPONSE_DATE_FORMAT = "%Y-%m-%d"


def get_current_time() -> datetime:
    return datetime.utcnow()


def get_modified_time(
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
    time: datetime = datetime.utcnow(),
) -> datetime:
    seconds += 60 * minutes
    seconds += hours * 60 * 60
    seconds += days * 24 * 60 * 60
    return timedelta(seconds=seconds) + time


def get_modified_time_wrapper(
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
    time: datetime = datetime.utcnow(),
) -> Callable[[], datetime]:
    def inner():
        return get_modified_time(seconds=seconds, minutes=minutes,
                                 hours=hours, days=days, time=time)
    return inner

def get_handle_metrics_expire_time(time: datetime = get_current_time()) -> datetime:
    return get_modified_time(days=7, time=time)

def get_datetime_from_facebook_response(time_str: str) -> datetime:
    return datetime.strptime(time_str, FACEBOOK_RESPONSE_DATE_TIME_FORMAT)

def get_datetime_from_youtube_response(time_str: str) -> datetime:
    return datetime.strptime(time_str, YOUTUBE_RESPONSE_DATE_TIME_FORMAT)

def get_tag_from_youtube_topics(topic:str) -> str:
    split_topic_url = topic.split("/")
    topic_name = split_topic_url[-1]
    split_topic_name = topic_name.split("_")
    fresh_name = " ".join(split_topic_name)
    return fresh_name.title()

def get_desired_resolution_image_from_youtube_thumbnail_url(url: str, res: str) -> str:
    record = {"high": "s800", "medium": "s240", "default": "s88"}
    reses = ["s800", "s240", "s88"]
    for resolution in reses:
        if resolution in url:
            return url.replace(resolution, record[res])

def time_to_string(time: datetime) -> str:
    return time.strftime(DATE_TIME_FORMAT)

def date_to_string(time: datetime) -> str:
    return time.strftime(DATE_FORMAT)



def string_to_time(time_str: str) -> datetime:
    time_split = time_str.split("-")
    format_split = DATE_TIME_FORMAT.split("-")
    time_format = format_split[: len(time_split)]
    return datetime.strptime(time_str, "-".join(time_format))


def date_from_date_time(time: datetime) -> date:
    return time.date()


def seconds_to_datetime_from_time(secs: int, current_dt: datetime) -> datetime:
    return current_dt + timedelta(seconds=secs)


def seconds_to_datetime_from_now(secs: int) -> datetime:
    time = datetime.utcnow()
    return seconds_to_datetime_from_time(secs, time)


def querydict_to_dict(querydict: QueryDict) -> Dict[str, Any]:
    data = {}
    for key, value in querydict.items():
        data[key] = value
    return data



def get_secret(name: str) -> str:
    return os.getenv(name)


def reformat_age_gender(data: Dict[str, int]) -> Dict[str, int]:
        gender_group = {"M": 0, "F": 0, "U": 0}
        age_group = {"age13-17": 0, "age18-24":0, "age25-34": 0, "age35-44": 0, "age45-54": 0, "age55-64": 0, "age65-": 0}
        for age_gender_name, value in data.items():
            gender, age = age_gender_name.split(".")
            gender_group[gender] += value
            age_group[f"age{age}"] += value
        return data | age_group | gender_group


def merge_metric(*metrics_array: Dict[str, int]) -> Dict[str, Union[int, float]]:
        data = {}
        for metrics in metrics_array:
            for key, value in metrics.items():
                if key not in data:
                    data[key] = 0
                data[key] += value
        return data


def is_in_debug_mode() -> bool:
    return os.getenv('DEBUG', False) == 'True'