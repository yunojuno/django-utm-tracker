import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse
from request_log.models import RequestLog

from .request import parse_qs
from .session import dump_utm_params, stash_utm_params

logger = logging.getLogger(__name__)


class UtmSessionMiddleware:
    """Extract utm values from querystring and store in session."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        utm_params = parse_qs(request)
        if not utm_params:
            return self.get_response(request)
        log = RequestLog.objects.create_log(request)
        stash_utm_params(request.session, parse_qs(request))
        if not request.session.session_key:
            request.session["LOG_ON_NEXT_REQUEST"] = log.id
            return self.get_response(request)

        if (log_id := request.session.pop("LOG_ON_NEXT_REQUEST", None)):
            log = RequestLog.objects.get(id=log_id)
            log.session_key = request.session.session_key
            log.save()
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
