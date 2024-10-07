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
        metavar="VERSION",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_VERSION", None),
    )

    parser.add_argument(
        "--clickhouse-binary-path",
        "--clickhouse",
        type=str,
        dest="clickhouse_path",
        help="path to ClickHouse package or binary, default: /usr/bin/clickhouse",
        metavar="PATH",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH", "/usr/bin/clickhouse"),
    )

    parser.add_argument(
        "--base-os",
        type=str,
        dest="base_os",
        help="base OS image for ClickHouse server and keeper",
        default=None,
    )

    parser.add_argument(
        "--keeper-binary-path",
        "--keeper",
        type=str,
        dest="keeper_path",
        help="path to ClickHouse Keeper package or binary",
        metavar="PATH",
        default=None,
    )

    parser.add_argument(
        "--zookeeper-version",
        type=str,
        dest="zookeeper_version",
        help="Zookeeper version",
        metavar="VERSION",
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
        "--collect-service-logs",
        action="store_true",
        default=False,
        help="enable docker log collection. for ci/cd use, does not work locally.",
    )

    parser.add_argument(
        "--thread-fuzzer",
        action="store_true",
        help="enable thread fuzzer",
        default=False,
    )

    parser.add_argument(
        "--with-analyzer",
        action="store_true",
        default=False,
        help="Use experimental analyzer.",
    )

    parser.add_argument(
        "--reuse-env",
        action="store_true",
        default=False,
        help="Do not tear down the environment after the test.",
    )


def CaptureClusterArgs(func):
    """
    Collect cluster arguments from argparser into cluster_args.

    Usage:

        @TestModule
        @ArgumentParser(argparser)
        @...  # other decorators
        @CaptureClusterArgs
        def regression(
            self,
            cluster_args,
            clickhouse_version,
            stress=None,
            with_analyzer=False,
        ):
            nodes = ...

            with Given("docker-compose cluster"):
                cluster = create_cluster(
                    **cluster_args,
                    nodes=nodes,
                    configs_dir=current_dir(),
                    docker_compose_project_dir=os.path.join(
                        current_dir(), os.path.basename(current_dir()) + "_env"
                    ),
                )

            ...

    """

    def capture_cluster_args(
        self,
        local,
        clickhouse_path,
        base_os,
        keeper_path,
        zookeeper_version,
        use_keeper,
        collect_service_logs,
        thread_fuzzer,
        reuse_env,
        **kwargs
    ):
        cluster_args = {
            "local": local,
            "clickhouse_path": clickhouse_path,
            "base_os": base_os,
            "keeper_path": keeper_path,
            "zookeeper_version": zookeeper_version,
            "use_keeper": use_keeper,
            "collect_service_logs": collect_service_logs,
            "thread_fuzzer": thread_fuzzer,
            "reuse_env": reuse_env,
        }
        return func(self, cluster_args=cluster_args, **kwargs)

    return capture_cluster_args
