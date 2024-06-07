import pandas as pd


def generate_bloom_report(data, filename=None, csv_filename="bloom_report.csv"):
    """Generate a bloom report from a dictionary of data."""
    if filename is None:
        filename = "README.md"

    df = pd.DataFrame(
        {
            "file": [],
            "condition": [],
            "filter": [],
            "rows_skipped": [],
            "total_rows": [],
            "elapsed": [],
        }
    )

    for file, conditions in data.items():
        for condition, filters in conditions.items():
            for filter, values in filters.items():
                df = df._append(
                    {
                        "file": file,
                        "condition": condition,
                        "filter": filter,
                        "rows_skipped": int(values["rows_skipped"]),
                        "total_rows": int(values["total_rows"]),
                        "elapsed": float(values["elapsed"]),
                    },
                    ignore_index=True,
                )

    df["rows_skipped"] = df["rows_skipped"].astype(int)
    df["total_rows"] = df["total_rows"].astype(int)

    with open(f"{filename}", "w") as f:
        f.write("# Bloom Filter Performance Report\n")
        for file, group in df.groupby("file"):
            f.write(f"\n## {file}\n")
            markdown_table = group.to_markdown(index=False)
            f.write(markdown_table)
            f.write("\n")

    df.to_csv(csv_filename, index=False)
