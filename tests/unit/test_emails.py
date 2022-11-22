from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from furl import furl

from interactive.emails import (
    send_analysis_request_confirmation_email,
    send_analysis_request_email,
    send_welcome_email,
)

from ..factories import AnalysisRequestFactory, UserFactory


def test_send_welcome_email(mailoutbox):
    user = UserFactory()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    reset_url = furl(settings.BASE_URL) / user.get_password_reset_url(uid, token)

    context = {
        "name": user.name,
        "url": reset_url,
    }
    send_welcome_email(user.email, context)

    m = mailoutbox[0]

    assert list(m.to) == [user.email]

    assert m.subject == "Welcome to OpenSAFELY Interactive"

    assert settings.BASE_URL in m.body
    assert user.name in m.body
    assert "password-reset" in m.body, m.body


def test_send_analysis_request_email(mailoutbox):
    user = UserFactory()
    analysis_request = AnalysisRequestFactory(user=user)

    context = {
        "name": user.name,
        "title": analysis_request.title,
        "url": furl(settings.BASE_URL) / analysis_request.get_output_url(),
    }
    send_analysis_request_email(user.email, context)

    # reference the last email because creating a user creates one too
    # TODO: remove the signal creating this email
    m = mailoutbox[-1]

    assert list(m.to) == [user.email]

    assert m.subject == f"OpenSAFELY: {analysis_request.title}"

    assert analysis_request.get_output_url() in m.body
    assert user.name in m.body


def test_send_analysis_request_confirmation_email(mailoutbox):
    user = UserFactory()
    analysis_request = AnalysisRequestFactory(user=user)

    context = {
        "name": user.name,
        "codelist": analysis_request.codelist_name,
        "email": user.email,
    }

    send_analysis_request_confirmation_email(
        user.email, analysis_request.title, context
    )

    # reference the last email because creating a user creates one too
    # TODO: remove the signal creating this email
    m = mailoutbox[-1]

    assert list(m.to) == [user.email]

    assert m.subject == f"OpenSAFELY: {analysis_request.title} submitted"

    assert analysis_request.codelist_name in m.body
    assert user.name in m.body
    assert user.email in m.body
