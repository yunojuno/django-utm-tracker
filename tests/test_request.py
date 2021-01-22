from unittest import mock

from django.http import HttpRequest

from utm_tracker.request import parse_qs


def test_pars_qs__ignores_non_utm():
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


def test_pars_qs__ignores_empty_fields():
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
