import pytest
from django.conf import settings
from django.http import Http404

from staff.views.analysis_requests import AnalysisRequestDetail, AnalysisRequestList

from ....factories import AnalysisRequestFactory, UserFactory


def test_analysisrequestdetail_get_success(rf, staff_user):
    analysis_request = AnalysisRequestFactory()

    request = rf.get("/")
    request.user = staff_user

    response = AnalysisRequestDetail.as_view()(request, pk=analysis_request.pk)

    assert response.status_code == 200
    assert response.context_data["analysis_request"] == analysis_request


def test_analysisrequestdetail_with_unknown_analysis_request(rf, staff_user):
    request = rf.get("/")
    request.user = staff_user

    with pytest.raises(Http404):
        AnalysisRequestDetail.as_view()(request, pk="unknown")


def test_analysisrequestdetail_without_staff_user(rf):
    user = UserFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = AnalysisRequestDetail.as_view()(request, pk=user.pk)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_analysisrequestlist_find_by_title(rf, staff_user):
    AnalysisRequestFactory(title="Asthma Variance")
    AnalysisRequestFactory(title="COVID-19 Covariance")
    AnalysisRequestFactory(title="COVID-19 Vaccination")

    request = rf.get("/?q=covid")
    request.user = staff_user

    response = AnalysisRequestList.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["object_list"]) == 2


def test_analysisrequestlist_success(rf, staff_user):
    AnalysisRequestFactory.create_batch(5)

    request = rf.get("/")
    request.user = staff_user

    response = AnalysisRequestList.as_view()(request)

    assert response.status_code == 200
    assert len(response.context_data["object_list"]) == 5
