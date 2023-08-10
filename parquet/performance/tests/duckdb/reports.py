import csv


def write_to_csv(filename, data):
    """Generating a CSV file with performance results from the test run."""
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            [
                "Query",
                "ClickHouse version",
                "DuckDB version" "ClickHouse Query Runtime",
                "DuckDB Query Runtime",
                "ClickHouse Query Description",
                "DuckDB Query Description",
            ]
        )

        for row in data:
            csv_writer.writerow(row)
