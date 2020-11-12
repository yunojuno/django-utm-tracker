from django.http import HttpRequest, HttpResponse


def test_view(request: HttpRequest) -> HttpResponse:
    request.session.setdefault("foo", 0)
    request.session["foo"] += 1
    return HttpResponse("OK")
