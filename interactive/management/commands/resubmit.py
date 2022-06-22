import django.core.exceptions
from django.core.management.base import BaseCommand, CommandError

from interactive.models import AnalysisRequest
from interactive.submit import submit_analysis


class Command(BaseCommand):
    help = "Resubmit an analysis request (commit, push, and resubmit job)"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument("analysis_request_ids", nargs="+")

    def handle(self, *args, **options):
        for ar_id in options["analysis_request_ids"]:
            try:
                r = AnalysisRequest.objects.get(pk=ar_id)
            except django.core.exceptions.ValidationError as exc:
                raise CommandError(
                    f"AnalysisRequest {ar_id} is not a valid id"
                ) from exc
            except AnalysisRequest.DoesNotExist as exc:
                raise CommandError(f"AnalysisRequest {ar_id} does not exist") from exc

            submit_analysis(r)

            self.stdout.write(
                self.style.SUCCESS("AnalysisRequest {ar_id} has been resubmitted")
            )
            self.stdout.write("Commit: {r.get_github_commit_url()}")
            self.stdout.write("Job: {r.job_request_url}")
