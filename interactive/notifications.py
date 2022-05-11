from urllib.parse import urljoin

import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from services import slack


def notify_analysis_request_submitted(analysis_request):
    # including the analysis id in the url will pre-fill the input in job-server.
    job_server_url = slack.link(
        f"{settings.JOB_SERVER_JOBS_URL}/{analysis_request.id}",
        "job server",
    )
    commit_link = slack.link(
        f"{settings.WORKSPACE_REPO}/tree/{analysis_request.id}",
        str(analysis_request.id),
    )

    message = f"{analysis_request.created_by} submitted an analysis request called {analysis_request.title} for {analysis_request.codelist}\n"
    message += f"Commit: {commit_link}"
    message += f"Please start the job in {job_server_url}\n"

    analysis_url = urljoin(settings.BASE_URL, analysis_request.get_output_url())
    analysis_link = slack.link(analysis_url, "here")

    message += f"When complete, the output will be viewable {analysis_link}"

    slack.post(text=message)


def notify_registration_request_submitted(full_name, job_title, organisation, email):
    full_name_link = slack.link(email, full_name, is_email=True)
    message = f"{full_name_link} ({job_title}) from {organisation} has registered their interest in using OpenSAFELY Interactive"
    slack.post(text=message)


def send_welcome_email(email, context):
    subject = "Welcome to OpenSAFELY Interactive"
    html_body = render_to_string("emails/welcome_email.html", context)
    text_body = _convert_html(html_body)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email="team@opensafely.org",
        to=[email],
        body=text_body,
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def _convert_html(raw_html):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_images = True
    text_maker.ignore_emphasis = True
    text_maker.ignore_links = True
    text_maker.body_width = 0
    raw_text = text_maker.handle(raw_html)
    return raw_text
