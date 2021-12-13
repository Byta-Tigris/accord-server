from hashlib import sha256
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict
from django.http.request import QueryDict
from utils.errors import PasswordValidationError


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
# EG: 20-11-2021-07-09-44-915637 ;; ALL TIMES IN UTC
DATE_TIME_FORMAT = "%d-%m-%Y-%H-%M-%S-%f"


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



def time_to_string(time: datetime) -> str:
    return time.strftime(DATE_TIME_FORMAT)


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