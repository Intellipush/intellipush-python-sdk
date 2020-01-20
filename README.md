# intellipush

A client for communicating with the intellipush API service for sending SMSes.

`pip install intellipush`

Sending an SMS:

    from intellipush import client
    intellipush = client.Intellipush(key=api_id, secret=api_secret)
    
    result = intellipush.sms(
        countrycode='0047',
        phonenumber=phonenumber,
        message='test from intellipush',
    )    

See the tests for current examples of how to perform most tasks available through the API. 

Running the tests
=================

The tests are run with `pytest`, and accepts `--api-id` and `--api-secret` to set
proper API access keys for testing against the live interface. Do not do this with accounts
you care about.

If not set, only the tests that do not depend on a live endpoint will be run.

    pytest tests/test_client.py --api-id=apiid --api-secret=secret
    
Tests that depend on a live phone number
----------------------------------------

Certain tests against the live system actually do stuff that ends up with a live 
message going out to a phone. Since we don't want this to happen without proper
cause, you'll have to provide two additional settings if you want live messages
to be sent.

    --live-phone-number <phonenumber> --live-country-code <countrycode>
    
Example:

    --live-phone-number 88888888 --live-country-code 0047
    
The methods do have mocked versions of their tests attached, but to make sure that
the tests actually work against the server side, this allows you to run those tests
as well if necessary.

Releasing a new version of the library
======================================

Create the archives:

    python setup.py sdist bdist_wheel
    
Upload the packages to pypi:

    