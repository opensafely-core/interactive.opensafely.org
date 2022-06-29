from pathlib import Path

import pandas as pd
import pipeline
import pytest

# this is not nice, but will do until we can sort jobrunner out
from opensafely._vendor.jobrunner.cli import local_run

import reports.codelist
from tests.factories import AnalysisRequestFactory


def test_write_files(tmp_path):
    analysis_request = AnalysisRequestFactory()
    reports.codelist.write_files(tmp_path, analysis_request, "codelist data")

    project = tmp_path / "project.yaml"
    codelist_csv = tmp_path / "codelist.csv"

    assert codelist_csv.read_text() == "codelist data"

    assert not Path(tmp_path / "__init__.py").exists()

    p = pipeline.load_pipeline(project)

    output_dir = f"output/{analysis_request.id}"

    for name, action in p.actions.items():
        assert f"--output-dir {output_dir}" in action.run.args

    assert (
        analysis_request.start_date
        in p.actions[f"codelist_report_{analysis_request.id}"].run.args
    )
    assert (
        analysis_request.end_date
        in p.actions[f"codelist_report_{analysis_request.id}"].run.args
    )


@pytest.mark.integration
def test_codelist_report(tmp_path):
    analysis_request = AnalysisRequestFactory()

    # write dummy codelist that matches the codes in
    rows = [("code,term")]
    rows.extend(f"{i},code_{i}" for i in range(16))
    reports.codelist.write_files(tmp_path, analysis_request, "\n".join(rows))

    # just check that it runs w/o error
    assert local_run.main(tmp_path, ["run_all"])

    output_dir = tmp_path / "output" / str(analysis_request.id)
    release_dir = output_dir / "for_release"

    pd.read_csv(output_dir / "counts_per_code.csv")
    pd.read_csv(output_dir / "counts_per_week_per_practice.csv")
    pd.read_csv(output_dir / "list_sizes.csv")
    pd.read_csv(output_dir / "measure_counts_per_week_per_practice.csv")
    pd.read_csv(output_dir / "patient_count.csv")

    # for_release files
    pd.read_csv(release_dir / "event_counts.csv")
    pd.read_csv(release_dir / "practice_count.csv")
    pd.read_csv(release_dir / "top_5_code_table.csv")
    assert (release_dir / "deciles_chart_counts_per_week_per_practice.png").exists()

    # we don't want this
    assert not (release_dir / "deciles_chart_counts_per_week_per_practice.csv").exists()
