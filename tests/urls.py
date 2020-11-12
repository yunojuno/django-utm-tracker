from django.contrib import admin
from django.urls import path

from .views import test_view

admin.autodiscover()

urlpatterns = [
    path("", test_view),
    path("admin/", admin.site.urls),
]
