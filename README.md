# Django UTM Tracker

Django app for extracting and storing UTM tracking values.

## Django support

This package supports Python 3.12+ and Django 5.2-6.0

## Background

This app has been designed to integrate the standard `utm_*` querystring parameters that are used by
online advertisers with your Django project.

It does _not_ replace analytics (e.g. Google Analytics) and Adwords tracking, but does have one
crucial difference - it allows you to assign a specific user to a campaign advert.

This may be useful if you are trying to assess the value of multiple channels / campaigns.

### Supported querystring parameters

| Parameter    | Definition                                                                             |
| :----------- | :------------------------------------------------------------------------------------- |
| utm_medium   | Identifies what type of link was used.                                                 |
| utm_source   | Identifies which site sent the traffic, and is a required parameter.                   |
| utm_campaign | Identifies a specific product promotion or strategic campaign.                         |
| utm_term     | Identifies search terms.                                                               |
| gclid        | Identifies a google click, is used for ad tracking in Google Analytics via Google Ads. |
| aclk         | Identifies a Microsoft Ad click (bing), is used for ad tracking.                       |
| msclkid      | Identifies a Microsoft Ad click (MS ad network), is used for ad tracking.              |
| twclid       | Identifies a Twitter Ad click, is used for ad tracking.                                |
| fbclid       | Identifies a Facebook Ad click, is used for ad tracking.                               |

In addition to the fixed list above, you can also specify custom tags using the
`UTM_TRACKER_CUSTOM_TAGS` setting. Any querystring params that match these tags are stashed in a
JSONField called `custom_tags`.

## How it works

The app works as a pair of middleware classes, that extract `utm_` values from any incoming request
querystring, and then store those parameters against the request.user (if authenticated), or in the
request.session (if not).

The following shows this workflow (pseudocode - see `test_utm_and_lead_source` for a real example):

```python
client = Client()
# first request stashes values, but does not create a LeadSource as user is anonymous
client.get("/?utm_medium=medium&utm_source=source...")
assert utm_values_in_session
assert LeadSource.objects.count() == 0

# subsequent request, with authenticated user, extracts values and stores LeadSource
user = User.objects.create(username="fred")
client.force_login(user, backend=settings.FORCED_AUTH_BACKEND)
client.get("/")
assert not utm_values_in_session
assert LeadSource.objects.count() == 1
```

### Why split the middleware in two?

By splitting the middleware into two classes, we enable the use case where we can track leads
without `utm_` querystring parameters. For instance, if you have an internal referral program, using
a simple token, you can capture this as a `LeadSource` by adding sentinel values to the
`request.session`:

```python
def referral(request, token):
    # do token handling
    ...
    # medium and source are mandatory for lead source capture
    request.session["utm_medium"] = "referral"
    request.session["utm_source"] = "internal"
    # campaign, term and content are optional fields
    request.session["utm_campaign"] = "july"
    request.session["utm_term"] = token
    request.session["utm_content"] = "buy-me"
    return render(request, "landing_page.html")
```

## Configuration

Add the app to `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "utm_tracker"
]

UTM_TRACKER_CUSTOM_TAGS = ["tag1", "tag2"]
```

and add both middleware classes to `MIDDLEWARE`:

```python
# settings.py
MIDDLEWARE = [
    ...
    "utm_tracker.middleware.UtmSessionMiddleware",
    "utm_tracker.middleware.LeadSourceMiddleware",
]
```

The `UtmSession` middleware must come before `LeadSource` middleware.
