from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest, HttpResponse
from django.test import Client

from utm_tracker.middleware import LeadSourceMiddleware, UtmSessionMiddleware
from utm_tracker.session import SESSION_KEY_UTM_PARAMS

User = get_user_model()


class TestUtmSessionMiddleware:
    @mock.patch("utm_tracker.middleware.parse_qs")
    def test_middleware(self, mock_utm):
        request = mock.Mock(spec=HttpRequest)
        request.session = {}
        mock_utm.return_value = {
            "utm_medium": "medium",
            "utm_source": "source",
            "utm_campaign": "campaign",
            "utm_term": "term",
            "utm_content": "content",
        }
        middleware = UtmSessionMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert len(request.session[SESSION_KEY_UTM_PARAMS]) == 1
        utm_params = request.session[SESSION_KEY_UTM_PARAMS][0]
        assert utm_params["utm_medium"] == "medium"
        assert utm_params["utm_source"] == "source"
        assert utm_params["utm_campaign"] == "campaign"
        assert utm_params["utm_term"] == "term"
        assert utm_params["utm_content"] == "content"

    @mock.patch("utm_tracker.middleware.parse_qs")
    def test_middleware__no_params(self, mock_utm):
        request = mock.Mock(spec=HttpRequest)
        request.session = {}
        mock_utm.return_value = {}
        middleware = UtmSessionMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert SESSION_KEY_UTM_PARAMS not in request.session


class TestLeadSourceMiddleware:
    @mock.patch("utm_tracker.middleware.dump_utm_params")
    def test_middleware__unauthenticated(self, mock_flush):
        request = mock.Mock(spec=HttpRequest, user=AnonymousUser())
        assert not request.user.is_authenticated
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert mock_flush.call_count == 0

    @mock.patch("utm_tracker.middleware.dump_utm_params")
    def test_middleware__authenticated(self, mock_flush):
        session = mock.Mock(SessionBase)
        request = mock.Mock(spec=HttpRequest, user=User(), session=session)
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert mock_flush.call_count == 1
        mock_flush.assert_called_once_with(request.user, session)

    @mock.patch("utm_tracker.middleware.dump_utm_params")
    def test_middleware__error(self, mock_flush):
        session = mock.Mock(SessionBase)
        request = mock.Mock(spec=HttpRequest, user=User(), session=session)
        mock_flush.side_effect = Exception("Panic")
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert mock_flush.call_count == 1
