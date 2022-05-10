from services import session


LIST_URL = "https://www.opencodelists.org/api/v1/codelist/?coding_system_id=snomedct&tag=allowed-for-opensafely-interactive"


def fetch():
    """Return valid codelists to choose."""
    response = session.get(LIST_URL)
    response.raise_for_status()

    return [
        (codelist["full_slug"], codelist["name"])
        for codelist in response.json()["codelists"]
    ]


def get_codelist(slug):
    """Get the contents of a codelist."""
    response = session.get(f"https://www.opencodelists.org/codelist/{slug}")
    response.raise_for_status()
    return response.text
