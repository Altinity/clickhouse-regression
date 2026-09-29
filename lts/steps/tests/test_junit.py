"""Unit tests for lts.steps.junit parsing.

Run from the repository root:

    python3 -m unittest discover -s lts/steps/tests -t .
"""

import os
import tempfile
import unittest

from lts.steps.junit import _tree, parse_junit

PYTEST = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="5">
  <testcase classname="tests.columns.test_datetime.DateTimeTestCase" name="test_ok" time="0.1"/>
  <testcase classname="tests.columns.test_datetime.DateTimeTestCase" name="test_fail" time="0.2">
    <failure message="AssertionError: 1 != 2">trace</failure>
  </testcase>
  <testcase classname="tests.test_connect.ConnectTestCase" name="test_error">
    <error message="failed on setup">setup trace</error>
  </testcase>
  <testcase classname="tests.test_connect.ConnectTestCase" name="test_skip">
    <skipped message="No certificate found"/>
  </testcase>
  <testcase classname="tests.test_param" name="test_x[a/b]"/>
</testsuite></testsuites>
"""

# Surefire with a default namespace, rerun and flaky elements.
SUREFIRE = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite xmlns="http://maven.apache.org/surefire" name="TestSuite" tests="3">
  <testcase classname="com.clickhouse.jdbc.ClickHouseConnectionTest" name="testAutoCommit"/>
  <testcase classname="com.clickhouse.jdbc.ClickHouseConnectionTest" name="testRerun">
    <rerunFailure message="first attempt failed">trace</rerunFailure>
  </testcase>
  <testcase classname="com.clickhouse.jdbc.ClickHouseConnectionTest" name="testFlaky">
    <flakyFailure message="passed on rerun">trace</flakyFailure>
  </testcase>
</testsuite>
"""

CTEST = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Linux-c++" tests="2" failures="1">
  <testcase name="test.py-3-dsn-0" classname="test.py-3-dsn-0" time="0.05" status="run"/>
  <testcase name="parametrized-regression.py-3-dsn-0" classname="parametrized-regression.py-3-dsn-0" status="fail">
    <failure message="Failed"/>
  </testcase>
</testsuite>
"""

DUPLICATES = """<testsuite>
  <testcase classname="a.B" name="test_same"/>
  <testcase classname="a.B" name="test_same"><failure message="second"/></testcase>
</testsuite>
"""


class ParseJUnitTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def write(self, name, content):
        path = os.path.join(self.dir.name, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def outcomes(self, cases):
        return {case["name"]: case["outcome"] for case in cases}

    def test_pytest_outcomes(self):
        cases = parse_junit([self.write("pytest.xml", PYTEST)])
        self.assertEqual(
            self.outcomes(cases),
            {
                "test_ok": "passed",
                "test_fail": "failed",
                "test_error": "error",
                "test_skip": "skipped",
                "test_x[a_b]": "passed",
            },
        )
        failed = [case for case in cases if case["name"] == "test_fail"][0]
        self.assertEqual(failed["message"], "AssertionError: 1 != 2")
        self.assertEqual(failed["details"], "trace")
        self.assertEqual(
            failed["path"], ["tests", "columns", "test_datetime", "DateTimeTestCase"]
        )

    def test_namespaced_surefire(self):
        cases = parse_junit(
            [self.write("surefire.xml", SUREFIRE)], strip_prefix="com.clickhouse."
        )
        self.assertEqual(
            self.outcomes(cases),
            {"testAutoCommit": "passed", "testRerun": "failed", "testFlaky": "flaky"},
        )
        self.assertEqual(cases[0]["path"], ["jdbc", "ClickHouseConnectionTest"])

    def test_ctest(self):
        cases = parse_junit([self.write("ctest.xml", CTEST)])
        self.assertEqual(
            self.outcomes(cases),
            {
                "test.py-3-dsn-0": "passed",
                "parametrized-regression.py-3-dsn-0": "failed",
            },
        )
        # The class name repeats the test name, so there is no class path.
        self.assertEqual([case["path"] for case in cases], [[], []])

    def test_multiple_files(self):
        cases = parse_junit(
            [self.write("pytest.xml", PYTEST), self.write("ctest.xml", CTEST)]
        )
        self.assertEqual(len(cases), 7)

    def test_duplicate_names_are_kept(self):
        cases = parse_junit([self.write("dup.xml", DUPLICATES)])
        node = _tree(cases)["children"]["a"]["children"]["B"]
        self.assertEqual(
            [case["outcome"] for case in node["cases"]], ["passed", "failed"]
        )

    def test_malformed_xml(self):
        path = self.write("broken.xml", "<testsuite><testcase name='x'>")
        with self.assertRaisesRegex(ValueError, "is not valid JUnit XML"):
            parse_junit([path])


if __name__ == "__main__":
    unittest.main()
