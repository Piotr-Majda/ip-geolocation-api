import pytest


@pytest.fixture
def use_real_api(request):
    return request.config.getoption("--use-real-api")


@pytest.fixture
def api_key(request):
    return request.config.getoption("--api-key")
