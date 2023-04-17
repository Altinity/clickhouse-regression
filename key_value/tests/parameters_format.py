from key_value.tests.steps import *


@TestScenario
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter_Format("1.0")
)
def quoting_character_format(self, node=None):
    """Check that `quoting_character` can be specified only with one symbol."""
    if node is None:
        node = self.context.node

    with Given("I specify supported and unsupported parameters"):
        supported_specifying = ["'1'", "'q'"]
        unsupported_specifying = ["'grkgork'", "1203", "[]", "[100]"]

    with When(
        "I check ClickHouse supports properly specified `quoting_character` parameter"
    ):
        for i in supported_specifying:
            r = node.query(f"SELECT extractKeyValuePairs('a:a', ':', ',', {i})")
            assert r.exitcode == 0
    with When(
        "I check ClickHouse returns an error if `quoting_character` specified wrong"
    ):
        for i in unsupported_specifying:
            r = node.query(
                f"SELECT extractKeyValuePairs('a:a', ':', ',', {i})", no_checks=True
            )
            assert r.exitcode != 0


@TestScenario
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiters_Format("1.0")
)
def pair_delimiters_format(self, node=None):
    """Check that `pair_delimiters` can be specified with any string."""
    if node is None:
        node = self.context.node

    with Given("I specify supported and unsupported parameters"):
        supported_specifying = ["' ,;'", "','"]
        unsupported_specifying = ["1203", "[]", "[100]"]

    with When(
        "I check ClickHouse supports properly specified `pair_delimiters` parameter"
    ):
        for i in supported_specifying:
            r = node.query(f"SELECT extractKeyValuePairs('a:a', ':', {i})")
            assert r.exitcode == 0
    with When(
        "I check ClickHouse returns an error if `pair_delimiters` specified wrong"
    ):
        for i in unsupported_specifying:
            r = node.query(
                f"SELECT extractKeyValuePairs('a:a', ':', {i})", no_checks=True
            )
            assert r.exitcode != 0


@TestScenario
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter_Format(
        "1.0"
    )
)
def key_value_pair_delimiter_format(self, node=None):
    """Check that `key_value_pair_delimiter` can be specified only with one symbol."""
    if node is None:
        node = self.context.node

    with Given("I specify supported and unsupported parameters"):
        supported_specifying = ["'1'", "'q'"]
        unsupported_specifying = ["'grkgork'", "1203", "[]", "[100]"]

    with When(
        "I check ClickHouse supports properly specified `key_value_pair_delimiter` parameter"
    ):
        for i in supported_specifying:
            r = node.query(f"SELECT extractKeyValuePairs('a:a', {i})")
            assert r.exitcode == 0
    with When(
        "I check ClickHouse returns an error if `key_value_pair_delimiter` specified wrong"
    ):
        for i in unsupported_specifying:
            r = node.query(f"SELECT extractKeyValuePairs('a:a', {i})", no_checks=True)
            assert r.exitcode != 0


@TestModule
@Name("parameters formats")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse's extractKeyValuePairs function accepts specifying parameters
    and returns an error if a parameter is specified incorrectly."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
