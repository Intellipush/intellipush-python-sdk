
class Intellipush:
    def __init__(self, key, secret, base_url=''):
        self.key = key
        self.secret = secret
        self.base_url = base_url

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

    def create_contact(self, name, number, email=None, company=None, sex=None, country=None, param1=None, param2=None, param3=None):
        pass

    def contact(self, contact_id):
        pass

    def delete_contact(self, contact_id):
        pass

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
        pass

    def shorturl(self, shorturl_id=None, shorturl=None):
        if not shorturl_id and not shorturl:
            raise NoValidIDException('Either shorturl_id or shorturl has to be provided')

    def create_shorturl(self, url):
        pass

    def create_child_shorturl(self, parent_shorturl_id, target=None):
        pass

    def shorturls(self, items=50, page=1, include_children=False, parent_shorturl_id=None, target=None):
        pass

    def _get(self):
        pass

    def _post(self):
        pass


class IntellipushException(Exception):
    pass


class NoValidIDException(IntellipushException):
    pass


class ServerSideException(IntellipushException):
    pass
