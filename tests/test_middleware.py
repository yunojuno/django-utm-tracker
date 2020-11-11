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
    @mock.patch("utm_tracker.middleware.flush_utm_params")
    def test_middleware__unauthenticated(self, mock_flush):
        request = mock.Mock(spec=HttpRequest, user=AnonymousUser())
        assert not request.user.is_authenticated
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert mock_flush.call_count == 0

    @mock.patch("utm_tracker.middleware.flush_utm_params")
    def test_middleware__authenticated(self, mock_flush):
        session = mock.Mock(SessionBase)
        request = mock.Mock(spec=HttpRequest, user=User(), session=session)
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert mock_flush.call_count == 1
        mock_flush.assert_called_once_with(request.user, session)

    @mock.patch("utm_tracker.middleware.flush_utm_params")
    def test_middleware__error(self, mock_flush):
        session = mock.Mock(SessionBase)
        request = mock.Mock(spec=HttpRequest, user=User(), session=session)
        mock_flush.side_effect = Exception("Panic")
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert mock_flush.call_count == 1


@pytest.mark.django_db
def test_utm_and_lead_source():
    """Integration test for extracting UTM params and storing LeadSource."""
    user = User.objects.create(username="fred")
    client = Client()

    # Initial request is unauthenticated - qs params are stashed in the session,
    # but no LeadSource is created, as we don't have a user at this point.
    client.get("/?utm_medium=medium1" "&utm_source=source1" "&foo=bar")
    utm_params = client.session[SESSION_KEY_UTM_PARAMS]
    assert len(utm_params) == 1
    assert utm_params[0]["utm_medium"] == "medium1"
    assert utm_params[0]["utm_source"] == "source1"

    # second unauthenticated request - should be appended
    client.get(
        "/?utm_medium=medium2"
        "&utm_source=source2"
        "&utm_campaign=campaign2"
        "&utm_term=term2"
        "&utm_content=content2"
        "&foo=bar"
    )
    utm_params = client.session[SESSION_KEY_UTM_PARAMS]
    assert utm_params[1]["utm_medium"] == "medium2"
    assert utm_params[1]["utm_source"] == "source2"
    assert utm_params[1]["utm_campaign"] == "campaign2"
    assert utm_params[1]["utm_term"] == "term2"
    assert utm_params[1]["utm_content"] == "content2"
    assert not user.lead_sources.exists()

    # Subsequent request, we force a login, so that we have a user - at which
    # point we should capture the LeadSource, and clear the session.
    client.force_login(user)
    client.get("/")
    ls = user.lead_sources.count() == 2
    ls = user.lead_sources.first()
    assert ls.medium == "medium1"
    assert ls.source == "source1"
    assert ls.campaign == ""
    assert ls.term == ""
    assert ls.content == ""

    ls = user.lead_sources.last()
    assert ls.medium == "medium2"
    assert ls.source == "source2"
    assert ls.campaign == "campaign2"
    assert ls.term == "term2"
    assert ls.content == "content2"

    # session is empty now
    assert not client.session.get(SESSION_KEY_UTM_PARAMS)
