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
