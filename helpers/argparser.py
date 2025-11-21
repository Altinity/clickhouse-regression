import os

from testflows.core import Secret


def argparser(parser):
    """Default argument parser for regression."""
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
        "--clickhouse",
        "--clickhouse-package-path",
        "--clickhouse-binary-path",
        type=str,
        dest="clickhouse_path",
        help="Path to ClickHouse package or binary, default: /usr/bin/clickhouse",
        metavar="PATH",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH", "/usr/bin/clickhouse"),
    )

    parser.add_argument(
        "--as-binary",
        action="store_true",
        help="Enable old behavior of copying binaries out of packages, instead of installing them",
    )

    parser.add_argument(
        "--base-os",
        type=str,
        dest="base_os",
        help="base OS image for ClickHouse server and keeper",
        default=None,
    )

    parser.add_argument(
        "--keeper",
        "--keeper-package-path",
        "--keeper-binary-path",
        type=str,
        dest="keeper_path",
        help="Path to ClickHouse Keeper package or binary",
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

    parser.add_argument(
        "--cicd",
        action="store_true",
        default=False,
        help="Run tests in CI/CD mode.",
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
        as_binary,
        base_os,
        keeper_path,
        zookeeper_version,
        use_keeper,
        collect_service_logs,
        thread_fuzzer,
        reuse_env,
        cicd,
        **kwargs
    ):
        cluster_args = {
            "local": local,
            "clickhouse_path": clickhouse_path,
            "as_binary": as_binary,
            "base_os": base_os,
            "keeper_path": keeper_path,
            "zookeeper_version": zookeeper_version,
            "use_keeper": use_keeper,
            "collect_service_logs": collect_service_logs,
            "thread_fuzzer": thread_fuzzer,
            "reuse_env": reuse_env,
            "cicd": cicd,
        }
        return func(self, cluster_args=cluster_args, **kwargs)

    return capture_cluster_args


def argparser_s3(parser):
    """Extended argument parser for suites with S3 storage."""
    argparser(parser)

    parser.add_argument(
        "--storage",
        action="append",
        help="select which storage types to run tests with",
        choices=["minio", "aws_s3", "gcs", "local", "azure"],
        default=None,
        dest="storages",
    )

    parser.add_argument(
        "--minio-uri",
        action="store",
        help="set url for the minio connection",
        type=Secret(name="minio_uri"),
        default="http://minio1:9001",
    )

    parser.add_argument(
        "--minio-root-user",
        action="store",
        help="minio root user name (access key id)",
        type=Secret(name="minio_root_user"),
        default="minio_user",
    )

    parser.add_argument(
        "--minio-root-password",
        action="store",
        help="minio root user password (secret access key)",
        type=Secret(name="minio_root_password"),
        default="minio123",
    )

    parser.add_argument(
        "--aws-s3-bucket",
        action="store",
        help="set bucket for the aws connection",
        type=Secret(name="aws_s3_bucket"),
        default=os.getenv("S3_AMAZON_BUCKET"),
    )

    parser.add_argument(
        "--aws-s3-region",
        action="store",
        help="set aws region for the aws connection",
        type=Secret(name="aws_s3_region"),
        default=os.getenv("AWS_DEFAULT_REGION"),
    )

    parser.add_argument(
        "--aws-s3-key-id",
        action="store",
        help="aws s3 key id",
        type=Secret(name="aws_s3_key_id"),
        default=os.getenv("AWS_ACCESS_KEY_ID"),
    )

    parser.add_argument(
        "--aws-s3-access-key",
        action="store",
        help="aws s3 access key",
        type=Secret(name="aws_s3_access_key"),
        default=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    parser.add_argument(
        "--gcs-uri",
        action="store",
        help="set url for the gcs connection",
        type=Secret(name="gcs_uri"),
        default=os.getenv("GCS_URI"),
    )

    parser.add_argument(
        "--gcs-key-id",
        action="store",
        help="gcs key id",
        type=Secret(name="gcs_key_id"),
        default=os.getenv("GCS_KEY_ID"),
    )

    parser.add_argument(
        "--gcs-key-secret",
        action="store",
        help="gcs key secret",
        type=Secret(name="gcs_key_secret"),
        default=os.getenv("GCS_KEY_SECRET"),
    )
    parser.add_argument(
        "--azure-account-name",
        action="store",
        help="azure account name",
        type=Secret(name="azure_account_name"),
        default=os.getenv("AZURE_ACCOUNT_NAME"),
    )
    parser.add_argument(
        "--azure-storage-key",
        action="store",
        help="azure storage key",
        type=Secret(name="azure_storage_key"),
        default=os.getenv("AZURE_STORAGE_KEY"),
    )
    parser.add_argument(
        "--azure-container",
        action="store",
        help="azure container",
        type=Secret(name="azure_container"),
        default=os.getenv("AZURE_CONTAINER_NAME"),
    )


def CaptureS3Args(func):
    """
    Collect S3 arguments from argparser into s3_args.

    Usage:

        @TestModule
        @ArgumentParser(argparser_s3)
        @...  # other decorators
        @CaptureClusterArgs
        @CaptureS3Args
        def regression(
            self,
            cluster_args,
            s3_args,
            clickhouse_version,
            stress=None,
            with_analyzer=False,
        ):
            ...

    """

    def capture_s3_args(
        self,
        storages,
        minio_uri,
        minio_root_user,
        minio_root_password,
        aws_s3_bucket,
        aws_s3_region,
        aws_s3_key_id,
        aws_s3_access_key,
        gcs_uri,
        gcs_key_id,
        gcs_key_secret,
        azure_account_name,
        azure_storage_key,
        azure_container,
        **kwargs
    ):
        s3_args = {
            "storages": storages,
            "minio_uri": minio_uri,
            "minio_root_user": minio_root_user,
            "minio_root_password": minio_root_password,
            "aws_s3_bucket": aws_s3_bucket,
            "aws_s3_region": aws_s3_region,
            "aws_s3_key_id": aws_s3_key_id,
            "aws_s3_access_key": aws_s3_access_key,
            "gcs_uri": gcs_uri,
            "gcs_key_id": gcs_key_id,
            "gcs_key_secret": gcs_key_secret,
            "azure_account_name": azure_account_name,
            "azure_storage_key": azure_storage_key,
            "azure_container": azure_container,
        }
        return func(self, s3_args=s3_args, **kwargs)

    return capture_s3_args


def argparser_minio(parser):
    """Extended argument parser for suites with only minio."""
    argparser(parser)

    parser.add_argument(
        "--minio-uri",
        action="store",
        help="set url for the minio connection",
        type=Secret(name="minio_uri"),
        default="http://minio:9001",
    )

    parser.add_argument(
        "--minio-root-user",
        action="store",
        help="minio root user name (access key id)",
        type=Secret(name="minio_root_user"),
        default="admin",
    )

    parser.add_argument(
        "--minio-root-password",
        action="store",
        help="minio root user password (secret access key)",
        type=Secret(name="minio_root_password"),
        default="password",
    )


def argparser_minio_hive(parser):
    """Extended argument parser for suites with only minio."""
    argparser(parser)

    parser.add_argument(
        "--minio-uri",
        action="store",
        help="set url for the minio connection",
        type=Secret(name="minio_uri"),
        default="http://minio1:9001",
    )

    parser.add_argument(
        "--minio-root-user",
        action="store",
        help="minio root user name (access key id)",
        type=Secret(name="minio_root_user"),
        default="admin",
    )

    parser.add_argument(
        "--minio-root-password",
        action="store",
        help="minio root user password (secret access key)",
        type=Secret(name="minio_root_password"),
        default="password",
    )


def CaptureMinioArgs(func):
    """
    Collect Minio arguments from argparser into minio_args.

    Usage:

        @TestModule
        @ArgumentParser(argparser_minio)
        @...  # other decorators
        @CaptureClusterArgs
        @CaptureMinioArgs
        def regression(
            self,
            cluster_args,
            minio_args,
            clickhouse_version,
            stress=None,
            with_analyzer=False,
        ):
            ...

    """

    def capture_minio_args(
        self, minio_uri, minio_root_user, minio_root_password, **kwargs
    ):
        minio_args = {
            "minio_uri": minio_uri,
            "minio_root_user": minio_root_user,
            "minio_root_password": minio_root_password,
        }
        return func(self, minio_args=minio_args, **kwargs)

    return capture_minio_args
