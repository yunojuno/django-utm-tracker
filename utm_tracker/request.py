from django.http import HttpRequest

from .types import UtmParamsDict

VALID_UTM_PARAMS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
]


def parse_qs(request: HttpRequest) -> UtmParamsDict:
    """
    Extract 'utm_*'+ values from request querystring.

    NB in the case where there are multiple values for the same key,
    this will extract the last one. Multiple values for utm_ keys
    should not appear in valid querystrings, so this may have an
    unpredictable outcome. Look after your querystrings.

    """
    utm_keys = {
        str(k).lower(): str(v).lower()
        for k, v in request.GET.items()
        if k in VALID_UTM_PARAMS and v != ""
    }

    if gclid := request.GET.get("gclid"):
        # We don't want to lowercase the gclid
        utm_keys['gclid'] = gclid

    return utm_keys