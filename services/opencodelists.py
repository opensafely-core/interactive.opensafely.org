import requests


def fetch():

    response = requests.get(
        "https://www.opencodelists.org/api/v1/codelist/?coding_system_id=snomedct&tag=allowed-for-opensafely-interactive"
    )
    response.raise_for_status()

    return [
        (codelist["full_slug"], codelist["name"])
        for codelist in response.json()["codelists"]
    ]
