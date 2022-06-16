import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings

from interactive.notifications import notify_analysis_request_submitted
from services import jobserver, opencodelists


PROJECT_YAML = """
version: '3.0'

expectations:
  population_size: 1000

actions:

  codelist_report_{ID}:
    run: >
      cohortextractor:latest generate_codelist_report
        --codelist-path=codelist.csv
        --start-date={START}
        --end-date={END}
        --output-dir output/{ID}
    outputs:
      moderately_sensitive:
        table: output/{ID}/counts_per_*.csv
        list_sizes: output/{ID}/list_sizes.csv
        patient_count_table: output/{ID}/patient_count.csv

  measures_{ID}:
    run: python:latest python analysis/generate_measures.py output/{ID}
    needs: [codelist_report_{ID}]
    outputs:
      moderately_sensitive:
        measure: output/{ID}/measure_counts_per_week_per_practice.csv
        events_count_table: output/{ID}/event_counts.csv
        practice_count_table: output/{ID}/practice_count.csv

  top_5_table_{ID}:
    run: python:latest python analysis/top_codes_table.py output/{ID}
    needs: [codelist_report_{ID}]
    outputs:
      moderately_sensitive:
        table: output/{ID}/top_5_code_table.csv

  deciles_charts_{ID}:
    run: >
      deciles-charts:v0.0.24
        --input-files output/{ID}/measure_counts_per_week_per_practice.csv
        --output-dir output/{ID}
    config:
      show_outer_percentiles: false
      tables:
        output: true
      charts:
        output: true
    needs: [measures_{ID}]
    outputs:
      moderately_sensitive:
        deciles_charts: output/{ID}/deciles_*.*
"""


VARIABLES_PY = """
study_start_date = "{START}"
study_end_date = "{END}"
low_count_threshold = 100
rounding_base = 10
"""


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


def create_analysis_commit(analysis_request, repo):

    # add auth token if it's a real github repo
    if str(repo).startswith("https://github.com"):
        repo = repo.replace(
            "https://", f"https://interactive:{settings.GITHUB_TOKEN}@"
        )  # pragma: no cover

    # check this commit does not already exist
    ps = git(
        "ls-remote",
        "--tags",
        repo,
        f"refs/tags/{analysis_request.id}",
        capture_output=True,
    )
    if ps.stdout != "":
        raise Exception(f"Commit for {analysis_request.id} already exists in {repo}")

    # grab the codelist contents
    codelist_slug = opencodelists.get_codelist(analysis_request.codelist_slug)

    attempts = 0
    while True:
        try:
            with tempfile.TemporaryDirectory(suffix=str(analysis_request.id)) as tmpd:
                checkout = Path(tmpd) / "interactive"
                git("clone", repo, checkout)
                project_yaml = write_files(checkout, analysis_request, codelist_slug)
                commit_sha = commit_and_push(checkout, analysis_request)
        except Exception:
            attempts += 1
            if attempts >= 3:
                raise
        else:
            return commit_sha, project_yaml


def write_files(checkout, analysis_request, codelist_slug):
    # this needs to be a fixed name, or else we'll litter HEAD with previous
    # codelists
    codelist_path = checkout / "codelist.csv"
    codelist_path.write_text(codelist_slug)

    project_path = checkout / "project.yaml"
    project_yaml = PROJECT_YAML.format(
        ID=str(analysis_request.id),
        START=analysis_request.start_date,
        END=analysis_request.end_date,
    )
    project_path.write_text(project_yaml)

    (checkout / "analysis").mkdir(exist_ok=True)
    variables_path = checkout / "analysis" / "variables.py"
    variables_path.write_text(
        VARIABLES_PY.format(
            START=analysis_request.start_date,
            END=analysis_request.end_date,
        )
    )

    return project_yaml


def commit_and_push(checkout, analysis_request):
    msg = f"Codelist {analysis_request.codelist_slug} ({analysis_request.id})"
    email = analysis_request.user.email
    git("add", "project.yaml", "codelist.csv", cwd=checkout)
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
    git("tag", str(analysis_request.id), cwd=checkout)
    # push the tag
    git("push", "origin", str(analysis_request.id), cwd=checkout)
    # push to master. Note: we technically wouldn't need this from a pure git
    # pov, as a tag would be enough, but job-runner explicitly checks that
    # a commit is on the branch history, for security reasons
    git("push", "origin", "--force-with-lease", cwd=checkout)
    return commit_sha


def submit_analysis(analysis_request):
    commit_sha, project_yaml = create_analysis_commit(
        analysis_request, settings.WORKSPACE_REPO
    )
    analysis_request.commit_sha = commit_sha
    analysis_request.save(update_fields=["commit_sha"])

    # submit a JobRequest to job-server, we update the AnalysisRequest again
    # here so a failure talking to job-server doesn't lose the request details
    url = jobserver.submit_job_request(analysis_request, project_yaml)
    analysis_request.job_request_url = url
    analysis_request.save(update_fields=["job_request_url"])

    notify_analysis_request_submitted(analysis_request)
