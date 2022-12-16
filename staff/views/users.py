import structlog
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView

from interactive.models import User

from ..decorators import staff_required


logger = structlog.get_logger(__name__)


@method_decorator(staff_required, name="dispatch")
class UserDetail(UpdateView):
    fields = [
        "email",
        "is_active",
        "is_staff",
        "job_title",
        "name",
    ]
    model = User
    template_name = "staff/user_detail.html"

    def get_context_data(self, **kwargs):
        analysis_requests = self.object.analysis_requests.order_by(Lower("title"))
        orgs = self.object.orgs.order_by(Lower("name"))

        return super().get_context_data(**kwargs) | {
            "analysis_requests": analysis_requests,
            "orgs": orgs,
        }

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset=queryset)
        except ValidationError:  # unknown timeflake ID
            raise Http404

    def get_success_url(self):
        return self.object.get_staff_url()


@method_decorator(staff_required, name="dispatch")
class UserList(ListView):
    model = User
    template_name = "staff/user_list.html"

    def get_context_data(self):
        return super().get_context_data() | {
            "active_options": ["yes", "no"],
            "staff_options": ["yes", "no"],
        }

    def get_queryset(self):
        qs = super().get_queryset()

        # filter on the search query
        if q := self.request.GET.get("q"):
            qs = qs.filter(Q(email__icontains=q) | Q(name__icontains=q))

        if active := self.request.GET.get("active"):
            is_active = active == "yes"  # treat anything else as no/false
            qs = qs.filter(is_active=is_active)

        if staff := self.request.GET.get("staff"):
            is_staff = staff == "yes"  # treat anything else as no/false
            qs = qs.filter(is_staff=is_staff)

        return qs
