import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def sort_csv_data(data):
    merged_data = {}

    for item in data:
        key = item[0][-1]
        if key in merged_data:
            merged_data[key].append(item)
        else:
            merged_data[key] = [item]

    result = []

    for key in merged_data:
        if len(merged_data[key]) > 1:
            merged_items = tuple(
                [item for sublist in merged_data[key] for item in sublist]
            )
            result.append(merged_items)
        else:
            result.extend(merged_data[key])

    return result


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
            "ClickHouse Query Runtime",
            "ClickHouse Query Description",
            "Query DuckDB",
            "DuckDB version",
            "DuckDB Query Runtime",
            "DuckDB Query Description",
        ]

        clickhouse_samples_position = 4

        for i in range(repeats):
            csv_contents.insert(clickhouse_samples_position, f"ClickHouse sample {i}")
            clickhouse_samples_position += 1

        for i in range(repeats):
            csv_contents.append(f"DuckDB sample {i}")

        csv_writer.writerow(csv_contents)

        corrected_data = sort_csv_data(data)

        for row in corrected_data:
            csv_writer.writerow(row)


def convert_to_markdown(csv_file, markdown_name, query):
    """Converting the CSV report of a Parquet performance test program into a markdown file."""
    data = pd.read_csv(csv_file, skiprows=1)

    query_dictionary = {}

    for i in query:
        query_dictionary[i[0]] = i[3]

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
    """Converting the CSV report of a Parquet performance test program into a bar chart png file."""
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

    y = np.arange(len(names))
    height = 0.25
    multiplier = 0

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_colors = ["#be362b", "#4285f4"]

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

    plt.savefig(png_path)
