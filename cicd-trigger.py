#!/usr/bin/env python3
"""Manual GitLab CI/CD pipeline trigger script.
"""
import os
import sys
import time
import gitlab
import datetime
import contextlib
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter

PROJECT_ID = 39540585
PROGRESS = "\u2591"


def timestamp():
    """Return timestamp string."""
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.astimezone().strftime("%b %d,%Y %H:%M:%S.%f %Z")


class Action:
    """Simple action wrapper."""

    debug = False

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"{timestamp()} \u270D  {self.name}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value is not None:
            print(f"{timestamp()} \u274C Error", BaseException)
            if self.debug:
                raise
            sys.exit(1)
        else:
            print(f"{timestamp()} \u2705 OK")


def get_or_create_pipeline_trigger(username, project, description=None):
    """Create pipeline trigger."""
    description = f"cicd-trigger-{username}"

    for trigger in project.triggers.list():
        if trigger.description == description:
            return trigger

    return project.triggers.create({"description": description})


description = """Script to launch CI/CD pipeline.
    
    Either pass GitLab user token using the '--token' option (make sure it has the 'api' scope)
    or even better set $GITLAB_TOKEN environment variable that will be used by default.
    
    Examples:
    
    Run all available suites on master branch with a specified token:
        python3 cicd_trigger.py --branch master --token $GITLAB_TOKEN

     Run all available suites wait for the run to complete:
        python3 cicd_trigger.py --wait

    Run all available suites and upload artifacts to public aws s3 bucket:
        python3 cicd_trigger.py --artifacts public

    Run all available suites on a specific build:
        python3 cicd_trigger.py --package https://s3.amazonaws.com/altinity-build-artifacts/217/c14c89992f760772f487f91fdb8bb71367b51e81/package_release/clickhouse-common-static_22.8.11.17.altinityfips_amd64.deb --version 22.8.11.17.altinityfips

    Run aes_encryption suite:
        python3 cicd_trigger.py --suite aes_encryption

    Run aggregate_function suite:
        python3 cicd_trigger.py --suite aggregate_function

    Run atomic_insert suite:
        python3 cicd_trigger.py --suite atomic_insert

    Run base_58 suite:
        python3 cicd_trigger.py --suite base_58

    Run clickhouse_keeper suite:
        python3 cicd_trigger.py --suite clickhouse_keeper

    Run datetime64_extended_range suite:
        python3 cicd_trigger.py --suite datetime64_extended_range

    Run disk_level_encryption suite:
        python3 cicd_trigger.py --suite disk_level_encryption

    Run dns suite:
        python3 cicd_trigger.py --suite dns

    Run example suite:
        python3 cicd_trigger.py --suite example

    Run extended_precision_data_types suite:
        python3 cicd_trigger.py --suite extended_precision_data_types

    Run extended_precision_data_types suite:
        python3 cicd_trigger.py --suite functional

    Run kafka suite:
        python3 cicd_trigger.py --suite kafka

    Run kerberos suite:
        python3 cicd_trigger.py --suite kerberos

    Run ldap suite:
        python3 cicd_trigger.py --suite ldap

    Run lightweight_delete suite:
        python3 cicd_trigger.py --suite lightweight_delete

    Run map_type suite:
        python3 cicd_trigger.py --suite map_type

    Run parquet suite:
        python3 cicd_trigger.py --suite parquet

    Run part_moves_between_shards suite:
        python3 cicd_trigger.py --suite part_moves_between_shards

    Run rbac suite:
        python3 cicd_trigger.py --suite rbac

    Run s3 suite:
        python3 cicd_trigger.py --suite s3

    Run s3_aws suite:
        python3 cicd_trigger.py --suite s3_aws

    Run s3_gcs suite:
        python3 cicd_trigger.py --suite s3_gcs

    Run selects suite:
        python3 cicd_trigger.py --suite selects

    Run ssl_server suite:
        python3 cicd_trigger.py --suite ssl_server

    Run tiered_storage suite:
        python3 cicd_trigger.py --suite tiered_storage

    Run tiered_storage_aws suite:
        python3 cicd_trigger.py --suite tiered_storage_aws

    Run tiered_storage_gcs suite:
        python3 cicd_trigger.py --suite tiered_storage_gcs

    Run window_functions suite:
        python3 cicd_trigger.py --suite window_functions

    Run benchmark suite:
        python3 cicd_trigger.py --suite benchmark
    """


def argparser(parser):
    """Argument parser for running the pipelines."""
    suites = [
        "all",
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
        "functional",
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
    outputs = ["classic", "nice"]
    arches = ["amd64", "arm64"]
    package_post_fix_choices = ["all", "amd64"]
    parallel_choices = ["on", "off"]
    artifact_locations = ["internal", "public"]
    default_package = "docker://clickhouse/clickhouse-server"
    default_version = "22.3.9.19-alpine"
    default_package_post_fix = "amd64"
    default_suite = "all"
    default_output = "classic"
    default_parallel = "on"
    default_artifact_location = "internal"
    default_arch = "amd64"
    default_branch = "main"

    parser.add_argument(
        "--wait",
        action="store_true",
        default=False,
        help="wait for the pipeline to finish, default: False",
    )
    parser.add_argument(
        "--package",
        metavar="deb://<url>|docker://<image>|https://<url>",
        action="store",
        help=(
            "Either 'deb://', 'docker://', or 'https://' package specifier to use for tests, "
            f"default: {default_package}."
            "For example: "
            "'docker://altinity/clickhouse-server', 'docker://clickhouse/clickhouse-server', "
            "'deb://builds.altinity.cloud/apt-repo/pool/main', "
            "'deb://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release',"
            "'https://s3.amazonaws.com/altinity-build-artifacts/217/acf34c9fc6932aaf9af69425612070b50529f484/package_release/clickhouse-client_22.8.11.17.altinitystable_amd64.deb'"
        ),
        default=default_package,
    )
    parser.add_argument(
        "--version",
        metavar="value",
        action="store",
        help=(
            f"Version of clickhouse to use for tests, default: {default_version}. When package option "
            "uses docker:// specifier then the version is the image tag. For example: "
            "'22.3.9.19-alpine', '22.3.8.40.altinitystable', 'latest', etc."
        ),
        default=default_version,
    )
    parser.add_argument(
        "--package-postfix",
        metavar=f"{package_post_fix_choices}",
        action="store",
        help=(
            f"Postfix of the clickhouse-server and clickhouse-client deb package; choices: {package_post_fix_choices}, default: '{default_package_post_fix}'. "
            "Before 22.3 the server and client packages ended with '_all.deb' and starting with 22.3 they end with '_amd64.deb'."
        ),
        default=default_package_post_fix,
    )
    parser.add_argument(
        "-s",
        "--suite",
        metavar="name",
        type=str,
        action="store",
        default=default_suite,
        choices=suites,
        help=f"choose specific suite you want to run, choices: {suites}, default: '{default_suite}'",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="type",
        action="store",
        type=str,
        default=default_output,
        choices=outputs,
        help=f"choose test program's output format, choices: {outputs}, default: '{default_output}'",
    )
    parser.add_argument(
        "--parallel",
        action="store",
        help=f"Enable or disable running tests in parallel, choices: {parallel_choices}, default: '{default_parallel}'.",
        default=default_parallel,
        choices=parallel_choices,
    )
    parser.add_argument(
        "--token",
        metavar="value",
        type=str,
        help="GitLab personal access token or private token with api access to the project, default: $GITLAB_TOKEN env variable.",
        default=os.getenv("GITLAB_TOKEN"),
    )
    parser.add_argument(
        "--options",
        metavar="value",
        action="store",
        help="Extra options that will be added to test run command, default: ''.",
        default="",
    )
    parser.add_argument(
        "--arch",
        metavar=f"{arches}",
        action="store",
        help=f"Architecture to run the tests on, choices: '{arches}', default: '{default_arch}'.",
        default=default_arch,
        choices=arches,
    )
    parser.add_argument(
        "--branch",
        action="store",
        help=f"Choose which branch to run the tests on, default: '{default_branch}'",
        default=default_branch,
    )
    parser.add_argument(
        "--artifacts",
        action="store",
        help=f"Specify whether to upload to internal or public s3 bucket, choices: '{artifact_locations}', default: '{default_artifact_location}'. \
            'altinity-internal-test-reports' for internal upload, 'altinity-test-reports' for public",
        default=default_artifact_location,
        choices=artifact_locations,
    )
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Enable script debug mode, default: False",
    )
    parser.add_argument(
        "--from-github",
        default=False,
        action="store_true",
        help="Indicate whether the call was initialized from github workflows, default: False",
    )
    parser.add_argument(
        "--commit-sha",
        default=None,
        action="store",
        help="Provide latest commit sha, default: None",
    )

    return parser


def trigger():
    """CI/CD trigger."""
    args = argparser(
        ArgumentParser(
            "cicd-trigger.py",
            description=description,
            formatter_class=RawTextHelpFormatter,
        )
    ).parse_args()

    if args.debug:
        Action.debug = True

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
            assert (
                args.package.startswith("deb://")
                or args.package.startswith("docker://")
                or args.package.startswith("https://")
            ), "package name should start with deb://, docker:// or https://"
            variables["package"] = args.package
        if args.version:
            variables["version"] = args.version
        if args.package_postfix:
            variables["package_postfix"] = args.package_postfix
        if args.suite:
            variables["suite"] = args.suite
        if args.output:
            variables["output"] = args.output
        if args.parallel:
            variables["parallel"] = args.parallel
        if args.options:
            variables["options"] = args.options
        if args.arch:
            variables["arch"] = args.arch
        if args.artifacts:
            variables["artifacts"] = args.artifacts
            if args.artifacts == "internal":
                log_path = "altinity-internal-test-reports"
            elif args.artifacts == "public":
                log_path = "altinity-test-reports"
        if args.from_github:
            variables["from_github"] = str(args.from_github)
        if args.commit_sha:
            variables["commit_sha"] = args.commit_sha

        pipeline = project.trigger_pipeline(
            args.branch, trigger.token, variables=variables
        )

        print(
            f"   Pipeline {pipeline.id} started by {pipeline.user['username']}, status: {pipeline.status} at\n"
            f"   \u2728 https://gitlab.com/altinity-qa/clickhouse/cicd/clickhouse-regression/-/pipelines/{pipeline.id} \u2728"
        )
        print("\n".join(f"   {k}: {v}" for k, v in variables.items()))
        print(
            f"   Job logs will be located in https://{log_path}.s3.amazonaws.com/index.html#clickhouse/{variables['version']}/{pipeline.id}/testflows/ after the run is complete"
        )

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
