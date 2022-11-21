from django.conf import settings
from furl import furl
from incuna_mail import send


def send_welcome_email(email, user):
    reset_url = furl(settings.BASE_URL) / user.get_password_reset_url()

    context = {
        "domain": settings.BASE_URL,
        "name": user.name,
        "url": reset_url,
    }

    send(
        to=email,
        subject="Welcome to OpenSAFELY Interactive",
        sender="OpenSAFELY Interactive <no-reply@mg.interactive.opensafely.org>",
        reply_to=["OpenSAFELY Team <team@opensafely.org>"],
        template_name="emails/welcome_email.txt",
        html_template_name="emails/welcome_email.html",
        context=context,
    )


def send_analysis_request_email(email, analysis_request):
    output_url = furl(settings.BASE_URL) / analysis_request.get_output_url()

    context = {
        "name": analysis_request.user.name,
        "title": analysis_request.title,
        "url": output_url,
    }

    send(
        to=email,
        subject=f"OpenSAFELY: {context.get('title')}",
        sender="OpenSAFELY Interactive <no-reply@mg.interactive.opensafely.org>",
        reply_to=["OpenSAFELY Team <team@opensafely.org>"],
        template_name="emails/analysis_done.txt",
        html_template_name="emails/analysis_done.html",
        context=context,
    )


def send_analysis_request_confirmation_email(email, analysis_request):
    context = {
        "name": analysis_request.user.name,
        "codelist": analysis_request.codelist_name,
        "email": analysis_request.user.email,
    }

    send(
        to=email,
        subject=f"OpenSAFELY: {analysis_request.title} submitted",
        sender="OpenSAFELY Interactive <no-reply@mg.interactive.opensafely.org>",
        reply_to=["OpenSAFELY Team <team@opensafely.org>"],
        template_name="emails/analysis_confirmation.txt",
        html_template_name="emails/analysis_confirmation.html",
        context=context,
    )
