import operator

from services import session


LIST_URL = "https://www.opencodelists.org/api/v1/codelist/?coding_system_id=snomedct&tag=allowed-for-opensafely-interactive"


def fetch():
    """Return valid codelists to choose."""
    response = session.get(LIST_URL)
    response.raise_for_status()

    codelists = []
    for codelist in response.json()["codelists"]:
        published_versions = [
            v for v in codelist["versions"] if v["status"] == "published"
        ]
        if published_versions:
            codelists.append(
                {
                    "slug": published_versions[-1]["full_slug"],
                    "name": codelist["name"],
                    "organisation": codelist["organisation"],
                }
            )

    return sorted(codelists, key=operator.itemgetter("name"))


def get_codelist(slug):
    """Get the contents of a codelist."""
    response = session.get(
        f"https://www.opencodelists.org/codelist/{slug}/download.csv"
    )
    response.raise_for_status()
    return response.text
