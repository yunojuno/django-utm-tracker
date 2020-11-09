from typing import List

from django.http import HttpRequest


def request_has_utm_params(
    request: HttpRequest, required_params: List[str] = None
) -> bool:
    """
    Return True if the request has UTM paramaters we consider valid.

    This function should be called before automatically persisting a
    LeadSource, to ensure that one is only persisted when enough valid
    UTM parameters exist for it to make sense.

    The `required_params` parameter can be overriden on a per-call basis to
    decide which parameters should be required for a given call. We provide
    a sane default.
    """
    required_params = required_params or ["utm_source", "utm_medium"]

    required_values = [request.session.get(param, "") for param in required_params]
    return all(required_values)
