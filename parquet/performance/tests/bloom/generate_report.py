import pandas as pd

def generate_bloom_report(data, filename=None):
    """Generate a bloom report from a dictionary of data."""
    if filename is None:
        filename = "README.md"

    df = pd.DataFrame(
        {"file": [], "condition": [], "filter": [], "rows_skipped": [], "elapsed": [], "query": []}
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
                        "elapsed": float(values["elapsed"]),
                        "query": values["query"],
                    },
                    ignore_index=True,
                )

    df["rows_skipped"] = df["rows_skipped"].astype(int)

    with open(f"{filename}", "w") as f:
        for file, group in df.groupby('file'):
            f.write(f"\n## {file}\n")
            markdown_table = group.to_markdown()
            f.write(markdown_table)
            f.write("\n")