import numpy as np
import pandas as pd


def group_low_values(df, count_column, code_column, threshold):
    """Suppresses low values and groups suppressed values into
    a new row "Other".

    Args:
        df: A measure table of counts by code.
        count_column: The name of the count column in the measure table.
        code_column: The name of the code column in the codelist table.
        threshold: Redaction threshold to use
    Returns:
        A table with redacted counts
    """

    # get sum of any values <= threshold
    suppressed_count = df.loc[df[count_column] <= threshold, count_column].sum()
    suppressed_df = df.loc[df[count_column] > threshold, count_column]

    # if suppressed values >0 ensure total suppressed count > threshold.
    # Also suppress if all values 0
    if (suppressed_count > 0) | (
        (suppressed_count == 0) & (len(suppressed_df) != len(df))
    ):

        # redact counts <= threshold
        df.loc[df[count_column] <= threshold, count_column] = np.nan

        # If all values 0, suppress them
        if suppressed_count == 0:
            df.loc[df[count_column] == 0, :] = np.nan

        else:
            # if suppressed count <= threshold redact further values
            while suppressed_count <= threshold:
                suppressed_count += df[count_column].min()
                df.loc[df[count_column].idxmin(), :] = np.nan

        # drop all rows where count column is null
        df = df.loc[df[count_column].notnull(), :]

        # add suppressed count as "Other" row (if > threshold)
        if suppressed_count > threshold:
            suppressed_count = {"code": "Other", count_column: suppressed_count}
            df = pd.concat([df, pd.DataFrame([suppressed_count])], ignore_index=True)

    return df


def create_top_5_code_table(
    df, code_df, code_column, term_column, low_count_threshold, rounding_base, nrows=5
):
    """Creates a table of the top 5 codes recorded with the number of events and % makeup of each code.
    Args:
        df: A measure table.
        code_df: A codelist table.
        code_column: The name of the code column in the codelist table.
        term_column: The name of the term column in the codelist table.
        measure: The measure ID.
        low_count_threshold: Value to use as threshold for disclosure control.
        rounding_base: Base to round to.
        nrows: The number of rows to display.
    Returns:
        A table of the top `nrows` codes.
    """

    # cast both code columns to str
    df[code_column] = df[code_column].astype(str)
    code_df[code_column] = code_df[code_column].astype(str)

    # sum event counts over patients
    event_counts = df.sort_values(ascending=False, by="num")

    event_counts = group_low_values(
        event_counts, "num", code_column, low_count_threshold
    )

    # round

    event_counts["num"] = event_counts["num"].apply(
        lambda x: round_values(x, rounding_base)
    )

    # calculate % makeup of each code
    total_events = event_counts["num"].sum()
    event_counts["Proportion of codes (%)"] = round(
        (event_counts["num"] / total_events) * 100, 2
    )

    # Gets the human-friendly description of the code for the given row
    # e.g. "Systolic blood pressure".
    code_df[code_column] = code_df[code_column].astype(str)
    code_df = code_df.set_index(code_column).rename(
        columns={term_column: "Description"}
    )

    event_counts = event_counts.set_index(code_column).join(code_df).reset_index()

    # set description of "Other column" to something readable
    event_counts.loc[event_counts[code_column] == "Other", "Description"] = "-"

    # Rename the code column to something consistent
    event_counts.rename(columns={code_column: "Code"}, inplace=True)

    # drop events column
    event_counts = event_counts.loc[
        :, ["Code", "Description", "Proportion of codes (%)"]
    ]

    # return top n rows
    return event_counts.head(5)


def calculate_rate(df, value_col, rate_per=1000, round_rate=False):
    """Calculates the number of events per 1,000 of the population.
    This function operates on the given measure table in-place, adding
    a `rate` column.
    Args:
        df: A measure table.
        value_col: The name of the numerator column in the measure table.
        population_col: The name of the denominator column in the measure table.
        round: Bool indicating whether to round rate to 2dp.
    """
    if round_rate:
        rate = round(df[value_col] * rate_per, 2)

    else:
        rate = df[value_col] * rate_per

    return rate


def round_values(x, base=5):
    rounded = x
    if isinstance(x, (int, float)):
        if np.isnan(x):
            rounded = np.nan
        else:
            rounded = int(base * round(x / base))
    return rounded


def redact_events_table(events_counts, low_count_threshold, rounding_base):
    # redact low counts
    events_counts[events_counts <= low_count_threshold] = f"<={low_count_threshold}"

    # round
    events_counts["count"] = events_counts["count"].apply(
        lambda x: round_values(x, base=rounding_base)
    )

    return events_counts


def convert_weekly_to_monthly(counts_table):
    """Converts a counts table of practice-level weekly counts to counts aggregated
    every 4 weeks. Where the number of weeks is not divisible by 4, the earliest weeks
    are dropped to ensure number of weeks is a multiple of 4.
    """

    dates = counts_table["date"].sort_values(ascending=True).unique()

    # drop earliest weeks if number of weeks not a multiple of 4.
    num_dates = len(dates)
    num_dates_over = num_dates % 4
    if num_dates_over != 0:
        # drop rows from counts table
        counts_table = counts_table.loc[
            ~counts_table["date"].isin(dates[0:num_dates_over]), counts_table.columns
        ]

        # drop dates from dates list
        dates = dates[num_dates_over:]

    # create 4 weekly date
    dates_map = {}
    for i in range(0, len(dates), 4):
        date_group = dates[i : i + 4]
        for date in date_group:
            dates_map[date] = date_group[0]
    counts_table.loc[counts_table.index, "date"] = counts_table.loc[
        counts_table.index, "date"
    ].map(dates_map)

    # group into 4 weeks
    counts_table = (
        (counts_table.groupby(by=["practice", "date"])[["num"]].sum().reset_index())
        .sort_values(by=["date"])
        .reset_index(drop=True)
    )

    return counts_table
