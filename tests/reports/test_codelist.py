from pathlib import Path

import numpy as np
import pandas as pd
import pipeline
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

# this is not nice, but will do until we can sort jobrunner out
from opensafely._vendor.jobrunner.cli import local_run
from pandas import testing

import reports.codelist
from reports.codelist.analysis import study_utils
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


@pytest.fixture()
def counts_table():
    """Returns a weekly counts table as produced by the codelist report."""
    return pd.DataFrame(
        {
            "practice": pd.Series([1, 2, 1, 2, 1, 2, 1, 2, 1, 2]),
            "date": pd.Series(
                [
                    "2019-01-01",
                    "2019-01-01",
                    "2019-01-08",
                    "2019-01-08",
                    "2019-01-15",
                    "2019-01-15",
                    "2019-01-22",
                    "2019-01-22",
                    "2019-01-29",
                    "2019-01-29",
                ]
            ),
            "num": pd.Series([3, 10, 1, 0, 4, 2, 5, 4, 8, 10]),
        }
    )


def test_convert_weekly_to_monthly(counts_table):
    obs = study_utils.convert_weekly_to_monthly(counts_table)
    exp = pd.DataFrame(
        {
            "practice": pd.Series([1, 2]),
            "date": pd.Series(
                [
                    "2019-01-08",
                    "2019-01-08",
                ]
            ),
            "num": pd.Series([18, 16]),
        }
    )
    testing.assert_frame_equal(obs, exp)


top_5_codes_params = [
    # no low numbers
    {
        "obs": {"code": ["01", "02", "03"], "num": [2, 80, 18]},
        "exp": {
            "Code": ["02", "Other"],
            "Description": ["code 2", "-"],
            "Proportion of codes (%)": [80.0, 20.0],
        },
    },
    # all low numbers (and total < threshold)
    {
        "obs": {"code": ["01", "02", "03"], "num": [2, 1, 1]},
        "exp": {"Code": [], "Description": [], "Proportion of codes (%)": []},
    },
    # all low numbers (and total > threshold)
    {
        "obs": {"code": ["01", "02", "03"], "num": [2, 3, 4]},
        "exp": {
            "Code": ["Other"],
            "Description": ["-"],
            "Proportion of codes (%)": [100.0],
        },
    },
    # low numbers with sum > total
    {
        "obs": {"code": ["01", "02", "03"], "num": [4, 4, 10]},
        "exp": {
            "Code": ["03", "Other"],
            "Description": ["code 3", "-"],
            "Proportion of codes (%)": [50.0, 50.0],
        },
    },
    # low numbers with sum < total
    {
        "obs": {"code": ["01", "02", "03"], "num": [2, 2, 10]},
        "exp": {
            "Code": ["Other"],
            "Description": ["-"],
            "Proportion of codes (%)": [100.0],
        },
    },
]

events_counts_params = [
    # no low numbers
    {
        "obs": {"count": [100, 8, 16]},
        "exp": {"count": [100, 10, 15]},
    },
    # all low numbers
    {
        "obs": {"count": [4, 1, 1]},
        "exp": {"count": [np.nan, np.nan, np.nan]},
    },
    # some low numbers
    {
        "obs": {"count": [12, 2, 3]},
        "exp": {"count": [10, np.nan, np.nan]},
    },
]


@pytest.fixture()
def codelist():
    """Returns a codelist like table."""
    return pd.DataFrame(
        {
            "code": pd.Series(["01", "02", "03"]),
            "term": pd.Series(["code 1", "code 2", "code 3"]),
        }
    )


@pytest.mark.parametrize("top_5_codes_params", top_5_codes_params)
def test_create_top_5_code_table(top_5_codes_params, codelist):

    # make a counts table
    counts_per_code_table = pd.DataFrame(
        {
            "code": pd.Series(top_5_codes_params["obs"]["code"]),
            "num": pd.Series(top_5_codes_params["obs"]["num"]),
        }
    )

    # make top 5 table using counts table
    obs = study_utils.create_top_5_code_table(
        counts_per_code_table, codelist, "code", "term", 5, 5
    )

    # get expected top 5 table
    exp = pd.DataFrame(
        {
            "Code": pd.Series(top_5_codes_params["exp"]["Code"], dtype=np.dtype(str)),
            "Description": pd.Series(
                top_5_codes_params["exp"]["Description"], dtype=np.dtype(str)
            ),
            "Proportion of codes (%)": pd.Series(
                top_5_codes_params["exp"]["Proportion of codes (%)"],
                dtype=np.dtype(float),
            ),
        },
    )

    # below fixes the typing if expected df is empty
    if exp["Code"].empty:
        exp["Code"] = exp["Code"].astype(str)
        exp["Description"] = exp["Description"].astype(str)
        exp["Proportion of codes (%)"] = exp["Proportion of codes (%)"].astype(float)

    testing.assert_frame_equal(obs, exp)


@pytest.mark.parametrize("events_counts_table", events_counts_params)
def test_redact_events_table(events_counts_table):

    # make events table

    events_table = pd.DataFrame(
        {"count": pd.Series(events_counts_table["obs"]["count"])},
        index=["total_events", "events_in_latest_period", "unique_patients"],
    )

    obs = study_utils.redact_events_table(events_table, 5, 5)

    exp = pd.DataFrame(
        {"count": pd.Series(events_counts_table["exp"]["count"])},
        index=["total_events", "events_in_latest_period", "unique_patients"],
    )

    testing.assert_frame_equal(obs, exp)


@st.composite
def distinct_strings_with_common_characters(draw):
    list_size = draw(st.integers(min_value=3, max_value=20))

    count_column = draw(
        st.lists(
            st.integers(min_value=0, max_value=1000000),
            min_size=list_size,
            max_size=list_size,
        )
    )
    code_column = draw(
        st.lists(
            st.text(min_size=1), min_size=list_size, max_size=list_size, unique=True
        )
    )
    assume(len(count_column) == len(code_column))

    count_column_name = draw(st.text(min_size=1))
    code_column_name = draw(st.text(min_size=1))
    assume(count_column_name != code_column_name)
    df = pd.DataFrame(
        data={count_column_name: count_column, code_column_name: code_column}
    )
    return df


# Test hits occasional long GC pauses so we need to tell Hypothesis
# not to worry about how long test case take to run.
hypothesis_settings = dict(deadline=None)


@given(
    distinct_strings_with_common_characters(), st.integers(min_value=1, max_value=10)
)
@settings(**hypothesis_settings)
def test_group_low_values(df, threshold):
    count_column, code_column = df.columns
    result = study_utils.group_low_values(df, count_column, code_column, threshold)

    assert list(result.columns) == list(df.columns)
    assert not (result[count_column] < threshold).any()
    suppressed_count = result.loc[result[code_column] == "Other", count_column].values
    assert len(suppressed_count) <= 1
    if len(suppressed_count) == 1:  # pragma: no cover
        assert suppressed_count.tolist()[0] >= threshold


@st.composite
def random_events_table(draw):
    total_events = draw(
        st.one_of(st.none(), st.integers(min_value=0, max_value=1000000))
    )
    events_in_latest_period = draw(
        st.one_of(st.none(), st.integers(min_value=0, max_value=1000000))
    )
    unique_patients = draw(
        st.one_of(st.none(), st.integers(min_value=0, max_value=1000000))
    )

    df = pd.DataFrame(
        {
            "total_events": total_events,
            "events_in_latest_period": events_in_latest_period,
            "unique_patients": unique_patients,
        },
        index=["count"],
    )
    return df


@given(
    random_events_table(),
    st.integers(min_value=1, max_value=1000),
    st.integers(min_value=1, max_value=10),
)
def test_redact_events_table_hypothesis(df, threshold, rounding_base):
    result = study_utils.redact_events_table(df.T, threshold, rounding_base)

    assert list(result.columns) == list(df.T.columns)
    numeric = result[result["count"].apply(lambda x: isinstance(x, (int, float)))]
    assert not (numeric["count"] < threshold).any()
