import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse

from .request import parse_qs
from .session import dump_utm_params, stash_utm_params

logger = logging.getLogger(__name__)


class UtmSessionMiddleware:
    """Extract utm values from querystring and store in session."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        stash_utm_params(request.session, parse_qs(request))
        return self.get_response(request)


class LeadSourceMiddleware:
    """
    Store LeadSource and clear Session UTM values.

    If there are any utm_ params stored in the request session, this middleware
    will create a new LeadSource object from them, and clear out the values. This
    middleware should come after UtmSessionMiddleware.

    Only authenticated users have a LeadSource created - if the user is anonymous
    then the params are left in the request.session. If the session expires, or
    is deleted then this will be lost. If the user subsequently logs in, or is
    registered, then the session data will be retained, and on the first request
    with an authenticated user the data will be stored.

    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            try:
                dump_utm_params(request.user, request.session)
            except:  # noqa E722
                logger.exception("Error flushing utm_params from request")

        return self.get_response(request)
