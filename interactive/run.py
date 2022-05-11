import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings

from services import opencodelists


PROJECT_YAML = """
version: '3.0'

expectations:
  population_size: 1000

actions:

  generate_codelist_report:
    run: >
      cohortextractor:latest generate_codelist_report
        --codelist-path=codelist.csv
        --start-date={START}
        --end-date={END}
        --output-dir output/{ID}
    outputs:
      moderately_sensitive:
        table: output/*/counts_per_*.csv
        list_sizes: output/*/list_sizes.csv

  generate_measures:
    run: python:latest python analysis/generate_measures.py output/{ID}
    needs: [generate_codelist_report]
    outputs:
      moderately_sensitive:
        measure: output/*/measure_counts_per_week_per_practice.csv

  generate_top_5_table:
    run: python:latest python analysis/top_codes_table.py output/{ID}
    needs: [generate_codelist_report]
    outputs:
      moderately_sensitive:
        table: output/*/top_5_code_table.csv

  generate_deciles_charts:
    run: >
      deciles-charts:v0.0.15
        --input-files output/measure_counts_per_week_per_practice.csv
        --output-dir output/{ID}
    config:
      show_outer_percentiles: false
      tables:
        output: true
      charts:
        output: true
    needs: [generate_measures]
    outputs:
      moderately_sensitive:
        deciles_charts: output/*/deciles_*_*.*
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
        repo = repo.replace("https://", f"https://interactive:{settings.GITHUB_TOKEN}@")  # pragma: no cover

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
    codelist = opencodelists.get_codelist(analysis_request.codelist)

    attempts = 0
    while True:
        try:
            with tempfile.TemporaryDirectory(suffix=str(analysis_request.id)) as tmpd:
                checkout = Path(tmpd) / "interactive"
                git("clone", repo, checkout)
                write_files(checkout, analysis_request, codelist)
                commit_and_push(checkout, analysis_request)
        except Exception:
            attempts += 1
            if attempts >= 3:
                raise
        else:
            return


def write_files(checkout, analysis_request, codelist):
    # this needs to be a fixed name, or else we'll litter HEAD with previous
    # codelists
    codelist_path = checkout / "codelist.csv"
    codelist_path.write_text(codelist)
    project_path = checkout / "project.yaml"
    project_path.write_text(
        PROJECT_YAML.format(
            ID=str(analysis_request.id),
            START=analysis_request.start_date,
            END=analysis_request.end_date,
        )
    )


def commit_and_push(checkout, analysis_request):
    msg = f"{analysis_request.id}: codelist {analysis_request.codelist} by {analysis_request.user.email}"
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
    # this is an super important step, makes it much easier to track commits
    git("tag", str(analysis_request.id), cwd=checkout)
    # push the tag
    git("push", "origin", str(analysis_request.id), cwd=checkout)
    # push to master. Note: we technically wouldn't need this from a pure git
    # pov, as a tag would be enough, but job-runner explicitly checks that
    # a commit is on the branch history, for security reasons
    git("push", "origin", "--force-with-lease", cwd=checkout)
