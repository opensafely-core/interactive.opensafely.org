import numpy as np
import pandas as pd
from study_utils import (
    calculate_rate,
    convert_weekly_to_monthly,
    redact_events_table,
    round_values,
)
from variables import (
    low_count_threshold,
    output_dir,
    rounding_base,
    rounding_base_practice_count,
)


def practice_counts(counts_table, list_sizes):
    # get number of weeks. If >52, convert to monthly

    dates = counts_table["date"].unique()

    if len(dates) > 52:
        counts_table = convert_weekly_to_monthly(counts_table)

    counts_table = counts_table.merge(list_sizes, on=["practice"], how="inner")

    counts_table["value"] = counts_table["num"] / counts_table["list_size"]
    counts_table["value"] = calculate_rate(counts_table, "value", round_rate=True)

    practice_count_total = len(np.unique(list_sizes["practice"]))
    practice_count_with_events = len(np.unique(counts_table["practice"]))

    practice_count = pd.DataFrame(
        {
            "total": practice_count_total,
            "with_at_least_1_event": practice_count_with_events,
        },
        index=["count"],
    )

    # round
    for column in practice_count.columns:

        practice_count[column] = practice_count[column].apply(
            lambda x: round_values(x, base=rounding_base_practice_count)
        )

    return practice_count, counts_table


def total_events_counts(counts_table, patient_count):
    # count total number of events
    total_events = int(counts_table["num"].sum())

    # total events in last week/month
    latest_time_period = counts_table["date"].max()
    events_in_latest_period = int(
        counts_table.loc[counts_table["date"] == latest_time_period, "num"].sum()
    )

    events_counts = pd.DataFrame(
        {
            "total_events": total_events,
            "events_in_latest_period": events_in_latest_period,
            "unique_patients": patient_count,
        },
        index=["count"],
    )

    events_counts = events_counts.T
    return events_counts


def main():

    patient_count_table = pd.read_csv(f"{output_dir}/patient_count.csv")
    patient_count = patient_count_table["num"][0]

    counts_table = pd.read_csv(
        f"{output_dir}/counts_per_week_per_practice.csv", parse_dates=["date"]
    )
    list_sizes = pd.read_csv(f"{output_dir}/list_sizes.csv")

    practice_count, counts_table = practice_counts(counts_table, list_sizes)
    events_counts = total_events_counts(counts_table, patient_count)

    practice_count.T.to_csv(f"{output_dir}/practice_count.csv")
    counts_table.to_csv(
        f"{output_dir}/measure_counts_per_week_per_practice.csv", index=False
    )
    redact_events_table(events_counts, low_count_threshold, rounding_base).to_csv(
        f"{output_dir}/event_counts.csv"
    )


if __name__ == "__main__":
    main()
