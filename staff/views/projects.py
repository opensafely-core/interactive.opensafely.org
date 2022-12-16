from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, ListView, UpdateView, View

from interactive.models import Org, Project, ProjectMembership, User

from ..decorators import staff_required
from ..forms import ProjectAddMemberForm, ProjectCreateForm


@method_decorator(staff_required, name="dispatch")
class ProjectCreate(CreateView):
    form_class = ProjectCreateForm
    template_name = "staff/project_create.html"

    def form_valid(self, form):
        project = form.save(commit=False)
        project.created_by = self.request.user
        project.save()

        return redirect(project.get_staff_url())

    def get_context_data(self, **kwargs):
        # we don't have a nice way to override the type of text input
        # components yet so doing this here is a bit of a hack because we can't
        # construct dicts in a template
        return super().get_context_data(**kwargs) | {
            "extra_field_attributes": {"type": "number"},
        }


@method_decorator(staff_required, name="dispatch")
class ProjectDetail(FormView):
    form_class = ProjectAddMemberForm
    template_name = "staff/project_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Project, slug=self.kwargs["slug"])

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
            "members": self.object.members.order_by("email"),
            "project": self.object,
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
class ProjectEdit(UpdateView):
    fields = [
        "name",
        "slug",
        "number",
        "status",
        "status_description",
        "org",
    ]
    model = Project
    template_name = "staff/project_edit.html"

    def form_valid(self, form):
        project = form.save(commit=False)
        project.updated_by = self.request.user
        project.save()

        return redirect(project.get_staff_url())

    def get_context_data(self, **kwargs):
        # we don't have a nice way to override the type of text input
        # components yet so doing this here is a bit of a hack because we can't
        # construct dicts in a template
        return super().get_context_data(**kwargs) | {
            "extra_field_attributes": {"type": "number"},
        }


@method_decorator(staff_required, name="dispatch")
class ProjectList(ListView):
    queryset = Project.objects.select_related("org").order_by("number", Lower("name"))
    template_name = "staff/project_list.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "orgs": Org.objects.order_by("name"),
            "q": self.request.GET.get("q", ""),
        }

    def get_queryset(self):
        qs = super().get_queryset()

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(number__icontains=q))

        org = self.request.GET.get("org")
        if org:
            qs = qs.filter(org__slug=org)
        return qs


@method_decorator(staff_required, name="dispatch")
class ProjectRemoveMember(View):
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, slug=self.kwargs["slug"])
        email = request.POST.get("email", None)

        try:
            project.memberships.get(user__email=email).delete()
        except ProjectMembership.DoesNotExist:
            pass

        messages.success(request, f"Removed {email} from {project.title}")
        return redirect(project.get_staff_url())
