import pandas as pd
from study_utils import create_top_5_code_table, write_csv
from variables import low_count_threshold, output_dir, release_dir, rounding_base


def main():
    code_df = pd.read_csv(f"{output_dir}/counts_per_code.csv")
    codelist = pd.read_csv("codelist.csv")

    top_5_code_table = create_top_5_code_table(
        df=code_df,
        code_df=codelist,
        code_column="code",
        term_column="term",
        low_count_threshold=low_count_threshold,
        rounding_base=rounding_base,
    )
    write_csv(top_5_code_table, release_dir / "top_5_code_table.csv", index=False)


if __name__ == "__main__":
    main()
