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

    ad_keys = ["gclid", "aclk", "msclkid", "fbclid", "twclid"]
    for ad_key in ad_keys:
        if akey := request.GET.get(ad_key):
            # We don't want to lowercase the ad key, as they are
            # typically BASE64 encoded
            utm_keys[ad_key] = akey

    return utm_keys
