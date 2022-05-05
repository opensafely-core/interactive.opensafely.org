import html2text
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from environs import Env

from services import slack


env = Env()


def notify_analysis_request_submitted(title, codelist, created_by):
    job_server_url = slack.link(
        env.str("JOB_SERVER_JOBS_URL", default=""),
        "job server",
    )
    message = (
        f"{created_by} submitted an analysis request called {title} for {codelist}\n"
    )
    message += f"Please start the job in {job_server_url}"
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
