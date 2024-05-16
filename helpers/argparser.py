import os


def argparser(parser):
    """Default argument parser for regressions."""
    parser.add_argument(
        "--local",
        action="store_true",
        help="run regression in local mode",
        default=True,
    )

    parser.add_argument(
        "--clickhouse-version",
        type=str,
        dest="clickhouse_version",
        help="clickhouse server version",
        metavar="version",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_VERSION", None),
    )

    parser.add_argument(
        "--clickhouse-binary-path",
        type=str,
        dest="clickhouse_binary_path",
        help="path to ClickHouse binary, default: /usr/bin/clickhouse",
        metavar="path",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH", "/usr/bin/clickhouse"),
    )

    parser.add_argument(
        "--keeper-binary-path",
        type=str,
        dest="keeper_binary_path",
        help="path to ClickHouse Keeper binary",
        default=None,
    )

    parser.add_argument(
        "--zookeeper-version",
        type=str,
        dest="zookeeper_version",
        help="Zookeeper version",
        default=None,
    )
    parser.add_argument(
        "--use-keeper",
        action="store_true",
        default=False,
        dest="use_keeper",
        help="use ClickHouse Keeper instead of ZooKeeper",
    )

    parser.add_argument(
        "--stress",
        action="store_true",
        default=False,
        help="enable stress testing (might take a long time)",
    )

    parser.add_argument(
        "--allow-vfs",
        help="Instruct the tests to enable allow_vfs for all external disks",
        action="store_true",
    )

    parser.add_argument(
        "--collect-service-logs",
        action="store_true",
        default=False,
        help="enable docker log collection. for ci/cd use, does not work locally.",
    )

    parser.add_argument(
        "--with-analyzer",
        action="store_true",
        default=False,
        help="Use experimental analyzer.",
    )
