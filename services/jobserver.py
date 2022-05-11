import csv
from base64 import b64encode
from urllib.parse import urljoin

from environs import Env

from services import session


env = Env()

JOB_SERVER_URL = env.str("JOB_SERVER_API")
JOB_SERVER_TOKEN = env.str("JOB_SERVER_TOKEN")
RELEASES_URL = urljoin(
    JOB_SERVER_URL,
    "api/v2/releases/workspace/test-interactive",
)


def fetch_release(analysis_request_id):
    headers = {"Authorization": JOB_SERVER_TOKEN}
    response = session.get(
        RELEASES_URL,
        headers=headers,
    )
    response.raise_for_status()

    output = {}
    for file in response.json()["files"]:
        if DecilesChart.exists(file, analysis_request_id):
            output[DecilesChart.name] = DecilesChart.decode(file)
        elif EventsCount.exists(file, analysis_request_id):
            output[EventsCount.name] = EventsCount.decode(file)
        elif CommonCodes.exists(file, analysis_request_id):  # pragma: no cover
            output[CommonCodes.name] = CommonCodes.decode(file)

    return output


def fetch_file(url):
    headers = {"Authorization": JOB_SERVER_TOKEN}
    response = session.get(urljoin(JOB_SERVER_URL, url), headers=headers)
    response.raise_for_status()

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
