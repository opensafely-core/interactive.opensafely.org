from django.conf import settings

from interactive.emails import (
    send_analysis_request_confirmation_email,
    send_analysis_request_email,
    send_welcome_email,
)

from ..factories import AnalysisRequestFactory, UserFactory


def test_send_welcome_email(mailoutbox):
    user = UserFactory()

    send_welcome_email(user.email, user)

    m = mailoutbox[0]

    assert list(m.to) == [user.email]

    assert m.subject == "Welcome to OpenSAFELY Interactive"

    assert settings.BASE_URL in m.body
    assert user.name in m.body
    assert "password-reset" in m.body, m.body


def test_send_analysis_request_email(mailoutbox):
    user = UserFactory()
    analysis_request = AnalysisRequestFactory(created_by=user)

    send_analysis_request_email(user.email, analysis_request)

    # reference the last email because creating a user creates one too
    # TODO: remove the signal creating this email
    m = mailoutbox[-1]

    assert list(m.to) == [user.email]

    assert m.subject == f"OpenSAFELY: {analysis_request.title}"

    assert analysis_request.get_output_url() in m.body
    assert user.name in m.body


def test_send_analysis_request_confirmation_email(mailoutbox):
    user = UserFactory()
    analysis_request = AnalysisRequestFactory(created_by=user)

    send_analysis_request_confirmation_email(user.email, analysis_request)

    # reference the last email because creating a user creates one too
    # TODO: remove the signal creating this email
    m = mailoutbox[-1]

    assert list(m.to) == [user.email]

    assert m.subject == f"OpenSAFELY: {analysis_request.title} submitted"

    assert analysis_request.codelist_name in m.body
    assert user.name in m.body
    assert user.email in m.body
