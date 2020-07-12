from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import Client

from utm_tracker.middleware import LeadSourceMiddleware, UtmSessionMiddleware
from utm_tracker.models import LeadSource

User = get_user_model()


class TestUtmSessionMiddleware:
    @mock.patch.object(UtmSessionMiddleware, "_utm")
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
        assert request.session["utm_medium"] == "medium"
        assert request.session["utm_source"] == "source"
        assert request.session["utm_campaign"] == "campaign"
        assert request.session["utm_term"] == "term"
        assert request.session["utm_content"] == "content"


class TestLeadSourceMiddleware:
    @pytest.mark.parametrize(
        "medium,source,result",
        (
            ("", "", False),
            ("foo", "", False),
            ("", "bar", False),
            ("foo", "bar", True),
        ),
    )
    def test_has_utm(self, medium, source, result):
        request = mock.Mock(spec=HttpRequest)
        request.session = {"utm_medium": medium, "utm_source": source}
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        assert middleware.has_utm(request) == result

    @pytest.mark.django_db
    def test_capture_lead_source(self):
        user = User.objects.create(username="Bob")
        request = mock.Mock(spec=HttpRequest, user=user)
        request.session = {
            "utm_medium": "medium",
            "utm_source": "source",
            "utm_campaign": "campaign",
            "utm_term": "term",
            "utm_content": "content",
        }
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware.capture_lead_source(request)
        ls = LeadSource.objects.get()
        assert ls.user == request.user
        assert ls.medium == "medium"
        assert ls.source == "source"
        assert ls.campaign == "campaign"
        assert ls.term == "term"
        assert ls.content == "content"
        # ensure we have cleared out the session
        assert request.session == {}

    @pytest.mark.django_db
    def test_capture_lead_source__exception(self):
        """Check that db errors don't kill middleware."""
        request = mock.Mock(spec=HttpRequest)
        request.session = {}  # empty session will cause capture_lead_source to blow
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware.capture_lead_source(request)
        assert LeadSource.objects.count() == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "utm,authenticated,captured",
        (
            ("", False, False),
            ("utm", False, False),
            ("", True, False),
            ("utm", True, True),
        ),
    )
    @mock.patch.object(LeadSourceMiddleware, "capture_lead_source")
    def test_middleware(self, mock_capture, utm, authenticated, captured):
        user = User() if authenticated else AnonymousUser()
        session = {"utm_medium": utm, "utm_source": utm}
        request = mock.Mock(spec=HttpRequest, user=user, session=session)
        middleware = LeadSourceMiddleware(lambda r: HttpResponse())
        middleware(request)
        assert (mock_capture.call_count == 1) == captured


@pytest.mark.django_db
def test_utm_and_lead_source():
    """Integration test for extracting UTM params and storing LeadSource."""
    user = User.objects.create(username="fred")
    client = Client()

    # Initial request is unauthenticated - qs params are stashed in the session,
    # but no LeadSource is created, as we don't have a user at this point.
    client.get(
        "/?utm_medium=medium"
        "&utm_source=source"
        "&utm_campaign=campaign"
        "&utm_term=term"
        "&utm_content=content"
        "&foo=bar"
    )
    assert client.session["utm_medium"] == "medium"
    assert client.session["utm_source"] == "source"
    assert client.session["utm_campaign"] == "campaign"
    assert client.session["utm_term"] == "term"
    assert client.session["utm_content"] == "content"
    assert not user.lead_sources.exists()

    # Subsequent request, we force a login, so that we have a user - at which
    # point we should capture the LeadSource, and clear the session.
    client.force_login(user)
    client.get("/")
    ls = user.lead_sources.get()
    assert ls.medium == "medium"
    assert ls.source == "source"
    assert ls.campaign == "campaign"
    assert ls.term == "term"
    assert ls.content == "content"
    # session is empty now
    assert not [k for k in client.session.keys() if k.startswith("utm")]
