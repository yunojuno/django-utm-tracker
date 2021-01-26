from django.contrib.auth import get_user_model
from django.test import TestCase

from utm_tracker.models import LeadSource
from utm_tracker.session import SESSION_KEY_UTM_PARAMS

User = get_user_model()


class IntegrationTests(TestCase):
    def test_single_utm(self):
        self.client.get("/200/?utm_medium=medium1&utm_source=source1&foo=bar")
        utm_params = self.client.session[SESSION_KEY_UTM_PARAMS]
        assert len(utm_params) == 1
        assert utm_params[0]["utm_medium"] == "medium1"
        assert utm_params[0]["utm_source"] == "source1"
        assert not LeadSource.objects.exists()

    def test_duplicate_utm(self):
        self.client.get("/200/?utm_medium=medium1&utm_source=source1&foo=bar")
        self.client.get("/200/?utm_medium=medium1&utm_source=source1&foo=bar")
        utm_params = self.client.session[SESSION_KEY_UTM_PARAMS]
        assert len(utm_params) == 1
        assert utm_params[0]["utm_medium"] == "medium1"
        assert utm_params[0]["utm_source"] == "source1"
        assert not LeadSource.objects.exists()

    def test_multiple_utm(self):
        self.client.get("/200/?utm_medium=medium1&utm_source=source1&foo=bar")
        self.client.get("/200/?utm_medium=medium2&utm_source=source1&foo=bar")
        utm_params = self.client.session[SESSION_KEY_UTM_PARAMS]
        assert len(utm_params) == 2
        assert utm_params[0]["utm_medium"] == "medium1"
        assert utm_params[1]["utm_medium"] == "medium2"
        assert not LeadSource.objects.exists()

    def test_redirect_utm(self):
        response = self.client.get(
            "/302/?utm_medium=medium1&utm_source=source1", follow=True
        )
        assert response.redirect_chain == [("/200/", 302)]
        utm_params = self.client.session[SESSION_KEY_UTM_PARAMS]
        assert len(utm_params) == 1
        assert not LeadSource.objects.exists()

    def test_redirect_perm_utm(self):
        response = self.client.get(
            "/301/?utm_medium=medium1&utm_source=source1", follow=True
        )
        assert response.redirect_chain == [("/200/", 301)]
        utm_params = self.client.session[SESSION_KEY_UTM_PARAMS]
        assert len(utm_params) == 1
        assert not LeadSource.objects.exists()

    def test_dump_params(self):
        user = User.objects.create(username="fred")
        self.client.get("/200/?utm_medium=medium1&utm_source=source1&gclid=1C5CHFA_enGB874GB874")
        assert not LeadSource.objects.exists()

        self.client.force_login(user)
        self.client.get("/200/?utm_medium=medium2&utm_source=source2&gclid=1C5CHFA_enGB874GB874222")
        assert SESSION_KEY_UTM_PARAMS not in self.client.session
        # implicit test that there are exactly two objects created
        ls1, ls2 = list(LeadSource.objects.order_by("id"))
        assert ls1.medium == "medium1"
        assert ls1.source == "source1"
        assert ls1.gclid == "1C5CHFA_enGB874GB874"
        assert ls2.medium == "medium2"
        assert ls2.source == "source2"
        assert ls2.gclid == "1C5CHFA_enGB874GB874222"
