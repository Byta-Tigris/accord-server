import os

def test_env_working():
    assert os.getenv('IS_ENV_FILE') == '1'