#!/usr/bin/env python3

import json
import csv
from collections import namedtuple
import argparse
import os

import requests

from testflows._core.transform.log.pipeline import ResultsLogPipeline
from testflows._core.compress import CompressedFile
from testflows._core.cli.arg.handlers.report.results import Handler

"""
Map keys from DB schema to keys in test attributes or test result messages.
Format: {"source": {"db_column": "source_key"}}

Additional keys that are created while reading the log:
pr_info: pull_request_number, commit_url, base_ref, head_ref, base_repo, head_repo, pull_request_url
test_attributes: testflows_version, start_time
test_results: message_rtime_ms
"""

table_schema_attr_map = {
    "pr_info": {"pull_request_number": "pull_request_number"},
    "test_attributes": {
        "version": "version",
        "repository": "repository",
        "package": "package",
        "commit_hash": "commit.hash",
        "job_url": "job.url",
        "report_url": "report.url",
        "start_time": "start_time",
        "architecture": "arch",
    },
    "test_results": {
        "test_duration_ms": "message_rtime_ms",  # This value is generated in read_json_report/read_log_line
        "result_type": "result_type",
        "test_name": "test_name",
        "result_reason": "result_reason",
        "result_message": "result_message",
    },
}

ARTIFACT_BUCKET = "altinity-test-reports"
DATABASE_HOST_VAR = "CHECKS_DATABASE_HOST"
DATABASE_USER_VAR = "CHECKS_DATABASE_USER"
DATABASE_PASSWORD_VAR = "CHECKS_DATABASE_PASSWORD"


class ResultUploader:

    def __init__(self, log_path=None, debug=False) -> None:
        self.log_path = log_path
        self.test_attributes = {}
        self.test_results = []
        self.run_start_time = 0
        self.last_message_time = 0
        self.duration_ms = None
        self.pr_info = {}
        self.debug = debug

    def get_pr_info(self, project: str, sha: str) -> dict:
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

    def read_json_report(self, report: dict = None):
        """
        Import the test results from tfs report results.
        """

        self.run_start_time = report["metadata"]["date"]
        self.test_attributes["start_time"] = self.run_start_time
        self.duration_ms = report["metadata"]["duration"] * 1000
        self.test_attributes["testflows_version"] = report["metadata"]["version"]

        for message in report["attributes"]:
            self.test_attributes[message["attribute_name"]] = message["attribute_value"]

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
            self.test_attributes[data["attribute_name"]] = data["attribute_value"]

        elif message_keyword == "PROTOCOL":
            print(data["protocol_version"])
            self.test_attributes["testflows_protocol"] = data["protocol_version"]
            assert data["protocol_version"] == "TFSPv2.1", "Unexpected protocol version"
            self.run_start_time = data["message_time"]
            self.test_attributes["start_time"] = self.run_start_time
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
            print(data)
            raise ValueError(f"Unknown message keyword: {message_keyword}")

    def report_url(self) -> str:
        """
        Construct the URL to the test report in the S3 bucket.
        This is a fallback if test_attributes report.url does not exist.
        """
        storage = (
            "/" + json.loads(self.test_attributes["storages"].replace("'", '"'))[0]
            if self.test_attributes.get("storages")
            else ""
        )

        return (
            f"https://{ARTIFACT_BUCKET}.s3.amazonaws.com/index.html#"
            f"clickhouse/{self.test_attributes['clickhouse_version']}/{self.test_attributes['job.id']}/testflows/"
            f"{self.test_attributes['arch']}/{self.suite}{storage}/"
        )

    def read_raw_log(self, log_lines=None):
        """
        Import the test results from raw log messages
        """
        for line in log_lines:
            self.read_log_line(line)

        # The test log could be truncated, so we can't rely on the message_rtime
        # of the most recent result message for the total duration
        self.duration_ms = (self.last_message_time - self.run_start_time) * 1000
        # If the log is truncated, this is the status of the last test
        self.status = self.test_results[-1]["result_type"]

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
            common_attributes["report_url"] = self.report_url()

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
        db="gh-data",
        table="checks",
        db_url=None,
        db_user=None,
        db_password=None,
        timeout=100,
    ):
        if db_url is None:
            db_url = os.getenv(DATABASE_HOST_VAR)

        if db_user is not None:
            db_auth = {
                "X-ClickHouse-User": db_user,
                "X-ClickHouse-Key": db_password,
            }
        else:
            db_auth = {
                "X-ClickHouse-User": os.getenv(DATABASE_USER_VAR),
                "X-ClickHouse-Key": os.getenv(DATABASE_PASSWORD_VAR),
            }

        json_lines = [json.dumps(row) for row in self.iter_formatted_test_results()]
        json_str = ",".join(json_lines)

        params = {
            "database": db,
            "query": f"INSERT INTO {table} FORMAT JSONEachRow",
            "date_time_input_format": "best_effort",
            "send_logs_level": "warning",
        }

        response = requests.post(
            url=db_url, headers=db_auth, params=params, data=json_str, timeout=timeout
        )

        print(response.text)

        if not response.ok:
            raise ValueError(
                f"Cannot insert data into clickhouse: HTTP code {response.status_code}: {response.text}"
            )

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
            report = self.report_from_compressed_log(log_path)
        except Exception as e:
            print(f"Failed to read log in report format: {repr(e)}", "")
            print("Falling back to reading raw log")
            log_raw_lines = self.raw_log_from_compressed_log(log_path=log_path)
            self.read_raw_log(log_lines=log_raw_lines)
        else:
            self.read_json_report(report=report)

    def run_local(self, log_path=None):
        self.read_log(log_path=log_path)
        self.read_pr_info()
        self.write_csv()

        if self.debug:
            self.write_native_csv()

            print(json.dumps(self.pr_info, indent=2))
            print(json.dumps(self.test_attributes, indent=2))
            print(json.dumps(self.test_results[-1], indent=2))

    def run_upload(self, log_path=None):
        self.read_log(log_path=log_path)
        self.read_pr_info()
        self.upload_results()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-file", help="Path to the log file")
    parser.add_argument("--debug", action="store_true", help="Extra debug output")
    args = parser.parse_args()

    R = ResultUploader(debug=args.debug, log_path=args.log_file)

    R.run_local()
