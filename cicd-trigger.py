#!/usr/bin/env python3
"""Manual GitLab CI/CD pipeline trigger script.
"""
import os
import sys
import time
import uuid
import gitlab
import datetime
import contextlib

from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter

PROJECT_ID = 39540585
DEBUG = False  # set True to debug this trigger program
PROGRESS = "\u2591"

suites = [
    "aes_encryption",
    "aggregate_functions",
    "atomic_insert",
    "base_58",
    "clickhouse_keeper",
    "datetime64_extended_range",
    "disk_level_encryption",
    "dns",
    "example",
    "extended_precision_data_types",
    "kafka",
    "kerberos",
    "ldap",
    "lightweight_delete",
    "map_type",
    "parquet",
    "part_moves_between_shards",
    "rbac",
    "s3",
    "s3_aws",
    "s3_gcs",
    "selects",
    "ssl_server",
    "tiered_storage",
    "tiered_storage_aws",
    "tiered_storage_gcs",
    "window_functions",
    "benchmark",
]


def timestamp():
    """Return timestamp string."""
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.astimezone().strftime("%b %d,%Y %H:%M:%S.%f %Z")


@contextlib.contextmanager
def Action(name):
    """Simple action wrapper."""
    try:
        print(f"{timestamp()} \u270D  {name}")
        yield
    except BaseException as e:
        print(f"{timestamp()} \u274C Error", e)
        if DEBUG:
            raise
        sys.exit(1)
    else:
        print(f"{timestamp()} \u2705 OK")


def token_type(v):
    if not v:
        v = default = os.getenv("GITLAB_TOKEN", None)
    if v is None:
        raise ArgumentTypeError("must be set")
    return v


def argparser(parser):
    """Argument parser."""

    parser.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Wait for pipeline to finish, default: False",
        default=False,
    )
    parser.add_argument(
        "--package",
        metavar="deb://<url>|docker://<image>|https://<url>",
        action="store",
        help=(
            "Either 'deb://', 'docker://', or 'https://' package specifier to use for tests, "
            "default: docker://clickhouse/clickhouse-server. The url for deb package specifier"
            "should not contain 'https://' prefix. "
            "For example: "
            "'docker://altinity/clickhouse-server', 'docker://clickhouse/clickhouse-server', "
            "'deb://builds.altinity.cloud/apt-repo/pool/main', "
            "'deb://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release'"
        ),
        default="docker://clickhouse/clickhouse-server",
    )

    parser.add_argument(
        "--version",
        metavar="value",
        action="store",
        help=(
            "Version of clickhouse to use for tests, default: 22.3.8.39-alpine. When package option "
            "uses docker:// specifier then the version is the image tag. For example: "
            "'22.3.9.19-alpine', '22.3.8.40.altinitystable', etc."
        ),
        default="22.3.9.19-alpine",
    )

    parser.add_argument(
        "--package-postfix",
        metavar="{all,amd64}",
        action="store",
        help=(
            "Postfix of the clickhouse-server and clickhouse-client deb package; either 'all' or 'amd64', default: 'amd64'. "
            "Before 22.3 the server and client packages ended with '_all.deb' and starting with 22.3 they end with '_amd64.deb'."
        ),
        default="amd64",
    )

    parser.add_argument(
        "--only",
        action="store",
        metavar="suite",
        help=f"Select test suite to run; only one suite can be selected. Choices {str(suites)[1:-1]}",
        choices=suites,
        default=None,
    )

    parser.add_argument(
        "--output",
        metavar="format",
        action="store",
        help="Tests stdout output style, default: 'classic'. Choices 'nice', 'classic', 'short', etc.",
        default="classic",
    )

    parser.add_argument(
        "--parallel",
        action="store",
        help="Enable or disable running tests in parallel.",
        default="on",
        choices=["on", "off"],
    )

    parser.add_argument(
        "--token",
        metavar="value",
        help="Personal access token or private token with api access to the gitlab project, default: 'GITLAB_TOKEN' environment variable.",
        type=token_type,
        default="",
    )

    parser.add_argument(
        "--options",
        metavar="value",
        action="store",
        help="Extra options that will be added to test run command.",
        default="",
    )

    parser.add_argument(
        "--arch",
        metavar="{arm64,amd64}",
        action="store",
        help="Architecture to run the tests on, default: 'amd64'.",
        default="amd64",
        choices=["amd64", "arm64"],
    )

    parser.add_argument(
        "--branch",
        action="store",
        help="Choose which branch to run the tests on",
        default="main",
    )

    return parser


def get_or_create_pipeline_trigger(username, project, description=None):
    """Create pipeline trigger."""
    description = f"cicd-trigger-{username}"

    for trigger in project.triggers.list():
        if trigger.description == description:
            return trigger

    return project.triggers.create({"description": description})


def trigger():
    """CI/CD trigger."""
    args = argparser(
        ArgumentParser(
            "cicd-trigger.py",
            description="""Script to launch the CI/CD pipeline.

        Either pass GitLab user token using the '--token' option (make sure it has 'api' scope)
        or even better set GITLAB_TOKEN environemnt variable that will be used by default.

        Examples:
        
        Running docker image clickhouse/clickhouse-server:22.3.7.28-alpine:
            $ ./cicd-trigger.py --package docker://clickhouse/clickhouse-server --version 22.3.7.28-alpine

        Running deb package from Altinity repo:
            $ ./cicd-trigger.py --package deb://builds.altinity.cloud/apt-repo/pool/main --version 21.8.8.1.altinitystable --package-postfix all`
        
        Running deb package from ClickHouse repo, example link 
        https://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release/clickhouse-client_22.7.1.1738_amd64.deb:
            $ ./cicd-trigger.py --package deb://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release --version 22.7.1.1738 --package-postfix amd64`
        """,
            formatter_class=RawTextHelpFormatter,
        )
    ).parse_args()

    with Action("Authenticate using token with https://gitlab.com"):
        gl = gitlab.Gitlab("https://gitlab.com/", private_token=args.token)
        gl.auth()
        print(f"   authenticated as {gl.user.username}")

    with Action(f"Get project {PROJECT_ID}"):
        project = gl.projects.get(PROJECT_ID)

    with Action(f"Get or create user pipeline trigger"):
        trigger = get_or_create_pipeline_trigger(gl.user.username, project=project)

    with Action("Trigger pipeline"):
        variables = {}
        if args.package:
            assert args.package.startswith("deb://") or args.package.startswith(
                "docker://"
            ), "package name should start with deb:// or docker://"
            variables["package"] = args.package
        if args.version:
            variables["version"] = args.version
        if args.package_postfix:
            variables["package_postfix"] = args.package_postfix
        if args.only:
            variables["only"] = args.only
        if args.output:
            variables["output"] = args.output
        if args.parallel:
            variables["parallel"] = args.parallel
        if args.options:
            variables["options"] = args.options
        if args.arch:
            variables["arch"] = args.arch

        pipeline = project.trigger_pipeline(
            args.branch, trigger.token, variables=variables
        )

        print(
            f"   Pipeline {pipeline.id} started by {pipeline.user['username']}, status: {pipeline.status} at\n"
            f"   \u2728https://gitlab.com/altinity-qa/clickhouse/cicd/clickhouse-regression/-/pipelines/{pipeline.id}\u2728"
        )
        print("\n".join(f"   {k}: {v}" for k, v in variables.items()))

    if args.wait:
        with Action("Wait for pipeline to finish"):
            i = 1
            sys.stdout.write(f"{timestamp()}    {PROGRESS}")
            sys.stdout.flush()
            try:
                while pipeline.finished_at is None:
                    pipeline.refresh()
                    if i > 1 and i % 40 == 0:
                        sys.stdout.write(f"\n{timestamp()}    ")
                    sys.stdout.write(PROGRESS)
                    sys.stdout.flush()
                    time.sleep(1)
                    i += 1
            finally:
                sys.stdout.write("\n")

            assert pipeline.status == "success", "not successful"


if __name__ == "__main__":
    trigger()
