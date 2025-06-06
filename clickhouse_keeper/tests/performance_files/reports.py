import csv


def create_csv_file(
    test_results_file_name: str = "test_file",
    repeats: int = 1,
    inserts: int = 1,
    configurations_insert_time_values: dict = None,
    setups: list = None,
):
    """Auto csv creation for performance tests."""

    configurations_sorted_by_min_insert_time = sorted(
        configurations_insert_time_values.items(), key=lambda x: x[1]
    )

    with open(
        f"performance_reports/{test_results_file_name}.csv",
        "a",
        encoding="UTF8",
        newline="",
    ) as f:
        writer = csv.writer(f)

        writer.writerow(["repeats", repeats, "inserts", inserts])

        comparison_setups = setups

        for setup in comparison_setups:
            min_inserts_times = ["minimum insert times:"]
            buffer_list = ["configuration:"]
            for configuration in configurations_sorted_by_min_insert_time:
                if setup in configuration[0] or setup == setups[0]:
                    if setup == setups[0]:
                        min_inserts_times.append(min(configuration[1]))
                    buffer_list.append(configuration[0])

            if setup == setups[0]:
                writer.writerow(min_inserts_times)

            if (
                len(buffer_list) != len(configurations_sorted_by_min_insert_time) + 1
                or setup == setups[0]
            ):
                writer.writerow([setup])

                writer.writerow(buffer_list)

                for first_configuration in configurations_sorted_by_min_insert_time:
                    if setup not in first_configuration[0] or setup == setups[0]:
                        buffer_list = [first_configuration[0]]
                        for (
                            second_configuration
                        ) in configurations_sorted_by_min_insert_time:
                            if setup in second_configuration[0] or setup == setups[0]:
                                buffer_list.append(
                                    float(
                                        (
                                            min(first_configuration[1])
                                            - min(second_configuration[1])
                                        )
                                        / min(first_configuration[1])
                                    )
                                )
                        writer.writerow(buffer_list)
                writer.writerow(" ")


def create_markdown_and_html_reports(
    test_results_file_name: str = "test_file",
    configurations_insert_time_values: dict = None,
):
    """Auto report creation for performance tests in .md and .html formats."""

    data = sorted(configurations_insert_time_values.items(), key=lambda x: x[1])

    header = "# Performance tests report\n\n"

    table = (
        f"| " + "| ".join(f"{config[0]}" for config in data) + " |\n"
        f"| - " + "| - ".join("" for config in data) + " |\n"
        f"| " + "| ".join(f"{min(config[1])}" for config in data) + " |\n\n"
    )

    min_insert_time_report = (
        f"In the current performance test run "
        + ", ".join(f' "{config[0]}"' for config in data)
        + f" ClickHouse versions were tested. The worst minimum insert time was for"
        f' "{data[-1][0]}" and the best one was for "{data[0][0]}"'
    )

    with open(f"performance_reports/{test_results_file_name}.md", "w") as f:
        f.write(header + table + min_insert_time_report)
