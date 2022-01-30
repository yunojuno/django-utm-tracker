from django.conf import settings

# list of custom args to extract from the querystring
CUSTOM_TAGS = getattr(settings, "UTM_TRACKER_CUSTOM_TAGS", [])
