from django.contrib import messages
from django.db import transaction
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, ListView, UpdateView, View

from interactive.models import Org, OrgMembership, User

from ..decorators import staff_required
from ..forms import OrgAddMemberForm


@method_decorator(staff_required, name="dispatch")
class OrgCreate(CreateView):
    fields = ["name"]
    model = Org
    template_name = "staff/org_create.html"

    def form_valid(self, form):
        org = form.save(commit=False)
        org.created_by = self.request.user
        org.save()

        return redirect(org.get_staff_url())


@method_decorator(staff_required, name="dispatch")
class OrgDetail(FormView):
    form_class = OrgAddMemberForm
    template_name = "staff/org_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Org, slug=self.kwargs["slug"])

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        users = form.cleaned_data["users"]

        with transaction.atomic():
            for user in users:
                self.object.memberships.create(
                    user=user,
                    created_by=self.request.user,
                )

        return redirect(self.object.get_staff_url())

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "members": self.object.members.order_by(Lower("name")),
            "org": self.object,
        }

    def get_form_kwargs(self):
        members = self.object.members.values_list("pk", flat=True)
        return super().get_form_kwargs() | {
            "users": User.objects.exclude(pk__in=members),
        }

    def get_initial(self):
        return super().get_initial() | {
            "users": self.object.members.values_list("pk", flat=True),
        }


@method_decorator(staff_required, name="dispatch")
class OrgEdit(UpdateView):
    fields = [
        "name",
        "slug",
        "logo_file",
    ]
    model = Org
    template_name = "staff/org_edit.html"

    def get_success_url(self):
        return self.object.get_staff_url()


@method_decorator(staff_required, name="dispatch")
class OrgList(ListView):
    queryset = Org.objects.order_by("name")
    template_name = "staff/org_list.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "q": self.request.GET.get("q", ""),
        }

    def get_queryset(self):
        qs = super().get_queryset()

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)

        return qs


@method_decorator(staff_required, name="dispatch")
class OrgRemoveMember(View):
    def post(self, request, *args, **kwargs):
        org = get_object_or_404(Org, slug=self.kwargs["slug"])
        email = request.POST.get("email", None)

        try:
            org.memberships.get(user__email=email).delete()
        except OrgMembership.DoesNotExist:
            pass

        messages.success(request, f"Removed {email} from {org.name}")
        return redirect(org.get_staff_url())
