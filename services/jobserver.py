import csv
from base64 import b64encode

from django.conf import settings

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
    file_types = [DecilesChart, EventsCount, CommonCodes]
    for file in response.json()["files"]:
        for file_type in file_types:
            if file_type.exists(file, analysis_request_id):
                output[file_type.name] = file_type.decode(file)

    return output


def fetch_file(url):
    response = job_server(url)
    return response.content


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
