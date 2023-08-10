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
