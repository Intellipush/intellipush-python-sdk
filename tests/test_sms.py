import pytest
import datetime

from intellipush.messages import (
    SMS,
)


def test_exception_thrown_if_when_is_present_but_not_datetime():
    with pytest.raises(TypeError):
        SMS(message='foo', when='foo')


def test_exception_not_thrown_if_when_is_datetime():
    SMS(message='foo', when=datetime.datetime.utcnow())


def test_exception_not_thrown_if_when_is_none():
    SMS(message='foo', when=datetime.datetime.utcnow())
