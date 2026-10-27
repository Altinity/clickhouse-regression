"""`allow_experimental_aggregate_function_states_in_open_formats` gates
creating, altering, reading and writing Iceberg tables with aggregate columns."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.aggregate_states import *
from iceberg.tests.iceberg_engine.aggregate_states.steps import *


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Gate_Create("1.0"))
@Examples(
    "columns",
    [
        (COLUMNS,),
        ("k Int32, s SimpleAggregateFunction(sum, Int64)",),
    ],
    args=Args(flags=TE),
)
def create_refused_without_setting(self, columns):
    """CREATE TABLE with an aggregate column fails naming the setting and
    writes nothing to the table location."""
    table_name = f"agg_{getuid()}"

    with When("CREATE TABLE without the setting"):
        iceberg_s3_table(
            table_name=table_name,
            columns=columns,
            engine_setting=False,
            query_settings=[("write_full_path_in_iceberg_metadata", 1)],
            message=SETTING,
        )

    with Then("the table does not exist"):
        exists = self.context.node.query(f"EXISTS TABLE {table_name}").output.strip()
        assert exists == "0", error(f"EXISTS TABLE {table_name} returned {exists}")

    with And("nothing was written under the table location"):
        objects = s3.object_inventory(table_prefix(table_name))
        assert objects == {}, error(f"objects written by a refused CREATE: {sorted(objects)}")


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Gate_AlterAddColumn("1.0"))
@Examples(
    "column refused_with_setting",
    [
        ("extra SimpleAggregateFunction(anyLast, Nullable(String))", None),
        ("extra AggregateFunction(uniqExact, String)", "non-nullable"),
    ],
    args=Args(flags=TE),
)
def alter_add_column_refused_without_setting(self, column, refused_with_setting):
    """ADD COLUMN of an aggregate column fails naming the setting and leaves
    the schema unchanged; with the setting the column is added and annotated.

    An AggregateFunction column cannot be Nullable, and Iceberg allows adding
    only optional columns, so with the setting it is still refused, by the
    Iceberg rule (``refused_with_setting``)."""
    node = self.context.node

    with Given("a table with aggregate columns"):
        table_name = iceberg_s3_table()
        prefix = table_prefix(table_name)
        before, before_key = read_latest_metadata(prefix)

    with When("ADD COLUMN without the setting"):
        query_refused(
            query=f"ALTER TABLE {table_name} ADD COLUMN {column}",
            settings=[("allow_insert_into_iceberg", 1)],
            message=SETTING,
        )

    with Then("the schema is unchanged"):
        after, after_key = read_latest_metadata(prefix)
        assert after_key == before_key, error(
            f"a refused ALTER wrote metadata: {before_key} -> {after_key}"
        )
        assert fields_by_name(after) == fields_by_name(before), error()

    if refused_with_setting:
        with When("ADD COLUMN with the setting"):
            query_refused(
                query=f"ALTER TABLE {table_name} ADD COLUMN {column}",
                settings=[("allow_insert_into_iceberg", 1), (SETTING, 1)],
                message=refused_with_setting,
            )
        return

    with When("ADD COLUMN with the setting"):
        node.query(
            f"ALTER TABLE {table_name} ADD COLUMN {column}",
            settings=[("allow_insert_into_iceberg", 1), (SETTING, 1)],
        )

    with Then("the new field carries the annotation"):
        metadata, key = read_latest_metadata(prefix)
        name, type_name = column.split(" ", 1)
        assert_annotations(metadata=metadata, expected={name: type_name}, where=key)


@TestScenario
@Requirements(
    RQ_Iceberg_AggregateStates_Iceberg_Gate_Read("1.0"),
    RQ_Iceberg_AggregateStates_Iceberg_Gate_TableFunctionScope("1.0"),
)
def table_function_applies_setting_per_query(self):
    """The icebergS3 table function honours the setting of each query: with
    it the states merge, without it SELECT and DESCRIBE are refused, and the
    next query with it succeeds again."""
    with Given("a table with states"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        function = icebergs3_function(table_name)
        expected = expected_result()

    with When("SELECT with the setting"):
        assert_merge_matches(source=function, expected=expected)

    with And("SELECT without the setting"):
        query_refused(
            query=merge_select(function),
            message=SETTING,
            exitcode=SUPPORT_IS_DISABLED,
        )

    with And("DESCRIBE without the setting"):
        query_refused(
            query=f"DESCRIBE {function}",
            message=SETTING,
            exitcode=SUPPORT_IS_DISABLED,
        )

    with Then("SELECT with the setting again"):
        assert_merge_matches(source=function, expected=expected)


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Gate_Read("1.0"))
def insert_into_table_function_refused_without_setting(self):
    """INSERT reads the schema too, so it is refused without the setting and
    commits nothing."""
    with Given("a table with states"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        function = icebergs3_function(table_name)
        before_key = latest_metadata_key(table_prefix(table_name))

    with When("INSERT INTO FUNCTION without the setting"):
        query_refused(
            query=f"INSERT INTO FUNCTION {function} (k, u, s) {states_select(start=200)}",
            settings=[
                ("allow_insert_into_iceberg", 1),
                ("write_full_path_in_iceberg_metadata", 1),
            ],
            message=SETTING,
        )

    with Then("no commit happened"):
        after_key = latest_metadata_key(table_prefix(table_name))
        assert after_key == before_key, error(
            f"a refused INSERT committed: {before_key} -> {after_key}"
        )
        assert_merge_matches(source=function, expected=expected_result())


@TestScenario
@Requirements(
    RQ_Iceberg_AggregateStates_Iceberg_Gate_Read("1.0"),
    RQ_Iceberg_AggregateStates_Parquet_SimpleAggregateFunction("1.0"),
)
def simple_columns_readable_without_setting(self):
    """A table whose only aggregate columns are SimpleAggregateFunction is not
    gated on read and still reports the annotated type."""
    node = self.context.node
    columns = "k Int32, s SimpleAggregateFunction(sum, Int64)"

    with Given("a table with a simple column"):
        table_name = iceberg_s3_table(columns=columns)
        node.query(
            f"INSERT INTO {table_name} SELECT toInt32(number % 2), toInt64(number) "
            "FROM numbers(200)",
            settings=write_settings(),
        )
        function = icebergs3_function(table_name)

    with Then("DESCRIBE without the setting reports SimpleAggregateFunction"):
        assert describe(function) == [("k", "Int32"), ("s", S_TYPE)], error()

    with And("SELECT without the setting aggregates the values"):
        actual = node.query(
            f"SELECT k, sum(s) FROM {function} GROUP BY k ORDER BY k FORMAT TabSeparated"
        ).output
        expected = node.query(
            "SELECT toInt32(number % 2) AS k, sum(toInt64(number)) FROM numbers(200) "
            "GROUP BY k ORDER BY k FORMAT TabSeparated"
        ).output
        assert actual == expected, error()


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Gate_TableEngineScope("1.0"))
def table_engine_keeps_first_outcome_after_attach(self):
    """The table engine parses the schema once: the first query after ATTACH
    decides, later queries without the setting inherit a success, and a fresh
    ATTACH followed by a query without the setting is refused."""
    node = self.context.node

    with Given("a table with states"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        expected = expected_result()

    with When("DETACH and ATTACH, then the first query has the setting"):
        node.query(f"DETACH TABLE {table_name}")
        node.query(f"ATTACH TABLE {table_name}")
        assert_merge_matches(source=table_name, expected=expected)

    with Then("a later query without the setting succeeds too"):
        assert_merge_matches(source=table_name, expected=expected, settings=None)

    with When("DETACH and ATTACH, then the first query lacks the setting"):
        node.query(f"DETACH TABLE {table_name}")
        node.query(f"ATTACH TABLE {table_name}")

    with Then("it is refused"):
        query_refused(
            query=merge_select(table_name),
            message=SETTING,
            exitcode=SUPPORT_IS_DISABLED,
        )


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Gate_InsertWriter("1.0"))
def insert_writer_takes_setting_from_create_settings_clause(self):
    """The Parquet writer of the table engine takes the setting from the
    CREATE TABLE SETTINGS clause: a table created with it only as a query
    setting refuses INSERT of states with UNKNOWN_TYPE even when the INSERT
    sets it, and a table created with the clause accepts it."""
    with Given("a table created with the setting only as a query setting"):
        without_clause = iceberg_s3_table(engine_setting=False)

    with When("INSERT with the setting"):
        query_refused(
            query=f"INSERT INTO {without_clause} (k, u, s) {states_select()}",
            settings=write_settings(),
            message="UNKNOWN_TYPE",
        )

    with Then("nothing was committed"):
        keys = data_file_keys(table_prefix(without_clause))
        assert keys == [], error(f"data files written by a refused INSERT: {keys}")

    with Given("a table created with the setting in its SETTINGS clause"):
        with_clause = iceberg_s3_table(engine_setting=True)

    with When("INSERT with the setting"):
        insert_states(table_name=with_clause)

    with Then("the states merge"):
        assert_merge_matches(source=with_clause, expected=expected_result())


@TestFeature
@Name("setting gate")
def feature(self):
    """The setting gates CREATE, ALTER, reads and writes."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
