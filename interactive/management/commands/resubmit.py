import uuid

import django.core.exceptions
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from interactive.models import AnalysisRequest
from interactive.submit import submit_analysis


class Command(BaseCommand):
    help = "Resubmit an analysis request (commit, push, and resubmit job)"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            "analysis_request_ids", nargs="*", help="list of analysis ids"
        )
        parser.add_argument(
            "--since",
            default=None,
            type=parse_datetime,
            help="all analysis requests missing a commit_sha since this date",
        )

    def handle(self, *args, **options):

        analysis_requests = []
        if options["analysis_request_ids"]:
            for ar_id in options["analysis_request_ids"]:
                id_size = len(ar_id)
                if id_size == 36:
                    analysis_requests.append(uuid.UUID(hex=ar_id))
                else:
                    analysis_requests.append(ar_id)

        if options["since"]:
            ars = AnalysisRequest.objects.filter(
                commit_sha=None, created_at__gte=options["since"]
            ).values_list("id", flat=True)
            if len(ars) == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"No AnalysisRequests found since {options['since']} with missing commit ids to resubmit",
                    )
                )
            else:
                analysis_requests.extend(ars)

        for ar_id in analysis_requests:
            try:
                r = AnalysisRequest.objects.get(pk=ar_id)
            except django.core.exceptions.ValidationError as exc:
                raise CommandError(
                    f"AnalysisRequest {ar_id} is not a valid id"
                ) from exc
            except AnalysisRequest.DoesNotExist as exc:
                raise CommandError(f"AnalysisRequest {ar_id} does not exist") from exc

            submit_analysis(r, force=True)

            self.stdout.write(
                self.style.SUCCESS(f"AnalysisRequest {ar_id} has been resubmitted")
            )
            self.stdout.write(f"Commit: {r.get_github_commit_url()}")
            self.stdout.write(f"Job: {r.job_request_url}")
