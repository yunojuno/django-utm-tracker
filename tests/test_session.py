import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import SessionBase
from utm_tracker.models import LeadSource
from utm_tracker.session import (
    SESSION_KEY_UTM_PARAMS,
    dump_utm_params,
    stash_utm_params,
)

User = get_user_model()


def test_stash_utm_params():
    session = SessionBase()
    assert not stash_utm_params(session, {})

    assert stash_utm_params(session, {"utm_medium": "foo"})
    assert session.modified
    assert len(session[SESSION_KEY_UTM_PARAMS]) == 1
    assert session[SESSION_KEY_UTM_PARAMS][0] == {"utm_medium": "foo"}

    # add a second set of params
    assert stash_utm_params(session, {"utm_medium": "bar"})
    assert len(session[SESSION_KEY_UTM_PARAMS]) == 2
    assert session[SESSION_KEY_UTM_PARAMS][1] == {"utm_medium": "bar"}

    # add a duplicate set of params
    assert not stash_utm_params(session, {"utm_medium": "bar"})
    assert len(session[SESSION_KEY_UTM_PARAMS]) == 2


@pytest.mark.django_db
def test_dump_utm_params():
    user = User.objects.create()
    utm_params1 = {"utm_medium": "medium1", "utm_source": "source1"}
    utm_params2 = {"utm_medium": "medium2", "utm_source": "source2"}
    session = {SESSION_KEY_UTM_PARAMS: [utm_params1, utm_params2]}
    created = dump_utm_params(user, session)
    assert LeadSource.objects.count() == 2
    first = LeadSource.objects.first()
    last = LeadSource.objects.last()
    assert first.medium == "medium1"
    assert last.medium == "medium2"
    assert created == [first, last]


@pytest.mark.django_db
def test_dump_utm_params__error():
    """Check that if one utm_params fail, others continue."""
    user = User.objects.create()
    utm_params1 = {"utm_mediumx": "medium1", "utm_source": "source1"}
    utm_params2 = {"utm_medium": "medium2", "utm_source": "source2"}
    session = {SESSION_KEY_UTM_PARAMS: [utm_params1, utm_params2]}
    created = dump_utm_params(user, session)
    # only one object will be stored
    source = LeadSource.objects.get()
    assert source.medium == "medium2"
    assert created == [source]
    # session is clean
    assert SESSION_KEY_UTM_PARAMS not in session
