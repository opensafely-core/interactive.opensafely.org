import functools

import structlog
from django.urls import reverse


logger = structlog.get_logger(__name__)


def _is_active(request, prefix):
    return request.path.startswith(prefix)


def staff_nav(request):
    if not request.user.is_staff:
        return {"staff_nav": []}

    _active = functools.partial(_is_active, request)

    options = [
        {
            "name": "Analysis Requests",
            "is_active": _active(reverse("staff:analysis-request-list")),
            "url": reverse("staff:analysis-request-list"),
        },
        {
            "name": "Orgs",
            "is_active": _active(reverse("staff:org-list")),
            "url": reverse("staff:org-list"),
        },
        {
            "name": "Projects",
            "is_active": _active(reverse("staff:project-list")),
            "url": reverse("staff:project-list"),
        },
        {
            "name": "Registration Requests",
            "is_active": _active(reverse("staff:registration-request-list")),
            "url": reverse("staff:registration-request-list"),
        },
        {
            "name": "Users",
            "is_active": _active(reverse("staff:user-list")),
            "url": reverse("staff:user-list"),
        },
    ]

    return {"staff_nav": options}
