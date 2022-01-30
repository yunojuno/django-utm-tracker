from unittest import mock

import pytest
from django.contrib.auth import get_user_model

from utm_tracker.models import LeadSource

User = get_user_model()


@pytest.mark.django_db
@mock.patch("utm_tracker.request.CUSTOM_TAGS", ["tag1", "tag2"])
def test_create_from_utm_params():
    user = User.objects.create(username="Bob")
    utm_params = {
        "utm_medium": "medium",
        "utm_source": "source",
        "utm_campaign": "campaign",
        "utm_term": "term",
        "utm_content": "content",
        "gclid": "1C5CHFA_enGB874GB874",
        "aclk": "2C5CHFA_enGB874GB874",
        "msclkid": "3C5CHFA_enGB874GB874",
        "twclid": "4C5CHFA_enGB874GB874",
        "fbclid": "5C5CHFA_enGB874GB874",
        "tag1": "foo",
        "tag2": "bar",
    }

    ls_returned = LeadSource.objects.create_from_utm_params(user, utm_params)

    ls = LeadSource.objects.get()
    assert ls == ls_returned

    assert ls.user == user
    assert ls.medium == "medium"
    assert ls.source == "source"
    assert ls.campaign == "campaign"
    assert ls.term == "term"
    assert ls.content == "content"
    assert ls.gclid == "1C5CHFA_enGB874GB874"
    assert ls.aclk == "2C5CHFA_enGB874GB874"
    assert ls.msclkid == "3C5CHFA_enGB874GB874"
    assert ls.twclid == "4C5CHFA_enGB874GB874"
    assert ls.fbclid == "5C5CHFA_enGB874GB874"
    assert ls.custom_tags == {"tag1": "foo", "tag2": "bar"}


@pytest.mark.django_db
def test_create_from_utm_params___missing_params():
    """Check failure on missing medium and content."""
    user = User.objects.create(username="Bob")
    utm_params = {"utm_source": "source"}
    with pytest.raises(ValueError):
        LeadSource.objects.create_from_utm_params(user, utm_params)

    utm_params = {"utm_medium": "source"}
    with pytest.raises(ValueError):
        LeadSource.objects.create_from_utm_params(user, utm_params)

    utm_params = {"utm_source": "source", "utm_medium": "medium"}
    LeadSource.objects.create_from_utm_params(user, utm_params)
