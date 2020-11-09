from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import Client

from utm_tracker.request import request_has_utm_params

User = get_user_model()


class TestRequestHasUtmParams:
    @pytest.mark.parametrize(
        "utm_medium,utm_source,result",
        (
            ("", "", False),
            ("foo", "", False),
            ("", "bar", False),
            ("foo", "bar", True),
        ),
    )
    def with_default_required_params(self, utm_medium, utm_source, result):
        request = mock.Mock(spec=HttpRequest)
        request.session = {"utm_medium": utm_medium, "utm_source": utm_source}
        assert request_has_utm_params(request) == result

    @pytest.mark.parametrize(
        "utm_medium,utm_source,utm_content,result",
        (
            ("", "", "", False),
            ("foo", "", "", False),
            ("foo", "", "car", False),
            ("", "bar", "", False),
            ("foo", "bar", "", False),
            ("", "", "car", False),
            ("foo", "bar", "car", True),
        ),
    )
    def with_passed_required_params(self, utm_medium, utm_source, utm_content, result):
        request = mock.Mock(spec=HttpRequest)
        request.session = {
            "utm_medium": utm_medium,
            "utm_source": utm_source,
            "utm_content": utm_content,
        }
        assert (
            request_has_utm_params(
                request, required_params=["utm_medium", "utm_source", "utm_content"]
            )
            == result
        )
