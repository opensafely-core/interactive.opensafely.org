import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from furl import furl
from incuna_mail import send


def send_welcome_email(email, context):
    subject = "Welcome to OpenSAFELY Interactive"
    html_body = render_to_string("emails/welcome_email.html", context)
    text_body = _convert_html(html_body)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email="OpenSAFELY Interactive <no-reply@mg.interactive.opensafely.org>",
        reply_to=("OpenSAFELY Team <team@opensafely.org>",),
        to=[email],
        body=text_body,
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


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

def send_analysis_request_confirmation_email(to, subject, context):
    subject = f"OpenSAFELY: {subject} submitted"
    html_body = render_to_string("emails/analysis_confirmation.html", context)
    text_body = _convert_html(html_body)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email="OpenSAFELY Interactive <no-reply@mg.interactive.opensafely.org>",
        reply_to=("OpenSAFELY Team <team@opensafely.org>",),
        to=[to],
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
