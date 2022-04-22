from interactive.models import AnalysisRequest


def test_model_string_repr():
    analysis = AnalysisRequest()
    analysis.title = "Analysis title"
    analysis.codelist = "Test Codelist"
    assert str(analysis) == "Analysis title (Test Codelist)"
