import textwrap

import requests
from environs import Env
from furl import furl


env = Env()


BASE_URL = "https://api.github.com"
GITHUB_TOKEN = env.str("GITHUB_TOKEN")


session = requests.Session()
session.headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "User-Agent": "OpenSAFELY Interactive",
}


def create_issue(analysis_request_id, job_server_url):
    body = f"""
    **This is a public issue. Use this to approve or reject the outputs below but do not discuss any disclosure concerns in this issue.**

    Workspace: {job_server_url}

    The below outputs are located in `output/{analysis_request_id}`
    - [ ] event_counts.csv
    - [ ] deciles_chart_counts_per_week_per_practice.png
    - [ ] top_5_code_table.csv
    - [ ] practice_count.csv

    The number of practices plotted in the deciles chart is shown in `practice_count.csv`. Check that a sufficient number of practices are included.

    The total number of events, total number of patients and the number of events within the last time period are in `event_counts.csv`. Check that these do not contain any values <=5.

    The unredacted counts underlying `top_5_code_table.csv` can be found in `counts_per_code.csv` . Check that no code with a count <=5 in `counts_per_code.csv` is included in `top_5_code_table.csv`.
    """

    f = furl(BASE_URL)
    f.path.segments += [
        "repos",
        "opensafely",
        "interactive",
        "issues",
    ]

    data = {
        "title": str(analysis_request_id),
        "body": textwrap.dedent(body),
        "labels": ["interactive"],
    }

    r = session.post(f.url, json=data)
    r.raise_for_status()

    return r.json()["html_url"]
