import logging
from typing import Callable, Dict

from django.http import HttpRequest, HttpResponse

from .models import LeadSource

logger = logging.getLogger(__name__)


class UtmSessionMiddleware:
    """Extract utm values from querystring and store in session."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.session.update(self._utm(request))
        return self.get_response(request)

    def _utm(self, request: HttpRequest) -> Dict[str, str]:
        """
        Extract 'utm_*' values from request querystring.

        NB in the case where there are multiple values for the same key,
        this will extract the last one. Multiple values for utm_ keys
        should not appear in valid querystrings, so this may have an
        unpredictable outcome. Look after your querystrings.

        """
        return {str(k): str(v) for k, v in request.GET.items() if k.startswith("utm_")}


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

    def has_utm(self, request: HttpRequest) -> bool:
        """Return True if the request has valid UTM params in session."""
        return all(
            [
                request.session.get("utm_medium", ""),
                request.session.get("utm_source", ""),
            ]
        )

    def capture_lead_source(self, request: HttpRequest) -> None:
        """
        Capture a new LeadSource from request UTM values.

        This method 'pop's the values from the session - so they will be deleted
        from hereon.

        """
        try:
            LeadSource.objects.create(
                user=request.user,
                medium=request.session.pop("utm_medium"),
                source=request.session.pop("utm_source"),
                campaign=request.session.pop("utm_campaign", ""),
                term=request.session.pop("utm_term", ""),
                content=request.session.pop("utm_content", ""),
            )
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Error creating LeadSource: %s", ex)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated and self.has_utm(request):
            self.capture_lead_source(request)
        return self.get_response(request)
