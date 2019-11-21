import pytest

from intellipush import (
    client
)

test_contact = {
    'name': 'Test Testerson',
    'countrycode': '0047',
    'phonenumber': '69336286',
    'email': 'test@example.com',
    'company': 'Test Inc.',
    'sex': 'male',
    'country': 'Sweden',
    'param1': 'this_is_param1',
    'param2': 'this_is_param2',
    'param3': 'this_is_param3',
}


@pytest.fixture
def intellipush(api_details):
    api_id, api_secret = api_details
    return client.Intellipush(key=api_id, secret=api_secret)


@pytest.fixture
def created_contact(intellipush):
    return intellipush.create_contact(
        **test_contact
    )


def test_create_contact(intellipush):
    result = intellipush.create_contact(
        **test_contact
    )

    assert 'id' in result
    assert result['id'] is not None
    assert int(result['id']) > 0

    fetched = intellipush.contact(result['id'])

    assert fetched

    for field, value in test_contact.items():
        assert fetched[field] == value


@pytest.mark.skip('Currently generates a 500 error?')
def test_contact_by_phone_number(intellipush, created_contact):
    fetched = intellipush.contact(countrycode=created_contact['countrycode'], phonenumber=created_contact['phonenumber'])
    assert fetched['contact_id'] == created_contact['id']


def test_delete_contact(intellipush, created_contact):
    fetched = intellipush.contact(created_contact['id'])
    assert fetched

    intellipush.delete_contact(contact_id=created_contact['id'])

    contact = intellipush.contact(created_contact['id'])

    assert contact is None
    assert intellipush.last_error_code == 508


def test_current_user(intellipush):
    user = intellipush.current_user()
    assert user
