import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def write_to_csv(filename, data, row_count, test_machine, repeats):
    """Generating a CSV file with performance results from the test run."""
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)

        csv_writer.writerow(
            ["Number of rows:", row_count, "Test Environment:", test_machine]
        )

        csv_contents = [
            "Query",
            "ClickHouse version",
            "DuckDB version",
            "ClickHouse Query Runtime",
            "DuckDB Query Runtime",
            "ClickHouse Query Description",
            "DuckDB Query Description",
        ]

        for i in range(repeats):
            csv_contents.append(f"ClickHouse sample {i}")

        for i in range(repeats):
            csv_contents.append(f"DuckDB sample {i}")

        csv_writer.writerow(csv_contents)

        for row in data:
            csv_writer.writerow(row)


def convert_to_markdown(csv_file, markdown_name, query):
    """Converting the CSV report of a Parquet performance test program into a markdown file."""
    data = pd.read_csv(csv_file, skiprows=1)

    query_dictionary = {}

    for i in query:
        query_dictionary[i[0]] = i[5]

    with open(markdown_name, "w") as f:
        f.write("# ClickHouse vs DuckDB (Runtime in Seconds)\n\n")
        f.write("## Bar Chart\n")
        f.write("![Bar Chart](bar_chart.png)\n")
        for index, row in data.iterrows():
            clickhouse_runtime = row["ClickHouse Query Runtime"]
            duckdb_runtime = row["DuckDB Query Runtime"]
            query_number = row["Query"]
            f.write(f"# {query_number}\n")
            f.write(f"```sql\n {query_dictionary[query_number]}\n```\n")
            f.write(
                f"""
```mermaid
     pie showData
         "ClickHouse" : {clickhouse_runtime}
         "DuckDB" : {duckdb_runtime}
```\n"""
            )


def create_bar_chart(csv_file, png_path):
    data = pd.read_csv(csv_file, skiprows=1)

    names = ()
    values = {
        "ClickHouse": (),
        "DuckDB": (),
    }

    for index, row in data.iterrows():
        clickhouse = row["ClickHouse Query Runtime"]
        duckdb = row["DuckDB Query Runtime"]
        query = row["Query"]

        names += (query,)

        values["ClickHouse"] += (clickhouse,)
        values["DuckDB"] += (duckdb,)

    y = np.arange(len(names))  # the label locations
    height = 0.25  # the height of the bars
    multiplier = 0

    # Set a larger figure size
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust the width and height as needed

    # Specify hex color codes for the bars
    bar_colors = ["#be362b", "#4285f4"]  # Example hex codes

    for attribute, measurement, color in zip(
        values.keys(), values.values(), bar_colors
    ):
        offset = height * multiplier
        rects = ax.barh(y + offset, measurement, height, label=attribute, color=color)
        multiplier += 1

    ax.set_xlabel("Runtime (Sec)")
    ax.set_title("ClickHouse vs DuckDB")
    ax.set_yticks(y + height / 2)
    ax.set_yticklabels(names)
    ax.legend(loc="upper right", ncol=1)

    plt.tight_layout()

    # Save the chart as a PNG file
    plt.savefig(png_path)
