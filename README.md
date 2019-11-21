# intellipush

Running the tests
-----------------

The tests are run with `pytest`, and accepts `--api-id` and `--api-secret` to set
proper API access keys for testing against the live interface. Do not do this with accounts
you care about.

If not set, only the tests that do not depend on a live endpoint will be run.

    pytest tests/test_client.py --api-id=apiid --api-secret=secret