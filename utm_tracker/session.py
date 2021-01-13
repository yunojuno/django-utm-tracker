import logging
from typing import Any, List

from django.contrib.sessions.backends.base import SessionBase

from .models import LeadSource
from .types import UtmParamsDict

SESSION_KEY_UTM_PARAMS = "utm_params"

logger = logging.getLogger(__name__)


def stash_utm_params(session: SessionBase, params: UtmParamsDict) -> bool:
    """
    Add new utm_params to the list of utm_params in the session.

    If the params dict is empty ({}), or already stashed in the session,
    then it's ignored.

    Returns True if the params are stored.

    """
    if not params:
        return False

    session.setdefault(SESSION_KEY_UTM_PARAMS, [])
    if params in session[SESSION_KEY_UTM_PARAMS]:
        return False
    session[SESSION_KEY_UTM_PARAMS].append(params)
    return True


def pop_utm_params(session: SessionBase) -> List[UtmParamsDict]:
    """Pop the list of utm_param dicts from a session."""
    return session.pop(SESSION_KEY_UTM_PARAMS, [])


def dump_utm_params(user: Any, session: SessionBase) -> List[LeadSource]:
    """
    Flush utm_params from the session and save as LeadSource objects.

    Calling this function will remove all existing utm_params from the
    current session.

    Returns a list of LeadSource objects created - one for each utm_params
    dict found in the session.

    """
    created = []
    for params in pop_utm_params(session):
        try:
            created.append(LeadSource.objects.create_from_utm_params(user, params))
        except ValueError as ex:
            logger.debug(f"Unable to save utm_params: {params}: {ex}")
    return created
