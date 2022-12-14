from django.conf import settings
from furl import furl

from services import slack


def notify_analysis_request_submitted(analysis_request, issue_url):
    codelist_url = (
        settings.OPENCODELISTS_URL / "codelist" / analysis_request.codelist_slug
    )
    codelist_link = slack.link(codelist_url, analysis_request.codelist_name)
    # this is only a valid link if WORKSPACE_REPO is a github url, i.e.
    # not in dev
    commit_link = slack.link(
        analysis_request.get_github_commit_url(),
        str(analysis_request.id),
    )
    job_request_url = slack.link(
        analysis_request.job_request_url,
        "automatically requested on job server",
    )
    analysis_url = furl(settings.BASE_URL) / analysis_request.get_output_url()
    analysis_link = slack.link(analysis_url, "here")

    issue_link = slack.link(issue_url, "tracked here")

    message = f"{analysis_request.created_by.email} submitted an analysis request called *{analysis_request.title}*\n"
    message += f"Using codelist: {codelist_link}\n"
    message += f"Commit: {commit_link}\n"
    message += f"A job has been {job_request_url}\n"
    message += f"Output checking request {issue_link}\n"
    message += f"When complete, the output will be viewable {analysis_link}"

    slack.post(text=message)
    slack.post(text=message, channel="opensafely-outputs")


def notify_registration_request_submitted(full_name, job_title, organisation, email):
    full_name_link = slack.link(email, full_name, is_email=True)
    message = f"{full_name_link} ({job_title}) from {organisation} has registered their interest in using OpenSAFELY Interactive"
    slack.post(text=message, channel="interactive-registration-requests")
