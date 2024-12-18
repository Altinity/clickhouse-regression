#!/usr/bin/env python3

import json
import csv
from collections import namedtuple
import argparse
import os
from datetime import datetime
from pprint import pprint
import requests
from clickhouse_driver import Client

from testflows.core import *
from testflows._core.transform.log.pipeline import ResultsLogPipeline
from testflows._core.compress import CompressedFile
from testflows._core.cli.arg.handlers.report.results import Handler

"""
Map keys from DB schema to keys in test attributes or test result messages.
Format: {"source": {"db_column": "source_key"}}

Additional keys that are created while reading the log:
pr_info: pull_request_number, commit_url, base_ref, head_ref, base_repo, head_repo, pull_request_url
test_attributes: testflows_version, start_time, start_datetime, test_raw_attributes, flags
test_results: message_rtime_ms
"""


DATABASE_HOST_VAR = "CHECKS_DATABASE_HOST"
DATABASE_USER_VAR = "CHECKS_DATABASE_USER"
DATABASE_PASSWORD_VAR = "CHECKS_DATABASE_PASSWORD"
REPORT_URL_VAR = "SUITE_REPORT_INDEX_URL"

table_schema_attr_map = {
    "pr_info": {},  # {"pr_number": "pull_request_number"},
    "test_attributes": {
        "clickhouse_version": "version",
        "clickhouse_package": "package",
        "base_os": "base_os",
        "architecture": "arch",
        "keeper_package": "keeper_path",
        "zookeeper_version": "zookeeper_version",
        "use_keeper": "use_keeper",
        "thread_fuzzer": "thread_fuzzer",
        "with_analyzer": "with_analyzer",
        "stress": "stress",
        "commit_hash": "commit.hash",
        "job_url": "job.url",
        "report_url": "report.url",
        "start_time": "start_datetime",
        "scheduled": "job.is_scheduled",
    },
    "test_results": {
        "test_duration_ms": "message_rtime_ms",
        "result": "result_type",
        "test_name": "test_name",
        "result_reason": "result_reason",
        "result_message": "result_message",
    },
}

CREATE_TABLE_QUERY = """
CREATE TABLE clickhouse_regression_results ON CLUSTER '{cluster}'
(
    `clickhouse_version` LowCardinality(String),
    `clickhouse_package` LowCardinality(String),
    `base_os` LowCardinality(String),
    `architecture` LowCardinality(String),
    `keeper_package` LowCardinality(String),
    `zookeeper_version` LowCardinality(String),
    `use_keeper` Bool,
    `thread_fuzzer` Bool,
    `with_analyzer` Bool,
    `stress` Bool,
    `commit_hash` String,
    `job_url` LowCardinality(String),
    `report_url` String,
    `start_time` DateTime,
    `test_duration_ms` UInt64,
    `result` LowCardinality(String),
    `test_name` String,
    `result_reason` String,
    `result_message` String,
)
ENGINE = ReplicatedMergeTree('/clickhouse/{cluster}/tables/gh-data/clickhouse_regression_results', '{replica}')
ORDER BY start_time
SETTINGS index_granularity = 8192;
"""


bools = {
    "True": True,
    "False": False,
    "true": True,
    "false": False,
    True: True,
    False: False,
}


class ResultUploader:

    def __init__(self, log_path=None, debug=False) -> None:
        self.log_path = log_path
        self.test_attributes = {"test_raw_attributes": {}, "flags": {}}
        self.test_results = []
        self.run_start_time = None
        self.last_message_time = 0
        self.duration_ms = None
        self.pr_info = {}
        self.debug = debug

    def get_pr_info(self, project: str, sha: str) -> dict:
        if table_schema_attr_map["pr_info"] == {}:
            return {}

        pr_info = {
            "commit_url": f"https://github.com/{project}/commits/{sha}",
            "pull_request_number": None,
        }

        prs_for_sha = requests.get(
            f"https://api.github.com/repos/{project}/commits/{sha}/pulls"
        ).json()

        if prs_for_sha:
            pr_number = prs_for_sha[0]["number"]
            pr_info["pull_request_number"] = pr_number

        # If the schema only requires the pr number or commit url, return now
        if not (
            set(table_schema_attr_map["pr_info"].values())
            - set(("commit_url", "pull_request_number"))
        ):
            return pr_info

        pr_info["base_ref"] = "main"
        pr_info["head_ref"] = "main"
        pr_info["base_repo"] = project
        pr_info["head_repo"] = project

        if not prs_for_sha:
            return pr_info

        pr_info["pull_request_number"] = pr_number

        pr_info["pull_request_url"] = f"https://github.com/{project}/pull/{pr_number}"

        pull_request = requests.get(
            f"https://api.github.com/repos/{project}/pulls/{pr_number}"
        ).json()

        pr_info["base_ref"] = pull_request["base"]["ref"]
        pr_info["head_ref"] = pull_request["head"]["ref"]
        pr_info["base_repo"] = pull_request["base"]["repo"]["full_name"]
        pr_info["head_repo"] = pull_request["head"]["repo"]["full_name"]

        return pr_info

    def record_attribute_from_message(self, message: dict):
        """
        Record an attribute from a test log message.
        """
        assert message["message_keyword"] == "ATTRIBUTE"

        value = message["attribute_value"]
        if value is None:
            return
        if isinstance(value, str) and value.startswith("Secret"):
            return

        if value in bools.keys():
            value = bools[value]
            self.test_attributes["flags"][message["attribute_name"]] = value

        self.test_attributes[message["attribute_name"]] = value
        self.test_attributes["test_raw_attributes"][message["attribute_name"]] = value

    def read_json_report(self, report: dict = None):
        """
        Import the test results from tfs report results.
        """

        self.run_start_time = report["metadata"]["date"]
        self.test_attributes["start_time"] = int(self.run_start_time)
        self.test_attributes["start_datetime"] = datetime.fromtimestamp(
            self.run_start_time
        )
        self.duration_ms = report["metadata"]["duration"] * 1000
        self.test_attributes["testflows_version"] = report["metadata"]["version"]

        for message in report["attributes"]:
            self.record_attribute_from_message(message)

        assert report["tests"], "No tests found in the report"

        for message in report["tests"]:
            result = message["result"]
            result["message_rtime_ms"] = int(result["message_rtime"] * 1000)
            self.test_results.append(result)

        self.suite = self.test_results[0]["test_name"].split("/")[1].replace(" ", "_")
        self.status = self.test_results[0]["result_type"]

    def read_log_line(self, line: str):
        data = json.loads(line)
        self.last_message_time = data["message_time"]
        message_keyword = data["message_keyword"]

        if message_keyword == "RESULT":
            if (
                data["test_type"] != "Step"
                and data["test_subtype"] != "Example"
                and data["test_parent_type"] != "Test"
            ):
                data["message_rtime_ms"] = int(data["message_rtime"] * 1000)
                self.test_results.append(data)

        elif message_keyword == "ATTRIBUTE":
            self.record_attribute_from_message(data)

        elif message_keyword == "PROTOCOL":
            print(data["protocol_version"])
            self.test_attributes["testflows_protocol"] = data["protocol_version"]
            assert data["protocol_version"] == "TFSPv2.1", "Unexpected protocol version"
            self.run_start_time = data["message_time"]
            self.test_attributes["start_time"] = int(self.run_start_time)
            self.test_attributes["start_datetime"] = datetime.fromtimestamp(
                self.run_start_time
            )
            self.suite = data["test_name"].split("/")[1]

        elif message_keyword == "VERSION":
            print(data["framework_version"])
            self.test_attributes["testflows_version"] = data["framework_version"]

        elif self.debug and message_keyword not in [
            "TEST",
            "SPECIFICATION",
            "ARGUMENT",
            "NONE",
            "EXAMPLE",
            "REQUIREMENT",
            "METRIC",
            "TAG",
            "VALUE",
            "DEBUG",
            "EXCEPTION",  # is always step type
            "STOP",
        ]:
            pprint(data)
            raise ValueError(f"Unknown message keyword: {message_keyword}")

    def report_url(self) -> str:
        """
        This is a fallback if test_attributes report.url does not exist.
        """
        return os.getenv(REPORT_URL_VAR)

    def read_raw_log(self, log_lines=None):
        """
        Import the test results from raw log messages
        """
        for line in log_lines:
            self.read_log_line(line)

        # The test log could be truncated, so we can't rely on the message_rtime
        # of the most recent result message for the total duration
        self.duration_ms = (self.last_message_time - self.run_start_time) * 1000

        if self.test_results:
            # If the log is truncated, this is the status of the last test
            self.status = self.test_results[-1]["result_type"]
        else:
            self.status = "Unknown"

    def read_pr_info(self):

        pr_info = self.get_pr_info(
            self.test_attributes["project"], self.test_attributes["commit.hash"]
        )
        self.pr_info = pr_info

    def write_native_csv(self):
        """
        Export the test results with their original attributes names.
        For debugging purposes.
        """

        with open("results_native.csv", "w", newline="") as csv_file:
            fieldnames = list(self.test_results[0].keys())
            hide_fields = [
                "message_keyword",
                "message_hash",
                "message_object",
                "message_num",
                "message_stream",
                "message_level",
                "message_time",
                "test_id",
                "test_name",
                "test_level",
                "tickets",
                "values",
                "metrics",
            ]
            for field in hide_fields:
                try:
                    fieldnames.remove(field)
                except ValueError:
                    pass

            writer = csv.DictWriter(
                csv_file, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()
            for test_result in self.test_results:
                writer.writerow(test_result)

    def get_common_attributes(self):
        """
        Return a dictionary with the common schema values for all tests.
        """
        common_attributes = {}

        for key, value in table_schema_attr_map["pr_info"].items():
            common_attributes[key] = self.pr_info.get(value, None)

        for key, value in table_schema_attr_map["test_attributes"].items():
            common_attributes[key] = self.test_attributes.get(value, None)

        if common_attributes["report_url"] is None:
            url = self.report_url()
            if url is None:
                fail("No report URL found in test attributes or in environment")
            common_attributes["report_url"] = url

        for key in table_schema_attr_map["test_results"].keys():
            common_attributes[key] = None

        return common_attributes

    def iter_formatted_test_results(self, common_attributes):
        """
        Yield each test result in the table schema format.
        """
        for test_result in self.test_results:
            row = common_attributes.copy()
            for schema_attr, test_attr in table_schema_attr_map["test_results"].items():
                if test_attr in test_result:
                    row[schema_attr] = test_result[test_attr]
            yield row

    def write_csv(self):
        """
        Export the test logs in the table schema format.
        """

        # Collect values that are the same for all tests
        common_attributes = self.get_common_attributes()

        # Write results in table schema format}
        with open("results_table.csv", "w", newline="") as csv_file:
            fieldnames = common_attributes.keys()

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for test_result in self.iter_formatted_test_results(common_attributes):
                writer.writerow(test_result)

    def upload_results(
        self,
        db,
        table,
        db_host=None,
        db_user=None,
        db_password=None,
        db_port=None,
        secure=None,
        verify=None,
    ):

        with Given("database credentials"):
            if db_host is None:
                db_host = os.getenv(DATABASE_HOST_VAR)
                assert db_host, "Failed to get database host from environment"

            if db_user is None:
                db_user = os.getenv(DATABASE_USER_VAR)

            if db_password is None:
                db_password = os.getenv(DATABASE_PASSWORD_VAR, "")

        with And("common attributes for this test run"):
            common_attributes = self.get_common_attributes()

        with And("an iterator of all test results"):
            rows = self.iter_formatted_test_results(common_attributes)

        with And("a database client"):
            client = Client(
                db_host,
                user=db_user,
                password=db_password,
                port=db_port,
                secure="y" if secure else None,
                verify=verify,
                settings={"insert_block_size": 1024},
            )

        with When("inserting test results"):
            settings = {
                "send_logs_level": "info",
                "input_format_null_as_default": True,
            }

            r = client.execute(
                f"INSERT INTO `{db}`.{table} VALUES",
                rows,
                types_check=self.debug,
                settings=settings,
            )
            note(f"Inserted {r} records")

    def report_from_compressed_log(self, log_path=None):
        args = namedtuple(
            "args", ["title", "copyright", "confidential", "logo", "artifacts"]
        )(title=None, copyright=None, confidential=None, logo=None, artifacts=None)

        log_path = log_path or self.log_path
        results = {}
        ResultsLogPipeline(CompressedFile(log_path), results).run()

        report = Handler().data(results, args)

        return report

    def raw_log_from_compressed_log(self, log_path=None):
        log_path = log_path or self.log_path

        f = CompressedFile(log_path)
        for line in f:
            yield line

    def read_log(self, log_path=None):
        try:
            with When("converting log to report format"):
                report = self.report_from_compressed_log(log_path)
        except Exception as e:
            with When(
                "failed to read log in report format, extracting raw log",
                description=repr(e),
            ):
                log_raw_lines = self.raw_log_from_compressed_log(log_path=log_path)

            with And("reading raw log line by line"):
                self.read_raw_log(log_lines=log_raw_lines)

        else:
            with And("reading report"):
                self.read_json_report(report=report)

    def run_local(self, log_path=None):
        with By("reading log"):
            self.read_log(log_path=log_path)
            if not self.test_results:
                print("No results to upload")
                return

        with And("fetching PR info"):
            self.read_pr_info()

        if self.debug:
            with And("printing debug info"):
                pprint(self.pr_info, indent=2)
                pprint(self.test_attributes, indent=2)
                pprint(self.test_results[-1], indent=2)

            with And("writing native csv"):
                self.write_native_csv()

        with And("writing table csv"):
            self.write_csv()

    def run_upload(
        self,
        db,
        table,
        db_host=None,
        db_user=None,
        db_password=None,
        log_path=None,
        db_port=None,
        secure=None,
        verify=None,
    ):
        with By("reading log"):
            self.read_log(log_path=log_path)
            if not self.test_results:
                print("No results to upload")
                return

        with And("fetching PR info"):
            self.read_pr_info()

        if self.debug:
            with And("printing debug info"):
                pprint(self.pr_info, indent=2)
                pprint(self.test_attributes, indent=2)
                pprint(self.test_results[-1], indent=2)

        with And("uploading results"):
            self.upload_results(
                db=db,
                table=table,
                db_host=db_host,
                db_user=db_user,
                db_password=db_password,
                db_port=db_port,
                secure=secure,
                verify=verify,
            )


def argparser(parser: argparse.ArgumentParser):
    parser.add_argument("--log-file", help="Path to the log file")
    parser.add_argument(
        "--local", action="store_true", help="Save results to csv instead of uploading"
    )
    parser.add_argument("--db-name", help="Database name to upload results to")
    parser.add_argument("--table", help="Table name to upload to")
    parser.add_argument("--db-host", help="Hostname of the ClickHouse database")
    parser.add_argument("--db-user", help="Database user to use for the upload")
    parser.add_argument("--db-password", help="Database password to use for the upload")
    parser.add_argument("--db-port", help="Database port to use for the upload")
    parser.add_argument("--secure", action="store_true", help="Use secure connection")
    parser.add_argument("--no-verify", action="store_true", help="Do not verify SSL")
    parser.add_argument("--debug-dump", action="store_true", help="Extra debug output")
    parser.add_argument(
        "--show-create", action="store_true", help="Show create table query"
    )


@TestModule
@ArgumentParser(argparser)
def upload(
    self,
    log_file,
    debug_dump,
    local,
    db_name,
    table,
    db_host,
    db_user,
    db_password,
    db_port,
    secure,
    no_verify,
    show_create,
):
    if show_create:
        note(CREATE_TABLE_QUERY)
        return

    with Given("uploader instance"):
        R = ResultUploader(log_path=log_file, debug=debug_dump)

    if local:
        with When("saving results locally"):
            R.run_local()

    else:
        with When("uploading results to database"):
            R.run_upload(
                db=db_name,
                table=table,
                db_host=db_host,
                db_user=db_user,
                db_password=db_password,
                db_port=db_port,
                secure=secure,
                verify=not no_verify,
            )


if main():
    upload()
