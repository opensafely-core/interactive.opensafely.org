import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_admin_view(client):
    url = reverse("admin:login")
    response = client.get(url)
    assert response.status_code == 200
