from interactive.models import AnalysisRequest, RegisterInterest


def test_analysis_request_string_repr():
    analysis = AnalysisRequest()
    analysis.title = "Analysis title"
    analysis.codelist = "Test Codelist"
    assert str(analysis) == "Analysis title (Test Codelist)"


def test_register_interest_string_repr():
    request = RegisterInterest()
    request.full_name = "Alice"
    request.email = "alice@test.com"
    request.organisation = "The Bennett Institute"
    request.job_title = "Tester"
    assert str(request) == "Alice (alice@test.com), Tester at The Bennett Institute"
