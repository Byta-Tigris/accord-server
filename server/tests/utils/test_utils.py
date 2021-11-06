from datetime import datetime
from typing import Dict, List, Tuple
import pytest
import unittest
from typing import List
from ...utils import account_id_generator


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
