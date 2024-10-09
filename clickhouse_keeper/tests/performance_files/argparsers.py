from helpers.common import getuid

from helpers.argparser import argparser as base_argparser


def argparser(parser):
    """Custom argperser that add --ssl option."""
    base_argparser(parser)

    parser.add_argument(
        "--ssl",
        action="store_true",
        help="enable ssl connection for clickhouse keepers and clickhouse",
        default=False,
    )

    parser.add_argument(
        "--clickhouse-package-list",
        action="extend",
        dest="clickhouse_package_list",
        help="path to ClickHouse package or binary, default: /usr/bin/clickhouse",
        metavar="path",
        default=[],
    )

    parser.add_argument(
        "--repeats",
        type=int,
        dest="repeats",
        help="number of insert test repeats for `mean` value calculation",
        default=4,
    )

    parser.add_argument(
        "--inserts",
        type=int,
        dest="inserts",
        help="number of inserts into table on one repeat",
        default=200,
    )

    parser.add_argument(
        "--results-file-name",
        type=str,
        dest="results_file_name",
        help="number of inserts into table on one repeat",
        default=f"performance_{getuid()}",
    )

    parser.add_argument(
        "--one-node",
        action="store_true",
        help="enable only one node coordination cluster testing",
        default=False,
    )

    parser.add_argument(
        "--three-node",
        action="store_true",
        help="enable only three nodes coordination cluster testing",
        default=False,
    )
