import pytest
import uuid


@pytest.fixture
def host() -> str:
    return "127.0.0.1"


@pytest.fixture
def port() -> int:
    return 5000


@pytest.fixture
def random_account_id() -> str:
    return str(uuid.uuid4())[:6]


@pytest.fixture
def stress_threads() -> int:
    return 10


@pytest.fixture
def stress_processes() -> int:
    return 10


@pytest.fixture
def stress_calls() -> int:
    return 50
