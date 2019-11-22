import pytest


def pytest_addoption(parser):
    parser.addoption('--api-id', action='store')
    parser.addoption('--api-secret', action='store')
    parser.addoption('--live-country-code', action='store')
    parser.addoption('--live-phone-number', action='store')


@pytest.fixture(scope='session')
def api_details(request):
    api_id = request.config.option.api_id
    api_secret= request.config.option.api_secret

    if not api_id or not api_secret:
        pytest.skip('--api-id and --api-secret must both be provided')

    return api_id, api_secret