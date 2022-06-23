import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings

from interactive.notifications import notify_analysis_request_submitted
from reports.codelist import write_files
from services import jobserver, opencodelists


def git(*args, check=True, text=True, **kwargs):
    """Wrapper around subprocess.run for git commands.

    Changes the defaults: check=True and text=True, and prints the command run
    for logging.
    """
    cmd = ["git"] + [str(arg) for arg in args]
    cwd = kwargs.get("cwd", os.getcwd())
    cleaned = [arg.replace(settings.GITHUB_TOKEN, "*****") for arg in cmd]
    sys.stderr.write(f"{' '.join(cleaned)} (in {cwd})\n")
    return subprocess.run(cmd, check=check, text=text, **kwargs)


def create_analysis_commit(analysis_request, repo, force=False):

    # add auth token if it's a real github repo
    if str(repo).startswith("https://github.com"):
        repo = repo.replace(
            "https://", f"https://interactive:{settings.GITHUB_TOKEN}@"
        )  # pragma: no cover

    # check this commit does not already exist
    if not force:
        ps = git(
            "ls-remote",
            "--tags",
            repo,
            f"refs/tags/{analysis_request.id}",
            capture_output=True,
        )
        if ps.stdout != "":
            raise Exception(
                f"Commit for {analysis_request.id} already exists in {repo}"
            )

    # grab the codelist contents
    codelist_data = opencodelists.get_codelist(analysis_request.codelist_slug)

    attempts = 0
    while True:
        try:
            with tempfile.TemporaryDirectory(suffix=str(analysis_request.id)) as tmpd:
                checkout = Path(tmpd) / "interactive"
                git("clone", repo, checkout)
                clean_dir(checkout)
                write_files(checkout, analysis_request, codelist_data)
                commit_sha = commit_and_push(checkout, analysis_request, force=force)
                project_yaml = (checkout / "project.yaml").read_text()
                return commit_sha, project_yaml
        except Exception:
            attempts += 1
            if attempts >= 3:
                raise


def commit_and_push(checkout, analysis_request, force=False):
    msg = f"Codelist {analysis_request.codelist_slug} ({analysis_request.id})"
    force_args = ["--force"] if force else []
    email = analysis_request.user.email
    git("add", "project.yaml", "codelist.csv", "analysis", cwd=checkout)
    git(
        # -c arguments are instead of having to having to maintain stateful git config
        "-c",
        "user.email=interactive@opensafely.org",
        "-c",
        "user.name=OpenSAFELY Interactive",
        "commit",
        "--author",
        f"{email} <{email}>",
        "-m",
        msg,
        cwd=checkout,
    )
    ps = git("rev-parse", "HEAD", capture_output=True, cwd=checkout)
    commit_sha = ps.stdout.strip()
    # this is an super important step, makes it much easier to track commits
    git("tag", str(analysis_request.id), *force_args, cwd=checkout)
    # push to master. Note: we technically wouldn't need this from a pure git
    # pov, as a tag would be enough, but job-runner explicitly checks that
    # a commit is on the branch history, for security reasons
    git("push", "origin", "--force-with-lease", cwd=checkout)
    # push the tag once we know the main push has succeeded
    git("push", "origin", str(analysis_request.id), *force_args, cwd=checkout)
    return commit_sha


def submit_analysis(analysis_request, force=False):
    commit_sha, project_yaml = create_analysis_commit(
        analysis_request,
        settings.WORKSPACE_REPO,
        force=force,
    )
    analysis_request.commit_sha = commit_sha
    analysis_request.save(update_fields=["commit_sha"])

    # submit a JobRequest to job-server, we update the AnalysisRequest again
    # here so a failure talking to job-server doesn't lose the request details
    url = jobserver.submit_job_request(analysis_request, project_yaml)
    analysis_request.job_request_url = url
    analysis_request.save(update_fields=["job_request_url"])

    notify_analysis_request_submitted(analysis_request)


def clean_dir(path):
    """Remove all files (except .git)"""
    for f in path.glob("**/*"):
        if not f.is_file():
            continue
        relative = f.relative_to(path)
        if str(relative).startswith(".git"):
            continue
        f.unlink()
