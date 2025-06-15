import re

from testflows.core import *
from testflows.asserts import error

# from version.requirements import *

VERSION_REGEX_QUERY = re.compile(r"(\d+\.\d+\.\d+.\d+.altinity[a-z]*)")
VERSION_REGEX_CLI = re.compile(
    r" (\d+\.\d+\.\d+.\d+.altinity[a-z]* \(altinity build\))"
)


@TestScenario
def stacktrace(self):
    """Check that stacktrace is enabled and symbols aren't stripped."""

    with Given("a ClickHouse instance"):
        node = self.context.cluster.node("clickhouse1")

    with When("running a query that throws an exception"):
        query = "SELECT throwIf(1, 'throw')"
        result = node.command(
            f'clickhouse local --stacktrace -q "{query}"', exitcode=139
        )

    with Then("the exception is not stripped"):
        assert "FunctionThrowIf::executeImpl" in result.output, error(
            "Stacktrace is not enabled"
        )


@TestScenario
def version_format(self):
    """Check that the version is formatted as expected."""

    with Given("a ClickHouse instance"):
        node = self.context.cluster.node("clickhouse1")

    with When("running a query to get the version"):
        query = "SELECT version()"
        result = node.query(query).output

    with Then("the version is formatted correctly"):
        assert VERSION_REGEX_QUERY.search(result), error(
            f"Version on query not formatted correctly, expected match for: '{VERSION_REGEX_QUERY.pattern}' but got: '{result}'"
        )

    with When("running the clickhouse command to get the version"):
        result = node.command("clickhouse --version").output

    with Then("the version is formatted correctly"):
        assert VERSION_REGEX_CLI.search(result), error(
            f"Version on cli not formatted correctly, expected match for: '{VERSION_REGEX_CLI.pattern}' but got: '{result}'"
        )


@TestScenario
def issue_link(self):
    """Check that the issue link is correct and not pointing to upstream."""

    with Given("a ClickHouse instance"):
        node = self.context.cluster.node("clickhouse1")

    with When("checking links to github that are embedded in the binary"):
        result = node.command(
            "grep --color=never -i -a clickhouse/issues /usr/bin/clickhouse"
        ).output

    with Then("the issue link is not pointing to upstream"):
        # Want to match the link to the issues page, but not links to individual issues
        assert "github.com/ClickHouse/ClickHouse/issues" not in result.replace(
            "issues/", "_"
        ), error()

    with Then("the issue link is pointing to Altinity's issues page"):
        assert "github.com/Altinity/ClickHouse/issues" in result, error()


@TestScenario
def error_message(self):
    """Check contents of log messages when an error occurs."""

    def grep_in_log(message):
        return node.command(
            f"grep --color=never -i '{message}' /var/log/clickhouse-server/clickhouse-server.log",
            no_checks=True,
        ).output.splitlines()

    with Given("a ClickHouse instance"):
        node = self.context.cluster.node("clickhouse1")

    signal = "SEGV"
    with When(f"the ClickHouse process is killed with a {signal} signal"):
        node.command(f"kill -{signal} $(pidof clickhouse)")

    with Then("the issues link is pointing to Altinity's issues page, if it's present"):
        if grep_in_log("ClickHouse/issues"):
            assert grep_in_log(
                "github.com/Altinity/ClickHouse/issues"
            ), "ClickHouse/issues link is not correct"

    unexpected_messages = [
        "github.com/ClickHouse/ClickHouse",
        "not official",
        "(official build)",
    ]
    for message in unexpected_messages:
        with Then(f"the log does not contain unexpected message '{message}'"):
            match = grep_in_log(message)
            assert not match, error()

    expected_messages = [
        "(altinity build)",
    ]
    for message in expected_messages:
        with Then(f"the log contains the expected message '{message}'"):
            match = grep_in_log(message)
            assert match, error()

    with Then("the log contains a version message"):
        version_messages = grep_in_log("(version ")
        assert len(version_messages) > 0, error("No version messages found in log")

    with Then("the version message is formatted correctly"):
        for version_message in version_messages:
            assert VERSION_REGEX_CLI.search(version_message), error()


@TestFeature
@Name("altinity")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
