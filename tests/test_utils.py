from intellipush import utils
from urllib.parse import unquote


def test_php_encode_batch_array():
    struct = {
        'batch': [
            {'name': 'foo', 'bar': 'baz'},
        ],
    }

    assert 'batch[0][name]=foo&batch[0][bar]=baz' == unquote(utils.php_encode(struct))


def test_php_encode_batch_array_ignores_none():
    struct = {
        'batch': [
            {'name': 'foo', 'bar': None},
        ],
    }

    assert 'batch[0][name]=foo' == unquote(utils.php_encode(struct))