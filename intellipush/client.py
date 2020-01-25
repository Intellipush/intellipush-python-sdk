import json as jsonlib
import requests
import time
import datetime

from .utils import php_encode
from .messages import SMS
from .contacts import Target


class Intellipush:
    def __init__(self, key, secret, base_url='https://www.intellipush.com/api', version='4.0'):
        """
        Creat a client instance for communicating with Intellipush.

        `base_url` and `version` should be left to their default values unless you have a particular requirement.

        :param key: Your API key
        :param secret: Your API secret
        :param base_url: The base URL of the Intellipush API
        :param version: Version of the API that the client should communicate with
        """
        self.key = key
        self.secret = secret
        self.base_url = base_url.rstrip('/')
        self.version = version
        self.sdk_tag = 'python'
        self.last_error = None
        self.last_error_code = None
        self.last_error_message = None

    def sms(self, countrycode, phonenumber, message):
        """
        Simple method to directly send an sms without any extra settings.

        :param countrycode: Country code of the phone number (i.e. 0047)
        :param phonenumber: Phone number the message should be delivered to
        :param message: The message itself - a message will be split into several messages behind the scenes if its
               lengthexceeds 160 characters.
        :return: Response from the API with metadata about the queued/delivered message
        """
        sms = SMS(
            receivers=[(countrycode, phonenumber), ],
            message=message,
        )

        return self.send_sms(sms)

    def send_sms(self, sms):
        """
        Send an SMS object - created from the `SMS` data type (`intellipush.messages.SMS`).

        The main difference from the `sms` method is that this allows for far greater granularity when configuring
        the message to be sent, such as scheduling the message for later delivery and providing multiple recipients.

        :param sms: SMS object (`intellipush.messages.SMS`)
        :return: Response from the API with metadata about the queued/delivered message(s)
        """
        if len(sms.receivers) > 1:
            return self.send_smses((sms, ))

        return self._post(
            'notification/createNotification',
            data=self._sms_as_post_object(sms=sms),
        )

    def send_smses(self, smses):
        """
        Send a batch of messages by giving a list of `SMS` objects (`intellipush.messages.SMS`).

        This will deliver a batch / list of messages to the API, reducing the overhead when sending a single message by
        itself. Useful if you need to deliver a large amount of messages at the same time.

        :param smses: iterable giving an `SMS` object for each iteration
        :return: Response from the API with metadata about the queued/delivered message(s)
        """
        batch = []

        for sms in smses:
            for receiver in sms.receivers:
                batch.append(self._sms_as_post_object(sms=sms, receiver=receiver))

        return self._post(
            'notification/createBatch',
            data={'batch': batch},
            expect_list_return=True,
        )

    def delete_sms(self, sms_id):
        """
        Delete an unsent SMS.

        Removes a queued SMS from the API, causing it to not be sent. Useful together with the ability to
        schedule sending time for an SMS when submitting it to Intellipush.

        :param sms_id: `id` of the SMS to remove - returned by the API when sending an SMS or listing SMSes available.
        :return: Response from the API for the operation
        """
        return self._post(
            'notification/deleteNotification',
            data={'notification_id': sms_id}
        )

    def update_sms(self, sms_id, sms):
        """
        Update the information for a queued SMS.

        Change the contents of an SMS that has been queued for scheduled sending.

        :param sms_id: `id` of the SMS to update - returned by the API when sending an SMS or listing SMSes available.
        :param sms: The updated SMS object
        :return: Response from the API with metadata about the updated message
        """
        sms_object = self._sms_as_post_object(sms)
        sms_object['notification_id'] = sms_id

        return self._post(
            'notification/updateNotification',
            data=sms_object
        )

    def fetch_sms(self, sms_id):
        """
        Fetch information about an SMS sent or scheduled through Intellipush.

        :param sms_id: `id` of the SMS to retrieve
        :return: Metadata about the message
        """
        return self._post(
            'notification/getNotification',
            data={'notification_id': sms_id}
        )

    def scheduled_smses(self, items=50, page=1):
        """
        Retrieve a list of still scheduled messages on Intellipush.

        :param items: Number of items on each page
        :param page: The current page (1-based)
        :return: A list of scheduled messages available on Intellipush
        """
        return self._post(
            'notification/getUnsendtNotifications',
            data={'page': page, 'items': items}
        )

    def sent_smses(self, items=50, page=1):
        """
        Retrieve a list of messages sent through Intellipush.

        :param items: Number of items on each page
        :param page: The current page (1-based)
        :return: A list of messages that have been sent
        """
        return self._post(
            'notification/getSendtNotifications',
            data={'page': page, 'items': items}
        )

    def received_smses(self, items=50, page=1, keyword=None, second_keyword=None):
        """
        Retrieve a list of messages _received_ by your keyword from your recipients.

        :param items: Number of items on each page
        :param page: The current page (1-based)
        :param keyword: The primary keyword to retrieve received smses for
        :param second_keyword: The secondary keyword to filter messages by
        :return:
        """
        return self._post(
            'notification/getReceived',
            data={'page': page, 'items': items, 'keyword': keyword, 'secondKeyword': second_keyword}
        )

    def create_contact(self,
                       name,
                       countrycode=None,
                       phonenumber=None,
                       email=None,
                       company=None,
                       sex=None,
                       country=None,
                       param1=None,
                       param2=None,
                       param3=None,
                       **kwargs,
    ):
        """
        Create a contact on Intellipush.

        :param name: Name of the contact
        :param countrycode: Country code of the contact (i.e. `0047``
        :param phonenumber: Phone number of the contact
        :param email: Email of the contact
        :param company: Company name of the contact
        :param sex: Sex of the contact
        :param country: Associated country of the contact
        :param param1: Free form value to associate with the contact
        :param param2: Free form value to associate with the contact
        :param param3: Free form value to associate with the contact
        :param kwargs: Any additional parameters are supported by the client as necessary if the contact format is
                       extended without the client being updated
        :return: Metadata about the created contact from Intellipush
        """
        contact = {
            'name': name,
            'countrycode': countrycode,
            'phonenumber': phonenumber,
            'email': email,
            'company': company,
            'sex': sex,
            'country': country,
            'param1': param1,
            'param2': param2,
            'param3': param3,
        }

        contact.update(kwargs)
        return self._post('contact/createContact', contact)

    def contact(self, contact_id=None, countrycode=None, phonenumber=None):
        """
        Retrieve a contact from your Intellipush account. Either `contact_id` or both `countrycode` and `phonenumber`
        has to be provided.

        :param contact_id: `id` of the contact to retrieve
        :param countrycode: Country code of the contact to retrieve (i.e. `0047`)
        :param phonenumber: Phone number of the contact to retrieve
        :return:
        """
        if contact_id:
            fetched = self._post('contact/getContact', data={
                'contact_id': contact_id,
            })
        elif countrycode and phonenumber:
            fetched = self._post('contact/getContactByPhoneNumber', data={
                'countrycode': countrycode,
                'phonenumber': phonenumber,
            })
        else:
            raise IntellipushException('Missing contact_id or (countrycode and phonenumber)')

        if not fetched:
            return None

        return fetched[0]

    def delete_contact(self, contact_id):
        """
        Delete a contact from its id.

        :param contact_id: The id of the contact to remove.
        :return: Reponse from the API
        """
        return self._post('contact/deleteContact', {
            'contact_id': contact_id,
        })

    def update_contact(self, contact_id, name=None, countrycode=None, phonenumber=None, email=None, company=None, sex=None, country=None, param1=None, param2=None, param3=None, **kwargs):
        contact = {
            'contact_id': contact_id,
            'name': name,
            'countrycode': countrycode,
            'phonenumber': phonenumber,
            'email': email,
            'company': company,
            'sex': sex,
            'country': country,
            'param1': param1,
            'param2': param2,
            'param3': param3,
        }

        contact.update(kwargs)
        return self._post('contact/updateContact', contact)

    def create_contact_list(self, name):
        """
        Create a new contact list.

        :param name: Name of the contact list
        :return: Response from the API with information about the created contact list
        """
        result = self._post('contactlist/createContactlist', {
            'contactlist_name': name,
        })

        return self._adopt_contact_list(result)

    def contact_list(self, contact_list_id):
        """
        Fetch a contact list given by its id.

        :param contact_list_id: The id of the contact list to fetch.
        :return:
        """
        return self._adopt_contact_list(self._post('contactlist/getContactlist', {
            'contactlist_id': contact_list_id,
        }))

    def add_to_contact_list(self, contact_list_id, contact_id):
        """
        Add a contact to a contact list. You can use this to group your contacts into multiple segments.

        :param contact_list_id: The `id` of the contact list to add the contact to
        :param contact_id: The `id` of the contact to add
        :return: Response from the API
        """
        return self._post('contactlist/addContactToContactlist', {
            'contactlist_id': contact_list_id,
            'contact_id': contact_id,
        })

    def remove_from_contact_list(self, contact_list_id, contact_id):
        """
        Remove a contact from a contact list.

        :param contact_list_id: The `id` of the contact list to remove the contact from
        :param contact_id: The `id` of the contact to remove
        :return: Response from the API
        """
        return self._post('contactlist/removeContactFromContactlist', {
            'contactlist_id': contact_list_id,
            'contact_id': contact_id,
        })

    def delete_contact_list(self, contact_list_id):
        """
        Delete a contact list / segment.

        :param contact_list_id: The `id` of the contact list to remove
        :return: Response from the API
        """
        return self._post('contactlist/deleteContactlist', {
            'contactlist_id': contact_list_id,
        })

    def update_contact_list(self, contact_list_id, name):
        """
        Update a contact list's information

        :param contact_list_id: The `id` of the contact list to update
        :param name: New name of the contact list
        :return: Response from the API
        """
        return self._adopt_contact_list(self._post('contactlist/updateContactlist', {
            'contactlist_id': contact_list_id,
            'contactlist_name': name,
        }))

    def contact_list_size(self, contact_list_id, contact_list_filter=None):
        """
        Get the number of entries in a given contact list.

        :param contact_list_id: The `id` of the contact list to retrieve a count for
        :param contact_list_filter: Filter the contact list by these values (a `intellipush.contacts.ContactFilter`)
        :return:
        """
        result = self._post('contactlist/getNumberOfFilteredContactsInContactlist', {
            'contactlist_id': contact_list_id,
        })

        if 'amount' in result:
            return int(result['amount'])

        return None

    def contacts_not_in_contact_list(self, contact_list_id, items=50, page=1):
        """
        Retrieve all your contacts that are _not_ in the specified contact list.

        :param contact_list_id: `id` of the contact list to check the contacts against
        :param items: Number of contacts on each page
        :param page: The current page (1-based)
        :return: A list of contacts that isn't in the given contact list
        """
        pass

    def current_user(self):
        """
        Retrieve information about the currently logged in user.

        :return:
        """
        return self._post('user')

    def shorturl(self, shorturl_id=None, shorturl=None):
        """
        Retrieve a shorturl definition from its id or its shorturl. One of the parameters has
        to be provided.

        :param shorturl_id: The id of the shorturl definition to be retrieved
        :param shorturl: The shorturl to retrieve details for (with or without `http://host/`)
        :return: The fetched shorturl or None on failure
        """
        if not shorturl_id and not shorturl:
            raise NoValidIDException('Either shorturl_id or shorturl has to be provided')

        if shorturl_id:
            return self._post('url/getUrlDetailsById', {
                'url_id': shorturl_id,
            })

        return self._post('url/getDetailsByShortUrl', {
            'short_url': shorturl,
        })

    def create_shorturl(self, url, parent_url_id=None, target=None):
        """
        Create a shorturl (or a child shorturl if `parent_url_id is provided).

        A `target` parameter can be provided that links the shorturl to a specific user. The
        parameter should be an `contacts.Target` object.

        :param url: The URL to link the shorturl to.
        :param parent_url_id: The ID of the parent shorturl if this is a version of the previous URL with a different target
        :param target: A `contacts.Target` object that contains information to associate with the shorturl. If a target is given, `parent_url_id` must be set as well.
        :return: Details about the created shorturl
        """
        if target:
            if not isinstance(target, Target):
                raise TypeError('A `contacts.Target` object is required for the `target` parameter')

            target = self._target_as_post_object(target=target)

        if parent_url_id:
            return self._post('url/generateChildUrl', {
                'long_url': url,
                'target': target,
                'parent_url_id': parent_url_id,
            })

        if target:
            raise InvalidTargetException('A `target` is only valid for child shorturls (when `parent_url_id` is given).')

        return self._post('url/generateShortUrl', {
            'long_url': url,
        })

    def shorturls(self, items=50, page=1, include_children=False, parent_shorturl_id=None, target=None):
        """
        Retrieve all shorturls available for your Intellipush account.

        :param items: The number of items to return for each request
        :param page: The page number to return results for (1-based)
        :param include_children: Also return shorturls that are children of other shorturls
        :param parent_shorturl_id: Only return shorturls that have `parent_shorturl_id` as a parent
        :param target: Only return shorturls that matches this target (`intellipush.contacts.Target`).
        :return: A list of shorturls as returned from the API.
        """
        if target:
            if not isinstance(target, Target):
                raise TypeError('A `contacts.Target` object is required for the `target` parameter')

            target = self._target_as_post_object(target=target)

        return self._post('url/getAll', {
            'items': items,
            'page': page,
            'include_children': include_children,
            'parent_shorturl_id': parent_shorturl_id,
            'target': target,
        })

    def statistics(self):
        """
        Retrieve statistics about pending messages (`unsentNotifications`), number of contacts
        (`contacts`) and the number of contact lists (`contactlists`) active on your account.

        These are returned under the `numberOf` key on the root dictionary.

        :return: dict
        """
        stats = self._post('statistics')
        self._fix_statistics_keys(stats)
        return stats

    def two_factor_send(self, countrycode, phonenumber, message_before_code=None, message_after_code=None):
        """
        Send a two factor authentication code to a given countrycode and phone number. The code
        is validated by calling `two_factor_validate`.

        :param countrycode: Country code of the recipient's phone number
        :param phonenumber: Phone number to send 2FA code to
        :param message_before_code: String to prefix the 2FA code with. The generated message is "<prefixmessage><code><postfix>".
        :param message_after_code: Message to append after the 2FA code. No spaces are added automagically. The generated message is "<prefixmessage><code><postfix>".
        :return: Response from Intellipush
        :raises: TwoFactorAuthenticationIsAlreadyActive
        """
        result = self._post('twofactor/send2FaCode', {
            'countrycode': countrycode,
            'phonenumber': phonenumber,
            'message_p1': message_before_code,
            'message_p2': message_after_code,
        })

        if result.get('hasCode', False):
            raise TwoFactorAuthenticationIsAlreadyActive('The phone number has an active two factor authentication request.')

        return result

    def two_factor_validate(self, countrycode, phonenumber, code):
        """
        Validate a previously sent two factor code. Method returns True if the code is valid for the
        given phone number and country code, and False if not.

        :param countrycode: Country code of the phone number of the user
        :param phonenumber: Phone number of the user
        :param code: The 2FA code the user has entered
        :return: True or False depending on the validity of the code for the given country code and phone number.
        """
        result = self._post('twofactor/check2FaCode', {
            'countrycode': countrycode,
            'phonenumber': phonenumber,
            'code': code,
        })

        if not result:
            return False

        if 'access' in result and result['access'] is True:
            return True

        return False

    def _default_parameters(self):
        """
        Get a dictionary containing the default parameters that should be included in every request.

        :return: A dict with basic request information
        """
        return {
            'api_secret': self.secret,
            'appID': self.key,
            't': int(time.time()),
            'v': self.version,
            's': self.sdk_tag,
        }

    def _url(self, endpoint):
        """
        Merge base service URL with the endpoint we're requesting data from.

        :param endpoint: Endpoint for the API request (usually `<module>/<command>`)
        :return: The complete URL to use for the request
        """
        return self.base_url + '/' + endpoint

    def _post(self, endpoint, data=None, expect_list_return=False):
        """
        Internal helper method to send requests to the intellipush service. Wraps error handling and raises exceptions
        for general error conditions (such as HTTP status codes >= 300).

        `last_error_code` and `last_error_message` will be set if an error occurs.

        :param endpoint: The API endpoint to query (i.e. `contact/getContact`)
        :param data: Information to send to the endpoint - depends on what the endpoint expects.
        :param expect_list_return: Expect a list returned from the API endpoint - useful when the response consists of
               multiple messages.
        :return: The response from the API (returned under the `data` key). `last_error_code` and `last_error_message`
                 will be set to describe any error that occured.
        """
        self.last_error_message = None
        self.last_error_code = None

        if not data:
            data = {}

        data.update(self._default_parameters())
        encoded_data = php_encode(data)

        response = requests.post(
            url=self._url(endpoint),
            data=encoded_data,
        )

        if response.status_code >= 300:
            raise ServerSideException(
                'Server generated an error code: ' +
                str(response.status_code) +
                ': ' + response.reason
            )

        try:
            response_data = response.json()
        except jsonlib.JSONDecodeError as e:
            raise ServerSideException('Invalid JSON: ' + response.text)

        # The `batch` command returns a list, one for each message. We keep the first error we find, but return the
        # whole list so the client can do what it wants.
        if expect_list_return:
            for status_message in response_data:
                if 'errorcode' in status_message:
                    self.last_error_code = response_data['errorcode']
                    self.last_error_message = response_data['status_message']
                    break

            return response_data

        if not response_data['success']:
            if 'errorcode' in response_data:
                self.last_error_code = response_data['errorcode']
                self.last_error_message = response_data['status_message']

            return None

        return response_data['data']

    @staticmethod
    def _fix_statistics_keys(statistics):
        """
        Helper function to clean up the response from the statistics endpoint by removing
        misspelled statistics keys.

        :param statistics: Dictionary containing statistics, modified by reference
        :return:
        """
        if 'numberOf' in statistics:
            number_of = statistics['numberOf']

            if 'unsendtNotifications' in number_of:
                number_of['unsentNotifications'] = number_of['unsendtNotifications']
                del number_of['unsendtNotifications']

    @staticmethod
    def _adopt_contact_list(contact_list):
        """
        A contact list is returned from the API with the 'name' key as 'contactlist_name' OR as
        `list_name`. This is different from the other elements, so we patch the object to be
        similar to the other objects returned by the library.

        :param contact_list:
        :return:
        """
        if not contact_list:
            return contact_list

        # Copy the list so we don't make direct changes to the one sent in
        contact_list = dict(contact_list)

        if 'contactlist_name' in contact_list:
            contact_list['name'] = contact_list['contactlist_name']
            del contact_list['contactlist_name']

        if 'list_name' in contact_list:
            contact_list['name'] = contact_list['list_name']
            del contact_list['list_name']

        return contact_list

    @staticmethod
    def _sms_as_post_object(sms, receiver=None):
        """
        Convert an SMS object and its values to a format suitable for posting to Intellipush.

        :param sms: an `contacts.SMS` object
        :param receiver: If given, the `receiver` should be a two element tuple with country code and phone number
                         that overrides the one given in the SMS. This is useful when doing batch requests, as it
                         allows us to avoid changing the original SMS object - just the data we're posting to
                         the server. The tuple would be formatted as `('0047', '900xxxxx').
        :return:
        """
        data = vars(sms)

        if data['when'] and isinstance(data['when'], datetime.datetime):
            data['date'] = data['when'].strftime('%Y-%m-%d')
            data['time'] = data['when'].strftime('%H:%M:%S')
        else:
            data['date'] = 'now'
            data['time'] = 'now'

        if len(data['receivers']) > 1 and not receiver:
            raise IntellipushException('Attempted to send message with multiple receivers without proper batching')

        if not receiver:
            receiver = data['receivers'][0]

        data['single_target_countrycode'] = receiver[0]
        data['single_target'] = receiver[1]

        del data['receivers']
        return data

    @staticmethod
    def _target_as_post_object(target):
        return vars(target)


class IntellipushException(Exception):
    pass


class NoValidIDException(IntellipushException):
    pass


class ServerSideException(IntellipushException):
    pass


class InvalidTargetException(IntellipushException):
    pass


class TwoFactorAuthenticationIsAlreadyActive(IntellipushException):
    pass


