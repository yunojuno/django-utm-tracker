from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from utm_tracker.models import LeadSource

User = get_user_model()


class TestLeadSourceManager:
    @pytest.mark.django_db
    def test_create_from_request(self):
        user = User.objects.create(username="Bob")
        request = mock.Mock(spec=HttpRequest, user=user)
        request.session = {
            "utm_medium": "medium",
            "utm_source": "source",
            "utm_campaign": "campaign",
            "utm_term": "term",
            "utm_content": "content",
        }

        ls_returned = LeadSource.objects.create_from_request(user=user, request=request)

        ls = LeadSource.objects.get()
        assert ls == ls_returned

        assert ls.user == user
        assert ls.medium == "medium"
        assert ls.source == "source"
        assert ls.campaign == "campaign"
        assert ls.term == "term"
        assert ls.content == "content"
        # Ensure we have cleared out the session
        assert request.session == {}
