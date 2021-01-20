from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.urls import reverse


def test_view_200(request: HttpRequest) -> HttpResponse:
    request.session.setdefault("foo", 0)
    request.session["foo"] += 1
    return HttpResponse("OK")


def test_view_301(request: HttpRequest) -> HttpResponsePermanentRedirect:
    return HttpResponsePermanentRedirect(reverse("test_view_200"))


def test_view_302(request: HttpRequest) -> HttpResponseRedirect:
    return HttpResponseRedirect(reverse("test_view_200"))
