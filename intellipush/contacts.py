class ContactFilter:
    def __init__(self, sex=None, age=None, country=None, company=None, param1=None, param2=None, param3=None):
        self.sex = sex
        self.age = age
        self.country = country
        self.company = company
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3


class Target:
    def __init__(self, contact_id=None, email=None, countrycode=None, phonenumber=None):
        self.contact_id = contact_id
        self.email = email
        self.countrycode = countrycode
        self.phonenumber = phonenumber
