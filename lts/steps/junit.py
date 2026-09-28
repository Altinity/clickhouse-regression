"""Report JUnit XML results (pytest, Maven surefire/failsafe) as TestFlows tests.

Every upstream testcase becomes one TestFlows scenario, so a failure points at a
named test and known failures are handled with ordinary ``xfails``.

The dotted class name is split into nested features, because TestFlows replaces
``.`` in a test name with a look-alike character that ``xfails`` patterns do
not match. ``tests.columns.test_datetime.DateTimeTestCase::test_x`` is reported
as ``.../tests/columns/test_datetime/DateTimeTestCase/test_x``.
"""

import glob
import xml.etree.ElementTree as ET

from testflows.core import *

FAILED = ("failure", "rerunFailure")
ERRORED = ("error", "rerunError")
FLAKY = ("flakyFailure", "flakyError")


def _safe(name):
    """Make an upstream name usable as a single TestFlows path segment."""
    return name.replace("/", "_").replace("\\", "_").strip() or "_"


def _local(tag):
    """Return an element tag without its XML namespace."""
    return tag.rsplit("}", 1)[-1]


def _child(element, tag):
    """Return the first child with local name ``tag``, ignoring namespaces."""
    for child in element:
        if _local(child.tag) == tag:
            return child
    return None


def _outcome(testcase):
    """Return ``(outcome, message, details)`` for a ``<testcase>`` element."""
    for tags, outcome in ((FAILED, "failed"), (ERRORED, "error")):
        for tag in tags:
            element = _child(testcase, tag)
            if element is not None:
                return outcome, element.get("message") or tag, element.text or ""
    skipped = _child(testcase, "skipped")
    if skipped is not None:
        return "skipped", skipped.get("message") or skipped.text or "skipped", ""
    for tag in FLAKY:
        element = _child(testcase, tag)
        if element is not None:
            return "flaky", element.get("message") or tag, element.text or ""
    return "passed", "", ""


def parse_junit(xml_paths, strip_prefix=""):
    """Return the testcases from JUnit XML files as a list of dicts."""
    cases = []
    for path in xml_paths:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as error:
            raise ValueError(f"{path} is not valid JUnit XML: {error}") from None
        for testcase in (e for e in root.iter() if _local(e.tag) == "testcase"):
            classname = testcase.get("classname") or "unknown"
            if strip_prefix and classname.startswith(strip_prefix):
                classname = classname[len(strip_prefix) :]
            outcome, message, details = _outcome(testcase)
            cases.append(
                {
                    "path": [_safe(part) for part in classname.split(".") if part],
                    "name": _safe(testcase.get("name") or "unnamed"),
                    "time": testcase.get("time"),
                    "outcome": outcome,
                    "message": message,
                    "details": details,
                }
            )
    return cases


@TestScenario
def testcase(self, case):
    """Replay the outcome of one upstream testcase."""
    if case["time"]:
        note(f"upstream duration: {case['time']}s")
    if case["details"]:
        note(case["details"][-8000:])
    if case["outcome"] == "failed":
        fail(case["message"][:2000])
    elif case["outcome"] == "error":
        err(case["message"][:2000])
    elif case["outcome"] == "skipped":
        skip(case["message"][:2000])
    elif case["outcome"] == "flaky":
        note(f"passed on rerun after: {case['message'][:2000]}")


def _tree(cases):
    """Group cases into a tree of nested dicts keyed by class-name parts."""
    root = {"children": {}, "cases": []}
    for case in cases:
        node = root
        for part in case["path"]:
            node = node["children"].setdefault(part, {"children": {}, "cases": []})
        node["cases"].append(case)
    return root


def _report(node):
    names = {}
    for case in node["cases"]:
        count = names[case["name"]] = names.get(case["name"], 0) + 1
        name = case["name"] if count == 1 else f"{case['name']} #{count}"
        Scenario(name=name, test=testcase, flags=TE)(case=case)
    for part, child in node["children"].items():
        with Feature(part, flags=TE):
            _report(child)


def report_junit_results(xml_glob, strip_prefix="", min_tests=1, max_skipped=None):
    """Report every testcase in the JUnit XML files matching ``xml_glob`` as
    features and scenarios nested under the current test.

    Fails if fewer than ``min_tests`` testcases are found, or, after
    reporting, if more than ``max_skipped`` were skipped, so that a lost
    dependency or broken test discovery cannot pass quietly.
    """
    xml_paths = sorted(glob.glob(xml_glob, recursive=True))
    if not xml_paths:
        fail(f"no JUnit XML files match {xml_glob}")

    try:
        cases = parse_junit(xml_paths, strip_prefix=strip_prefix)
    except ValueError as error:
        fail(str(error))
    if len(cases) < min_tests:
        fail(f"expected at least {min_tests} tests, found {len(cases)} in {xml_paths}")

    counts = {}
    for case in cases:
        counts[case["outcome"]] = counts.get(case["outcome"], 0) + 1
    note(
        f"{len(cases)} upstream tests in {len(xml_paths)} file(s): "
        + ", ".join(f"{n} {outcome}" for outcome, n in sorted(counts.items()))
    )

    skip_reasons = {}
    for case in cases:
        if case["outcome"] == "skipped":
            reason = " ".join(case["message"].split())[:200]
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
    if skip_reasons:
        note(
            "skip reasons:\n"
            + "\n".join(
                f"{n:5} {reason}"
                for reason, n in sorted(skip_reasons.items(), key=lambda item: -item[1])
            )
        )

    _report(_tree(cases))

    skipped = counts.get("skipped", 0)
    if max_skipped is not None and skipped > max_skipped:
        fail(
            f"{skipped} upstream tests were skipped, more than the {max_skipped} "
            "expected; see the skip reasons above"
        )
