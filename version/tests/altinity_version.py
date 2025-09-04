import re

from testflows.core import *
from testflows.asserts import error, values
from testflows.snapshots import snapshot

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
        result = node.command("clickhouse client --version").output

    with Then("the version is formatted correctly"):
        assert VERSION_REGEX_CLI.search(result), error(
            f"Version on cli not formatted correctly, expected match for: '{VERSION_REGEX_CLI.pattern}' but got: '{result}'"
        )


@TestScenario
def issue_link_in_binary(self):
    """Check that the issue link in the binary is correct and not pointing to upstream."""

    with Given("a ClickHouse instance"):
        node = self.context.cluster.node("clickhouse1")

    with When("checking links to github that are embedded in the binary"):
        result = node.command(
            "grep --color=never -i -a clickhouse/issues /usr/bin/clickhouse",
            no_checks=True,
        )

    with Then("grep should find links to clickhouse/issues"):
        assert result.output != "", error(
            "no links to 'clickhouse/issues' found in the binary."
        )
        assert result.exitcode == 0, error()

    with Then("the issue link is not pointing to upstream"):
        for line in result.output.splitlines():
            # Want to match the link to the issues page, but not links to individual issues
            individual_issue_link_mangled = line.replace("issues/", "_issues_/")
            assert (
                "github.com/ClickHouse/ClickHouse/issues"
                not in individual_issue_link_mangled
            ), error()

    with Then("the issue link is pointing to Altinity's issues page"):
        assert "github.com/Altinity/ClickHouse/issues" in result.output, error()


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

    try:
        signal = "SEGV"
        with When(f"the ClickHouse process is killed with a {signal} signal"):
            node.command(f"kill -{signal} $(pidof clickhouse)")

        with Then("the issues link is pointing to Altinity's issues page, if present"):
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
                assert not match, error(
                    f"unexpected message '{message}' found in log '{match}'"
                )

        expected_messages = [
            "(altinity build)",
        ]
        for message in expected_messages:
            with Then(f"the log contains the expected message '{message}'"):
                match = grep_in_log(message)
                assert match, error(f"expected message '{message}' not found in log")

        with Then("the log contains a version message"):
            version_messages = grep_in_log("(version ")
            assert len(version_messages) > 0, error("No version messages found in log")

        with Then("the version message is formatted correctly"):
            for version_message in version_messages:
                assert VERSION_REGEX_CLI.search(version_message), error()

    finally:
        with Finally("the ClickHouse process is restarted"):
            node.restart(safe=False)


@TestScenario
def embedded_logos(self):
    """Check that the embedded logos are correct."""

    with Given("a ClickHouse instance"):
        node = self.context.cluster.node("clickhouse1")

    with When("checking logos that are embedded in the binary"):
        altinity_logos = node.command(
            "grep --color=never -i -a 'data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwI' /usr/bin/clickhouse | uniq",
            no_checks=True,
        ).output

        clickhouse_logos = node.command(
            "grep --color=never -i -a 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1NCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDkgOCI+PHN0eWx' /usr/bin/clickhouse | uniq",
            no_checks=True,
        ).output

    with Then("Altinity logos should be present in the binary"):
        values_after_grep = (
            f"altinity: {altinity_logos.strip()} clickhouse: {clickhouse_logos.strip()}"
        )
        with values() as that:
            assert that(
                snapshot(
                    values_after_grep,
                    name="altinity_logos",
                    id="embedded_logos",
                    mode=snapshot.CHECK,
                )
            ), error()

        assert altinity_logos.strip() != "", error()
        assert clickhouse_logos.strip() == "", error()


@TestFeature
@Name("altinity")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
