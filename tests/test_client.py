import datetime
import random
import string
import pytest

from intellipush import (
    client
)

from intellipush.messages import (
    SMS,
)

test_contact = {
    'name': 'Test Testerson',
    'countrycode': '0047',
    'phonenumber': '91753699',
    'email': 'test@example.com',
    'company': 'Test Inc.',
    'sex': 'male',
    'country': 'Sweden',
    'param1': 'this_is_param1',
    'param2': 'this_is_param2',
    'param3': 'this_is_param3',
}

updated_contact = {
    'name': 'Feast Feasterson',
    'countrycode': '0047',
    'phonenumber': '91753699',
    'email': 'feast@example.com',
    'company': 'Feast Inc.',
    'sex': 'female',
    'country': 'Norway',
    'param1': 'this_was_param1',
    'param2': 'this_was_param2',
    'param3': 'this_was_param3',
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


@pytest.fixture
def created_contact_2(intellipush):
    return intellipush.create_contact(
        **updated_contact
    )


@pytest.fixture
def created_contact_list(intellipush):
    name = ''.join(random.choices(string.ascii_letters, k=10))
    return intellipush.create_contact_list(name=name)


@pytest.mark.live_test
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


@pytest.mark.live_test
def test_contact_by_phone_number(intellipush, created_contact):
    fetched = intellipush.contact(countrycode=created_contact['countrycode'], phonenumber=created_contact['phonenumber'])
    assert fetched['id'] == created_contact['id']


@pytest.mark.live_test
def test_delete_contact(intellipush, created_contact):
    fetched = intellipush.contact(created_contact['id'])
    assert fetched

    intellipush.delete_contact(contact_id=created_contact['id'])

    contact = intellipush.contact(created_contact['id'])

    assert contact is None
    assert intellipush.last_error_code == 508


@pytest.mark.live_test
def test_update_contact(intellipush, created_contact):
    update_command = {
        'contact_id': created_contact['id'],
    }
    update_command.update(updated_contact)

    updated = intellipush.update_contact(**update_command)
    fetched = intellipush.contact(created_contact['id'])

    assert fetched

    for field, value in updated_contact.items():
        assert fetched[field] == value


@pytest.mark.live_test
def test_create_contact_list(intellipush):
    name = ''.join(random.choices(string.ascii_letters, k=10))
    created = intellipush.create_contact_list(name=name)

    assert created
    assert created['id']
    assert created['name'] == name

    intellipush.delete_contact_list(contact_list_id=created['id'])


@pytest.mark.live_test
def test_get_contact_list(intellipush, created_contact_list):
    fetched = intellipush.contact_list(contact_list_id=created_contact_list['id'])

    assert fetched['name'] == created_contact_list['name']
    assert fetched['id'] == created_contact_list['id']

    intellipush.delete_contact_list(contact_list_id=created_contact_list['id'])


@pytest.mark.live_test
def test_manipulate_contact_list(intellipush, created_contact_list, created_contact):
    result = intellipush.add_to_contact_list(
        contact_list_id=created_contact_list['id'],
        contact_id=created_contact['id']
    )

    assert result['contactlist_id'] == created_contact_list['id']
    assert result['contact_id'] == created_contact['id']

    fetched = intellipush.contact_list(contact_list_id=created_contact_list['id'])
    assert len(fetched['contacts']) == 1

    result = intellipush.remove_from_contact_list(contact_list_id=created_contact_list['id'], contact_id=created_contact['id'])

    fetched = intellipush.contact_list(contact_list_id=created_contact_list['id'])
    assert len(fetched['contacts']) == 0

    intellipush.delete_contact_list(contact_list_id=created_contact_list['id'])


@pytest.mark.live_test
def test_delete_contact_list(intellipush, created_contact_list):
    intellipush.delete_contact_list(contact_list_id=created_contact_list['id'])
    contact_list = intellipush.contact_list(contact_list_id=created_contact_list['id'])

    assert not contact_list
    assert intellipush.last_error_code == 501


@pytest.mark.live_test
def test_update_contact_list(intellipush, created_contact_list):
    name = ''.join(random.choices(string.ascii_letters, k=10))
    updated = intellipush.update_contact_list(contact_list_id=created_contact_list['id'], name=name)
    assert updated['name'] == name

    fetched = intellipush.contact_list(contact_list_id=created_contact_list['id'])
    assert fetched['name'] == name

    intellipush.delete_contact_list(contact_list_id=created_contact_list['id'])


@pytest.mark.live_test
def test_contact_list_size(intellipush, created_contact_list, created_contact):
    result = intellipush.add_to_contact_list(
        contact_list_id=created_contact_list['id'],
        contact_id=created_contact['id']
    )

    size = intellipush.contact_list_size(contact_list_id=created_contact_list['id'])
    assert size == 1

    intellipush.delete_contact_list(contact_list_id=created_contact_list['id'])


@pytest.mark.live_test
def test_contacts_not_in_contact_list(intellipush, created_contact_list, created_contact, created_contact_2):
    result = intellipush.add_to_contact_list(
        contact_list_id=created_contact_list['id'],
        contact_id=created_contact['id']
    )

    assert False

@pytest.mark.live_test
def test_current_user(intellipush):
    user = intellipush.current_user()
    assert user


@pytest.mark.live_test
def test_sms_simple_live(intellipush, request):
    if not request.config.option.live_country_code or \
            not request.config.option.live_phone_number:
        pytest.skip('Requires --live-country-code and --live-phone-number')

    message = 'Hello from intellipush test suite'

    result = intellipush.sms(
        countrycode=request.config.option.live_country_code,
        phonenumber=request.config.option.live_phone_number,
        message=message,
    )

    assert result['id']
    assert result['text_message'] == message
    assert result['method'] == 'sms'


def test_sms_simple(intellipush, mocker):
    mocked_post = mocker.patch.object(intellipush, '_post')

    intellipush.sms(
        countrycode=test_contact['countrycode'],
        phonenumber=test_contact['phonenumber'],
        message='Hello from intellipush test suite',
    )

    assert mocked_post.called

    args, kwargs = mocked_post.call_args
    assert kwargs['data']['text_message'] == 'Hello from intellipush test suite'
    assert kwargs['data']['single_target_countrycode'] == test_contact['countrycode']
    assert kwargs['data']['single_target'] == test_contact['phonenumber']


@pytest.mark.live_test
def test_sms_send_at_live(intellipush, request):
    if not request.config.option.live_country_code or not request.config.option.live_phone_number:
        pytest.skip('Requires --live-country-code and --live-phone-number')

    # all datetimes are assumed to be in local time in APIv4
    when = datetime.datetime.now() + datetime.timedelta(minutes=2)
    message = 'Hello from intellipush test suite'

    sms = SMS(
        receivers=[(request.config.option.live_country_code, request.config.option.live_phone_number)],
        message=message,
        when=when,
    )

    result = intellipush.send_sms(sms)
    assert result['id']
    assert result['text_message'] == message
    assert result['method'] == 'sms'
    assert result['timetosend'] == when.strftime('%Y-%m-%d %H:%M')


def test_sms_send_at(intellipush, mocker):
    mocked_post = mocker.patch.object(intellipush, '_post')

    # all datetimes are assumed to be in local time in APIv4
    when = datetime.datetime.now() + datetime.timedelta(minutes=5)

    sms = SMS(
        receivers=[(test_contact['countrycode'], test_contact['phonenumber'])],
        message='Hello from intellipush test suite',
        when=when,
    )

    intellipush.send_sms(sms)

    assert mocked_post.called

    args, kwargs = mocked_post.call_args
    assert kwargs['data']['text_message'] == 'Hello from intellipush test suite'
    assert kwargs['data']['single_target_countrycode'] == test_contact['countrycode']
    assert kwargs['data']['single_target'] == test_contact['phonenumber']
    assert kwargs['data']['time'] == when.strftime('%H:%M:%S')
    assert kwargs['data']['date'] == when.strftime('%Y-%m-%d')


@pytest.mark.live_test
def test_sms_batch_live(intellipush, request):
    if not request.config.option.live_country_code or not request.config.option.live_phone_number:
        pytest.skip('Requires --live-country-code and --live-phone-number')

    messages = {
        'Hello from intellipush test suite 1': True,
        'Hello from intellipush test suite 2': True,
    }

    smses = []

    for message in messages:
        smses.append(SMS(
            receivers=[(request.config.option.live_country_code, request.config.option.live_phone_number)],
            message=message,
        ))

    result = intellipush.send_smses(smses)

    assert len(result) == len(messages)

    for message in result:
        assert message['success']
        del messages[message['data']['text_message']]

    assert len(messages) == 0


@pytest.mark.live_test
def test_fetch_and_delete_sms_live(intellipush, request):
    if not request.config.option.live_country_code or not request.config.option.live_phone_number:
        pytest.skip('Requires --live-country-code and --live-phone-number')

    when = datetime.datetime.now() + datetime.timedelta(minutes=30)
    message = 'This should not be sent'

    sms = SMS(
        receivers=[(request.config.option.live_country_code, request.config.option.live_phone_number)],
        message=message,
        when=when,
    )

    result = intellipush.send_sms(sms)
    assert result['id']

    fetched = intellipush.fetch_sms(sms_id=result['id'])
    assert fetched['text_message'] == message

    delete_result = intellipush.delete_sms(sms_id=result['id'])
    fetched = intellipush.fetch_sms(sms_id=result['id'])
    assert not fetched


@pytest.mark.live_test
def test_sent_smses(intellipush):
    result = intellipush.sent_smses()

    assert isinstance(result, list)

    # this could be zero if tests run without any actual messages sent -- ever..
    if len(result) > 0:
        for message in result:
            assert message['id']


