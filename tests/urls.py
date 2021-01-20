from django.contrib import admin
from django.urls import path

from .views import test_view_200, test_view_301, test_view_302

admin.autodiscover()

urlpatterns = [
    path("200/", test_view_200, name="test_view_200"),
    path("301/", test_view_301, name="test_view_301"),
    path("302/", test_view_302, name="test_view_302"),
    path("admin/", admin.site.urls),
]
