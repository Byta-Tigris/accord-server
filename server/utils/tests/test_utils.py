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
        