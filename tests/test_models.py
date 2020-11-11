import pytest
from django.contrib.auth import get_user_model

from utm_tracker.models import LeadSource

User = get_user_model()


@pytest.mark.django_db
def test_create_from_utm_params():
    user = User.objects.create(username="Bob")
    utm_params = {
        "utm_medium": "medium",
        "utm_source": "source",
        "utm_campaign": "campaign",
        "utm_term": "term",
        "utm_content": "content",
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
