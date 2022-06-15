from django.conf import settings
from furl import furl

from services import slack


# run jobs page
JOB_SERVER_JOBS_URL = (
    furl(settings.JOB_SERVER_URL)
    / "datalab/opensafely-interactive"
    / settings.JOB_SERVER_WORKSPACE
    / "run-jobs"
)


def notify_analysis_request_submitted(analysis_request):
    codelist_url = (
        settings.OPENCODELISTS_URL / "codelist" / analysis_request.codelist_slug
    )
    codelist_link = slack.link(codelist_url, analysis_request.codelist_name)
    # this is only a valid link if WORKSPACE_REPO is a github url, i.e.
    # not in dev
    commit_link = slack.link(
        f"{settings.WORKSPACE_REPO}/tree/{analysis_request.id}",
        str(analysis_request.id),
    )
    job_server_url = slack.link(
        JOB_SERVER_JOBS_URL / analysis_request.commit_sha,
        "job server",
    )
    analysis_url = furl(settings.BASE_URL) / analysis_request.get_output_url()
    analysis_link = slack.link(analysis_url, "here")

    message = f"{analysis_request.created_by} submitted an analysis request called *{analysis_request.title}*\n"
    message += f"Using codelist: {codelist_link}\n"
    message += f"Commit: {commit_link}\n"
    message += f"Please start the job in {job_server_url}\n"
    message += f"When complete, the output will be viewable {analysis_link}"

    slack.post(text=message)


def notify_registration_request_submitted(full_name, job_title, organisation, email):
    full_name_link = slack.link(email, full_name, is_email=True)
    message = f"{full_name_link} ({job_title}) from {organisation} has registered their interest in using OpenSAFELY Interactive"
    slack.post(text=message, channel="interactive-registration-requests")
