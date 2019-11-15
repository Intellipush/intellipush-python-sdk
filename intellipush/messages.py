class SMS:
    def __init__(self, message, receivers=None, when=None, repeat=None, contact_id=None, contact_list_id=None, contact_list_filter=None):
        self.message = message
        self.receivers = receivers
        self.when = when
        self.repeat = repeat
        self.contact_id = contact_id
        self.contact_list_id = contact_list_id
        self.contact_list_filter = contact_list_filter
