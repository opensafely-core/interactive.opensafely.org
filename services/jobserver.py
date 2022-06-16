import csv
from base64 import b64encode

from django.conf import settings
from furl import furl

from services import session


RELEASES_PATH = f"/api/v2/releases/workspace/{settings.JOB_SERVER_WORKSPACE}"


def job_server(path):
    headers = {"Authorization": settings.JOB_SERVER_TOKEN}
    response = session.get(
        str(settings.JOB_SERVER_URL / path),
        headers=headers,
    )
    response.raise_for_status()
    return response


def fetch_release(analysis_request_id):
    response = job_server(RELEASES_PATH)
    output = {}
    file_types = [DecilesChart, EventsCount, CommonCodes, PracticeCount]

    for file in response.json()["files"]:
        for file_type in file_types:
            if file_type.exists(file, analysis_request_id):
                output[file_type.name] = file_type.decode(file)

    return output


def fetch_file(url):
    response = job_server(url)
    return response.content


def submit_job_request(analysis_request, project_yaml):
    headers = {"Authorization": settings.JOB_SERVER_TOKEN}

    # we're constructing the furl object in this style, instead of using its
    # overloaded __divmod__ method, because it's [marginally] clearer that the
    # URL needs a trailing slash.  job-server's URLs all use a trailing slash
    # and Django can't redirect POST requests and maintain the POST data.
    f = furl(settings.JOB_SERVER_URL)
    f.path = "api/v2/job-requests/"

    data = {
        "backend": "tpp",
        "workspace": settings.JOB_SERVER_WORKSPACE,
        "sha": analysis_request.commit_sha,
        "project_definition": project_yaml,
        "requested_actions": ["run_all"],
        "force_run_dependencies": True,
    }

    r = session.post(f.url, headers=headers, json=data)

    r.raise_for_status()

    return r.json()["url"]


class DecilesChart:
    name = "deciles_chart"

    def exists(file, analysis_request_id):
        return analysis_request_id in file["name"] and file["name"].endswith(
            "deciles_chart_counts_per_week_per_practice.png"
        )

    def decode(file):
        return b64encode(fetch_file(file["url"])).decode("utf-8")


class EventsCount:
    name = "summary"

    def exists(file, analysis_request_id):
        return analysis_request_id in file["name"] and file["name"].endswith(
            "event_counts.csv"
        )

    def decode(file):
        return EventsCount.read_event_counts(fetch_file(file["url"]))

    def read_event_counts(file):
        return list(csv.DictReader(file.decode("utf-8").splitlines()))


class CommonCodes:
    name = "common_codes"

    def exists(file, analysis_request_id):
        return analysis_request_id in file["name"] and file["name"].endswith(
            "top_5_code_table.csv"
        )

    def decode(file):
        return CommonCodes.read_common_codes(fetch_file(file["url"]))

    def read_common_codes(file):
        common_codes = list(csv.DictReader(file.decode("utf-8").splitlines()))
        for line in common_codes:
            line["Proportion"] = line.get("Proportion of codes (%)")
        return common_codes


class PracticeCount:
    name = "practices"

    def exists(file, analysis_request_id):
        return analysis_request_id in file["name"] and file["name"].endswith(
            "practice_count.csv"
        )

    def decode(file):
        return PracticeCount.read_practice_counts(fetch_file(file["url"]))

    def read_practice_counts(file):
        practice_list = list(csv.DictReader(file.decode("utf-8").splitlines()))
        practice_counts = {
            "total": practice_list[0].get("count", 0) if len(practice_list) > 0 else 0,
            "with_at_least_1_event": practice_list[1].get("count", 0)
            if len(practice_list) > 1
            else 0,
        }
        return practice_counts
