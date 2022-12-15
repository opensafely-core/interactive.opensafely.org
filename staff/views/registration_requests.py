import structlog
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from interactive.models import RegistrationRequest

from ..decorators import staff_required


logger = structlog.get_logger(__name__)


@method_decorator(staff_required, name="dispatch")
class RegistrationRequestDetail(DetailView):
    context_object_name = "registration_request"
    model = RegistrationRequest
    template_name = "staff/registration_request_detail.html"


@method_decorator(staff_required, name="dispatch")
class RegistrationRequestList(ListView):
    model = RegistrationRequest
    template_name = "staff/registration_request_list.html"

    def get_queryset(self):
        qs = super().get_queryset()

        # filter on the search query
        if q := self.request.GET.get("q"):
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(email__icontains=q)
                | Q(organisation__icontains=q)
                | Q(job_title__icontains=q)
            )

        return qs
