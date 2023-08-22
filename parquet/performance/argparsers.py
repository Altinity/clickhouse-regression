from helpers.argparser import argparser as base_argparser


def argparser(parser):
    """Custom argperser that add --duckdb-binary-path option."""
    base_argparser(parser)

    parser.add_argument(
        "--duckdb-binary-path",
        type=str,
        dest="duckdb_binary_path",
        help="path to duckdb binary, default: /usr/bin/duckdb",
        metavar="path",
        required=True,
    )

    parser.add_argument(
        "--from-year",
        type=str,
        dest="from_year",
        help="Used to determine the starting year for downloading the large ontime dataset from the Bureau of Transportation Statistics",
        metavar="value",
        default=1987,
    )

    parser.add_argument(
        "--to-year",
        type=str,
        dest="to_year",
        help="Used to determine the end year for downloading the large ontime dataset from the Bureau of Transportation Statistics",
        metavar="value",
        default=2015,
    )

    parser.add_argument(
        "--threads",
        type=str,
        dest="threads",
        help="Used to determine the number of threads used in creating a parquet file with large dataset",
        metavar="value",
        default=20,
    )

    parser.add_argument(
        "--max-memory-usage",
        type=str,
        dest="max_memory_usage",
        help="Used to determine The maximum amount of RAM to use for running a query on a single server (values used in bytes)",
        metavar="value",
        default=0,
    )

    parser.add_argument(
        "--compression",
        type=str,
        dest="compression",
        help="Used to determine compression used for inserting into outfile",
        metavar="value",
        default=None,
    )

    parser.add_argument(
        "--rerun-queries",
        type=str,
        dest="rerun_queries",
        help="Used to determine the number of time to rerun each query for performance test",
        metavar="value",
        default=3,
    )

    parser.add_argument(
        "--filename",
        type=str,
        dest="filename",
        help="Used to determine the name of the csv file",
        metavar="value",
        default="query.csv",
    )
