import structlog
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from interactive.models import AnalysisRequest

from ..decorators import staff_required


logger = structlog.get_logger(__name__)


@method_decorator(staff_required, name="dispatch")
class AnalysisRequestDetail(DetailView):
    context_object_name = "analysis_request"
    model = AnalysisRequest
    template_name = "staff/analysis_request_detail.html"


@method_decorator(staff_required, name="dispatch")
class AnalysisRequestList(ListView):
    model = AnalysisRequest
    template_name = "staff/analysis_request_list.html"

    def get_queryset(self):
        qs = super().get_queryset()

        # filter on the search query
        if q := self.request.GET.get("q"):
            qs = qs.filter(title__icontains=q)

        return qs
