from django.urls import include, path

from .views.analysis_requests import AnalysisRequestDetail, AnalysisRequestList
from .views.index import Index
from .views.registration_requests import (
    RegistrationRequestDetail,
    RegistrationRequestList,
)
from .views.users import UserDetail, UserList


app_name = "staff"

analysis_request_urls = [
    path("", AnalysisRequestList.as_view(), name="analysis-request-list"),
    path("<str:pk>/", AnalysisRequestDetail.as_view(), name="analysis-request-detail"),
]


registration_request_urls = [
    path("", RegistrationRequestList.as_view(), name="registration-request-list"),
    path(
        "<str:pk>/",
        RegistrationRequestDetail.as_view(),
        name="registration-request-detail",
    ),
]
user_urls = [
    path("", UserList.as_view(), name="user-list"),
    path("<str:pk>/", UserDetail.as_view(), name="user-detail"),
]

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("analysis_requests/", include(analysis_request_urls)),
    path("registration_requests/", include(registration_request_urls)),
    path("users/", include(user_urls)),
]
