import json

import requests
import time
import datetime

class Intellipush:
    def __init__(self, key, secret, base_url='https://www.intellipush.com/api', version='4.0'):
        self.key = key
        self.secret = secret
        self.base_url = base_url.rstrip('/')
        self.version = version
        self.sdk_tag = 'python'
        self.last_error = None
        self.last_error_code = None

    def send_sms(self, sms):
        pass

    def send_smses(self, smses):
        pass

    def delete_sms(self, sms_id):
        pass

    def update_sms(self, sms_id, sms):
        pass

    def scheduled_smses(self, items=50, page=1):
        pass

    def sent_smses(self, items=50, page=1):
        pass

    def received_smses(self, items=50, page=1, keyword=None, second_keyword=None):
        pass

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
        if contact_id:
            fetched = self._post('contact/getContact', data={
                'contact_id': contact_id,
            })
        elif countrycode and phonenumber:
            fetched = self._post('contact/getByPhoneNumber', data={
                'countrycode': countrycode,
                'phonenumber': phonenumber,
            })
        else:
            raise IntellipushException('Missing contact_id or (countrycode and phonenumber)')

        if not fetched:
            return None

        return fetched[0]

    def delete_contact(self, contact_id):
        return self._post('contact/deleteContact', {
            'contact_id': contact_id,
        })

    def update_contact(self, contact_id, name=None, number=None, email=None, company=None, sex=None, country=None, param1=None, param2=None, param3=None):
        pass

    def create_contact_list(self, name):
        pass

    def contact_list(self, contact_list_id):
        pass

    def add_to_contact_list(self, contact_list_id, contact_id):
        pass

    def remove_from_contact_list(self, contact_list_id, contact_id):
        pass

    def delete_contact_list(self, contact_list_id):
        pass

    def update_contact_list(self, contact_list_id, name):
        pass

    def contact_list_size(self, contact_list_id, contact_list_filter=None):
        pass

    def contacts_not_in_contact_list(self, contact_list_id, items=50, page=1):
        pass

    def current_user(self):
        return self._post('user')

    def shorturl(self, shorturl_id=None, shorturl=None):
        if not shorturl_id and not shorturl:
            raise NoValidIDException('Either shorturl_id or shorturl has to be provided')

    def create_shorturl(self, url):
        pass

    def create_child_shorturl(self, parent_shorturl_id, target=None):
        pass

    def shorturls(self, items=50, page=1, include_children=False, parent_shorturl_id=None, target=None):
        pass

    def statistics(self):
        pass

    def two_factor_generate(self):
        pass

    def two_factor_validate(self):
        pass

    def _default_parameters(self):
        return {
            'api_secret': self.secret,
            'appID': self.key,
            't': int(time.time()),
            'v': self.version,
            's': self.sdk_tag,
        }

    def _url(self, endpoint):
        return self.base_url + '/' + endpoint

    def _post(self, endpoint, data=None):
        self.last_error = None
        self.last_error_code = None

        if not data:
            data = {}

        data.update(self._default_parameters())

        response = requests.post(
            url=self._url(endpoint),
            data=data,
        )

        if response.status_code >= 500:
            raise ServerSideException(
                'Server generated an error code: ' +
                str(response.status_code) +
                ': ' + response.reason
            )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ServerSideException('Invalid JSON: ' + response.text)

        if not data['success']:
            if 'errorcode' in data:
                self.last_error_code = data['errorcode']
                self.last_error_message = data['status_message']

            return None

        return data['data']


class IntellipushException(Exception):
    pass


class NoValidIDException(IntellipushException):
    pass


class ServerSideException(IntellipushException):
    pass
