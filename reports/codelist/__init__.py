import shutil
from pathlib import Path


low_count_threshold = 100
rounding_base = 10

PROJECT_YAML = """
version: '3.0'

expectations:
  population_size: 1000

actions:

  codelist_report_{id}:
    run: >
      cohortextractor:latest generate_codelist_report
        --codelist-path=codelist.csv
        --start-date={start_date}
        --end-date={end_date}
        --output-dir output/{id}
    outputs:
      moderately_sensitive:
        table: output/{id}/counts_per_*.csv
        list_sizes: output/{id}/list_sizes.csv
        patient_count_table: output/{id}/patient_count.csv

  measures_{id}:
    run: >
      python:latest python analysis/generate_measures.py
        --start-date={start_date}
        --end-date={end_date}
        --output-dir output/{id}
        --low-count-threshold {low_count_threshold}
        --rounding-base {rounding_base}
    needs: [codelist_report_{id}]
    outputs:
      moderately_sensitive:
        measure: output/{id}/measure_counts_per_week_per_practice.csv
        events_count_table: output/{id}/event_counts.csv
        practice_count_table: output/{id}/practice_count.csv

  top_5_table_{id}:
    run: >
      python:latest python analysis/top_codes_table.py
        --start-date={start_date}
        --end-date={end_date}
        --output-dir output/{id}
        --low-count-threshold {low_count_threshold}
        --rounding-base {rounding_base}
    needs: [codelist_report_{id}]
    outputs:
      moderately_sensitive:
        table: output/{id}/top_5_code_table.csv

  deciles_charts_{id}:
    run: >
      deciles-charts:v0.0.24
        --input-files output/{id}/measure_counts_per_week_per_practice.csv
        --output-dir output/{id}
    config:
      show_outer_percentiles: false
      tables:
        output: true
      charts:
        output: true
    needs: [measures_{id}]
    outputs:
      moderately_sensitive:
        deciles_charts: output/{id}/deciles_*.*
"""


# Note: this will only work when CWD is the project root. We may want to do
# something more robust in future
action_directory = Path("reports/codelist")


def write_files(checkout, analysis_request, codelist):
    # this needs to be a fixed name, or else we'll litter HEAD with
    # previous codelists
    shutil.copytree(
        action_directory,
        checkout,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__init__.py"),
    )

    codelist_path = checkout / "codelist.csv"
    codelist_path.write_text(codelist)

    project_path = checkout / "project.yaml"
    project_yaml = PROJECT_YAML.format(
        id=str(analysis_request.id),
        start_date=analysis_request.start_date,
        end_date=analysis_request.end_date,
        low_count_threshold=low_count_threshold,
        rounding_base=rounding_base,
    )
    project_path.write_text(project_yaml)
