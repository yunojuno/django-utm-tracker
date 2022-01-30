from django.http import HttpRequest

from .settings import CUSTOM_TAGS
from .types import UtmParamsDict

VALID_UTM_PARAMS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
]
# additional service-specific parameters
VALID_AD_PARAMS = [
    "gclid",  # Google ad click
    "aclk",  # Bing ad click
    "msclkid",  # MSFT ad click (non-Bing)
    "fbclid",  # Facebook ad click
    "twclid",  # Twitter ad click
]


def parse_qs(request: HttpRequest) -> UtmParamsDict:
    """
    Extract 'utm_*'+ values from request querystring.

    NB in the case where there are multiple values for the same key,
    this will extract the last one. Multiple values for utm_ keys should
    not appear in valid querystrings, so this may have an unpredictable
    outcome. Look after your querystrings.

    This function parses three separate chunks of qs values - first it
    parses the utm_* tags, then it adds the ad click ids, then it adds
    custom tags the user wishes to stash.

    """
    utm_keys = {
        str(k).lower(): str(v).lower()
        for k, v in request.GET.items()
        if k in VALID_UTM_PARAMS and v != ""
    }

    for ad_key in VALID_AD_PARAMS:
        if akey := request.GET.get(ad_key):
            # We don't want to lowercase the ad key, as they are
            # typically BASE64 encoded
            utm_keys[ad_key] = akey

    # add in any custom tags we have decided to stash
    for tag in CUSTOM_TAGS:
        # custom tags may be a list
        if val := request.GET.getlist(tag):
            utm_keys[tag] = ",".join(val)

    return utm_keys
