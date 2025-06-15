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
    node = self.context.cluster.node("clickhouse1")
    query = "SELECT throwIf(1, 'throw')"
    result = node.command(f'clickhouse local --stacktrace -q "{query}"', exitcode=139)
    assert "FunctionThrowIf::executeImpl" in result.output, error(
        "Stacktrace is not enabled"
    )


@TestScenario
def version_format(self):
    node = self.context.cluster.node("clickhouse1")
    query = "SELECT version()"
    result = node.query(query).output
    assert VERSION_REGEX_QUERY.search(result), error(
        f"Version on query not formatted correctly, expected match for: '{VERSION_REGEX_QUERY.pattern}' but got: '{result}'"
    )

    result = node.command("clickhouse --version").output
    assert VERSION_REGEX_CLI.search(result), error(
        f"Version on cli not formatted correctly, expected match for: '{VERSION_REGEX_CLI.pattern}' but got: '{result}'"
    )


@TestScenario
def issues_link(self):
    node = self.context.cluster.node("clickhouse1")
    result = node.command(
        "grep --color=never -i -a clickhouse/issues /usr/bin/clickhouse"
    ).output

    # Want to match the link to the issues page, but not links to individual issues
    assert "github.com/ClickHouse/ClickHouse/issues" not in result.replace(
        "issues/", "_"
    ), error(
        f"ClickHouse/issues link is not correct, expected to not find upstream link but got: '{result}'"
    )
    assert "github.com/Altinity/ClickHouse/issues" in result, error(
        f"ClickHouse/issues link is not correct, expected to find Altinity link but got: '{result}'"
    )


@TestScenario
def error_message(self):
    node = self.context.cluster.node("clickhouse1")

    # Send error signal
    node.command("kill -SEGV $(pidof clickhouse)")

    def grep_in_log(message):
        return node.command(
            f"grep --color=never -i '{message}' /var/log/clickhouse-server/clickhouse-server.log",
            no_checks=True,
        ).output.splitlines()

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
        match = grep_in_log(message)
        assert not match, error(f"Unexpected message '{message}' found in log: {match}")

    expected_messages = [
        "(altinity build)",
    ]

    for message in expected_messages:
        match = grep_in_log(message)
        assert match, error(f"Expected message '{message}' not found in log")

    version_messages = grep_in_log("(version ")
    assert len(version_messages) > 0, error("No version messages found in log")

    for version_message in version_messages:
        assert VERSION_REGEX_CLI.search(version_message), error(
            f"Version is not formatted correctly, expected match for: '{VERSION_REGEX_CLI.pattern}' but got: {version_message}"
        )


@TestFeature
@Name("altinity version")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
