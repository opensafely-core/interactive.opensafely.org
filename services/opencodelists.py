def fetch():

    # Fetch codelists from https://www.opencodelists.org/api/v1/codelist/opensafely/?coding_system_id=snomedct
    return [
        (
            "opensafely/assessment-instruments-and-outcome-measures-for-long-covid",
            "Assessment instruments and outcome measures for long covid",
        ),
        ("opensafely/systolic-blood-pressure-qof", "Systolic blood pressure QoF"),
        (
            "opensafely/chronic-cardiac-disease-snomed",
            "Chronic Cardiac Disease (SNOMED)",
        ),
    ]
