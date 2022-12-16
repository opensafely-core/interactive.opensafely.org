from staff.views.index import Index

from ....factories import (
    AnalysisRequestFactory,
    RegistrationRequestFactory,
    UserFactory,
)


def test_index_without_search(rf, staff_user):
    request = rf.get("/")
    request.user = staff_user

    response = Index.as_view()(request)

    assert response.context_data["q"] is None
    assert response.context_data["results"] == []


def test_index_search(rf, staff_user):
    user = UserFactory(name="George Hickman")
    UserFactory.create_batch(5)

    analysis_request1 = AnalysisRequestFactory(user=user)
    analysis_request2 = AnalysisRequestFactory(title="Not George's Analysis")
    AnalysisRequestFactory.create_batch(5)

    registration_request = RegistrationRequestFactory(full_name="George Hickman")
    RegistrationRequestFactory.create_batch(5)

    request = rf.get("/?q=george")
    request.user = staff_user

    response = Index.as_view()(request)

    assert response.context_data["q"] == "george"

    results = response.context_data["results"]
    assert len(results) == 3
    assert results == [
        ("AnalysisRequest", [analysis_request1, analysis_request2]),
        ("RegistrationRequest", [registration_request]),
        ("User", [user]),
    ]
