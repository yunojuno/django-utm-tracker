from unittest import mock

from django.http import HttpRequest
from django.test import RequestFactory

from utm_tracker.request import parse_qs


def test_parse_qs__ignores_non_utm():
    request = mock.Mock(spec=HttpRequest)
    request.GET = {
        "utm_source": "source",
        "utm_medium": "medium",
        "utm_campaign": "campaign",
        "utm_term": "term",
        "utm_content": "content",
        "foo": "bar",
    }
    assert parse_qs(request) == {
        "utm_source": "source",
        "utm_medium": "medium",
        "utm_campaign": "campaign",
        "utm_term": "term",
        "utm_content": "content",
    }


def test_parse_qs__ignores_empty_fields():
    request = mock.Mock(spec=HttpRequest)
    request.GET = {
        "utm_source": "Source",
        "utm_medium": "Medium",
        "utm_campaign": "",
        "utm_term": "",
        "utm_content": "",
    }
    assert parse_qs(request) == {
        "utm_source": "source",
        "utm_medium": "medium",
    }


@mock.patch("utm_tracker.request.CUSTOM_TAGS", ["tag1", "tag2"])
def test_parse_qs__custom_tags(rf: RequestFactory) -> None:
    request = mock.Mock(spec=HttpRequest)
    request.GET = {
        "utm_source": "Source",
        "utm_medium": "Medium",
        "tag1": "foo",
        "tag2": "",
    }
    assert parse_qs(request) == {
        "utm_source": "source",
        "utm_medium": "medium",
        "tag1": "foo",
    }
