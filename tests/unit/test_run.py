import pipeline
import pytest
import requests
from django.conf import settings

from interactive import run
from tests.factories import AnalysisRequestFactory


@pytest.fixture
def workspace_repo(tmp_path, monkeypatch):
    repo = tmp_path / "workspace_repo"
    repo.mkdir()
    # --bare means we can push to it, as it has no checkout
    run.git("init", "--bare", cwd=repo)
    monkeypatch.setattr(settings, "WORKSPACE_REPO", str(repo))
    return repo


def test_write_files(tmp_path):
    analysis_request = AnalysisRequestFactory()
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    run.write_files(checkout, analysis_request, "codelist")

    project = checkout / "project.yaml"
    codelist = checkout / "codelist.csv"

    assert codelist.read_text() == "codelist"
    p = pipeline.load_pipeline(project)

    output_dir = f"output/{analysis_request.id}"

    for name, action in p.actions.items():
        assert output_dir in action.run.args

    assert analysis_request.start_date in p.actions["generate_codelist_report"].run.args
    assert analysis_request.end_date in p.actions["generate_codelist_report"].run.args


def test_commit_files(tmp_path, workspace_repo):
    analysis_request = AnalysisRequestFactory()
    checkout = tmp_path / "checkout"
    run.git("clone", workspace_repo, checkout)
    (checkout / "project.yaml").write_text("project")
    (checkout / "codelist.csv").write_text("codelist")
    run.commit_and_push(checkout, analysis_request)

    ps = run.git(
        "show", str(analysis_request.id), cwd=workspace_repo, capture_output=True
    )
    assert analysis_request.codelist in ps.stdout
    assert str(analysis_request.id) in ps.stdout


def test_create_analysis_commit(workspace_repo, add_codelist_response):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist, "1\n2\n3")
    run.create_analysis_commit(analysis_request, workspace_repo)

    ps = run.git(
        "show",
        f"{analysis_request.id}:project.yaml",
        cwd=workspace_repo,
        capture_output=True,
    )
    p = pipeline.load_pipeline(ps.stdout)
    assert list(p.actions.keys()) == [
        "generate_codelist_report",
        "generate_measures",
        "generate_top_5_table",
        "generate_deciles_charts",
    ]

    ps = run.git(
        "show",
        f"{analysis_request.id}:codelist.csv",
        cwd=workspace_repo,
        capture_output=True,
    )
    assert ps.stdout == "1\n2\n3"


def test_create_analysis_commit_commit_exists(workspace_repo, add_codelist_response):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist, "1\n2\n3")
    run.create_analysis_commit(analysis_request, workspace_repo)

    with pytest.raises(Exception) as e:
        run.create_analysis_commit(analysis_request, workspace_repo)

    assert str(analysis_request.id) in str(e.value)
    assert "already exists" in str(e.value)


def test_create_analysis_commit_codelist_error(workspace_repo, add_codelist_response):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist, status=500)
    with pytest.raises(requests.HTTPError):
        run.create_analysis_commit(analysis_request, workspace_repo)


def test_create_analysis_commit_git_error_retry(
    workspace_repo, add_codelist_response, mocker
):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist, "1\n2\n3")

    mock_commit = mocker.patch("interactive.run.commit_and_push", autospec=True)
    mock_commit.side_effect = Exception("git error")

    with pytest.raises(Exception) as exc:
        run.create_analysis_commit(analysis_request, workspace_repo)

    assert str(exc.value) == "git error"
    assert mock_commit.call_count == 3
