from datetime import datetime
import pytest
from typing import Dict, List, Tuple
from utils import *


@pytest.fixture
def account_emails() -> List[str]:
    return [
        "testemail@gmail.com",
        "bytatigristesting@hotmail.com",
        "xnxxx_reviva@gotmail.com"
    ]


def test_account_id_generator(account_emails):
    for email in account_emails:
        account_id = account_id_generator(email, datetime.now())
        assert len(account_id) == 64, f"{account_id} : account id generation is failing"


@pytest.fixture
def passwords() -> List[Tuple[str, bool]]:
    return [
        ("", False),
        ("hello", False),
        ("pin123", False),
        ("pink1234", True),
        ("pink@1234", True),
        ("12345678", False),
        ("pinklogs@", False),
        ("@1234567", False)
    ]
def test_validate_password(passwords):
    for password in passwords:
        try:
            assert password[1] == validate_password(password[0]), f"Password validation is failing for password {password}"
        except PasswordValidationError as err :
            assert password[1] == False, err


def test_string_to_time():
    time_strs = [
        "20-11-2021-12-46-34-465855",
        "20-11-2021-12-46-34",
        "20-11-2021-12-46",
        "20-11-2021-12",
        "20-11-2021"
    ]
    for time_str in time_strs:
        time = string_to_time(time_str)
        is_valid_output = time.day == 20 and time.month == 11 and time.year == 2021
        assert is_valid_output, "Time format is not working"



def test_seconds_to_datetime_from_time():
    current_time = string_to_time("21-11-2021-15-52-00")
    fixtures = [
        (25, string_to_time("21-11-2021-15-52-25")), # 25 seconds,
        (600, string_to_time("21-11-2021-16-02")), #10 minutes,
        (3600, string_to_time("21-11-2021-16-52-00")), # 1 hours,
        (86400, string_to_time("22-11-2021-15-52-00")), # 1 day,
        (5184000, string_to_time("20-01-2022-15-52-00")), # 60 days
    ]
    for fixture in fixtures:
        time = seconds_to_datetime_from_time(fixture[0], current_time)
        assert time == fixture[1], f"Time is not matiching {time}"