from helpers.argparser import argparser as base_argparser


def argparser(parser):
    """Custom argperser that add --duckdb-binary-path option."""
    base_argparser(parser)

    parser.add_argument(
        "--duckdb-binary-path",
        type=str,
        dest="duckdb_binary_path",
        help="path to duckdb binary",
        metavar="path",
        required=True,
    )

    parser.add_argument(
        "--from-year",
        type=str,
        dest="from_year",
        help="determines the starting year for downloading the large ontime dataset from the Bureau of Transportation Statistics",
        metavar="value",
        default=1987,
    )

    parser.add_argument(
        "--to-year",
        type=str,
        dest="to_year",
        help="determines the end year for downloading the large ontime dataset from the Bureau of Transportation Statistics",
        metavar="value",
        default=2022,
    )

    parser.add_argument(
        "--threads",
        type=str,
        dest="threads",
        help="determines the number of threads used in creating a parquet file with large dataset",
        metavar="value",
        default=20,
    )

    parser.add_argument(
        "--max-memory-usage",
        type=str,
        dest="max_memory_usage",
        help="sets the maximum amount of RAM to use for running a query on a single server, 0 sets it to "
        "unlimited (values used in bytes)",
        metavar="value",
        default=0,
    )

    parser.add_argument(
        "--compression",
        type=str,
        dest="compression",
        help="determines compression used for inserting into a parquet file",
        metavar="value",
        default="snappy",
    )

    parser.add_argument(
        "--rerun-queries",
        type=str,
        dest="rerun_queries",
        help="determines the number of times each query in the steps file will be run",
        metavar="value",
        default=3,
    )

    parser.add_argument(
        "--filename",
        type=str,
        dest="filename",
        help="determines the name of the csv file that contains the report of the test run",
        metavar="value",
        default="performance.csv",
    )

    parser.add_argument(
        "--test-machine",
        type=str,
        dest="test_machine",
        help="the name of the test environment",
        metavar="value",
        default=None,
    )
