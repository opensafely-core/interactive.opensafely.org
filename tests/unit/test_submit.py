import subprocess

import pipeline
import pytest
import requests
from django.conf import settings

from interactive import submit
from tests.factories import AnalysisRequestFactory


@pytest.fixture
def workspace_repo(tmp_path, monkeypatch):
    repo = tmp_path / "workspace_repo"
    repo.mkdir()
    # --bare means we can push to it, as it has no checkout
    submit.git("init", "--bare", cwd=repo)
    monkeypatch.setattr(settings, "WORKSPACE_REPO", str(repo))
    return repo


def write_dummy_files(checkout):
    (checkout / "project.yaml").write_text("project")
    (checkout / "codelist.csv").write_text("codelist")
    code = checkout / "analysis/code"
    code.parent.mkdir(exist_ok=True)
    code.write_text("code")


def test_commit_files(tmp_path, workspace_repo):
    analysis_request = AnalysisRequestFactory()
    checkout = tmp_path / "checkout"
    submit.git("clone", workspace_repo, checkout)
    write_dummy_files(checkout)
    commit = submit.commit_and_push(checkout, analysis_request)

    assert commit is not None

    ps = submit.git("show", commit, cwd=workspace_repo, capture_output=True)
    assert analysis_request.codelist_slug in ps.stdout
    assert str(analysis_request.id) in ps.stdout


def test_commit_files_parallel_change_to_upstream(tmp_path, workspace_repo):
    analysis_request = AnalysisRequestFactory()

    # prepare initial checkout
    checkout = tmp_path / "checkout"
    submit.git("clone", workspace_repo, checkout)
    write_dummy_files(checkout)

    # simulate parallel change from other request
    other_request = AnalysisRequestFactory()
    other_checkout = tmp_path / "other"
    submit.git("clone", workspace_repo, other_checkout)
    write_dummy_files(other_checkout)
    commit = submit.commit_and_push(other_checkout, other_request)
    assert commit is not None

    # now try commit original
    with pytest.raises(subprocess.CalledProcessError):
        submit.commit_and_push(checkout, analysis_request)

    # ensure the tag didn't get pushed upstream
    with pytest.raises(subprocess.CalledProcessError):
        submit.git("show", str(analysis_request.id), cwd=workspace_repo)


def test_create_analysis_commit(workspace_repo, add_codelist_response):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, "1\n2\n3")
    commit, _ = submit.create_analysis_commit(analysis_request, workspace_repo)

    ps = submit.git(
        "show",
        f"{commit}:project.yaml",
        cwd=workspace_repo,
        capture_output=True,
    )
    p = pipeline.load_pipeline(ps.stdout)
    assert list(p.actions.keys()) == [
        f"codelist_report_{analysis_request.id}",
        f"measures_{analysis_request.id}",
        f"top_5_table_{analysis_request.id}",
        f"deciles_charts_{analysis_request.id}",
    ]

    ps = submit.git(
        "show",
        f"{commit}:codelist.csv",
        cwd=workspace_repo,
        capture_output=True,
    )
    assert ps.stdout == "1\n2\n3"


def test_create_analysis_commit_commit_exists(workspace_repo, add_codelist_response):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, "1\n2\n3")
    submit.create_analysis_commit(analysis_request, workspace_repo)

    with pytest.raises(Exception) as e:
        submit.create_analysis_commit(analysis_request, workspace_repo)

    assert str(analysis_request.id) in str(e.value)
    assert "already exists" in str(e.value)


def test_create_analysis_commit_codelist_error(workspace_repo, add_codelist_response):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, status=500)
    with pytest.raises(requests.HTTPError):
        submit.create_analysis_commit(analysis_request, workspace_repo)


def test_create_analysis_commit_git_error_retry(
    workspace_repo, add_codelist_response, mocker
):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, "1\n2\n3")

    mock_commit = mocker.patch("interactive.submit.commit_and_push", autospec=True)
    mock_commit.side_effect = Exception("git error")

    with pytest.raises(Exception) as exc:
        submit.create_analysis_commit(analysis_request, workspace_repo)

    assert str(exc.value) == "git error"
    assert mock_commit.call_count == 3


def test_clean_dir(tmp_path):

    foo_file = tmp_path / "foo"
    git_file = tmp_path / ".git/gitfile"

    foo_file.write_text("foo")
    git_file.parent.mkdir()
    git_file.write_text("git")

    submit.clean_dir(tmp_path)

    assert not foo_file.exists()
    assert git_file.exists()
