import uuid

from extended_precision_data_types.requirements import *
from extended_precision_data_types.common import *
from helpers.common import check_clickhouse_version


def get_table_name():
    return "table" + "_" + str(uuid.uuid1()).replace("-", "_")


@TestOutline(Suite)
@Requirements(
    RQ_SRS_020_ClickHouse_Extended_Precision_Arrays_Int_Supported("1.0"),
    RQ_SRS_020_ClickHouse_Extended_Precision_Arrays_Int_NotSupported("1.0"),
    RQ_SRS_020_ClickHouse_Extended_Precision_Arrays_Dec_Supported("1.0"),
    RQ_SRS_020_ClickHouse_Extended_Precision_Arrays_Dec_NotSupported("1.0"),
)
def array_func(self, data_type, node=None):
    """Check array functions with extended precision data types."""
    if check_clickhouse_version(">=23.2")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=23.2")

    if node is None:
        node = self.context.node

    for func in [
        "arrayPopBack(",
        "arrayPopFront(",
        "arraySort(",
        "arrayReverseSort(",
        "arrayDistinct(",
        "arrayEnumerate(",
        "arrayEnumerateDense(",
        "arrayEnumerateUniq(",
        "arrayReverse(",
        "reverse(",
        "arrayFlatten(",
        "arrayCompact(",
        "arrayReduceInRanges('sum', [(1, 5)],",
        "arrayMap(x -> (x + 2),",
        "arrayFill(x -> x=3,",
        "arrayReverseFill(x -> x=3,",
        f"arrayConcat([{to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)}],",
        "arrayFilter(x -> x == 1, ",
    ]:
        with Scenario(f"Inline - {data_type} - {func})"):
            execute_query(
                f"""
                SELECT {func}array({to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)}))
                """
            )

        with Scenario(f"Table - {data_type} - {func})"):
            table_name = get_table_name()

            table(name=table_name, data_type=f"Array({data_type})")

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)})) FORMAT TabSeparated"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in ["arraySplit((x, y) -> x=y, [0, 0, 0],"]:
        with Scenario(f"Inline - {data_type} - {func})"):
            execute_query(
                f"SELECT {func}array({to_data_type(data_type,3)}, {to_data_type(data_type,2)},"
                f"{to_data_type(data_type,1)}))"
            )

        with Scenario(f"Table - {data_type} - {func})"):
            table_name = get_table_name()

            table(name=table_name, data_type=f"Array(Array({data_type}))")

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}))"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in [f"arrayZip([{to_data_type(data_type,1)}],"]:
        with Scenario(f"Inline - {data_type} - {func})"):
            execute_query(f"SELECT {func}array({to_data_type(data_type,3)}))")

        with Scenario(f"Table - {data_type} - {func})"):
            table_name = get_table_name()

            table(name=table_name, data_type=f"Array(Tuple({data_type}, {data_type}))")

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}array({to_data_type(data_type,1)})) FORMAT TabSeparated"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in [
        "empty(",
        "notEmpty(",
        "length(",
        "arrayCount(x -> x == 1, ",
        "arrayUniq(",
        "arrayJoin(",
        "arrayExists(x -> x==1,",
        "arrayAll(x -> x==1,",
        "arrayMin(",
        "arrayMax(",
        "arraySum(",
        "arrayAvg(",
        "arrayReduce('max', ",
        "arrayFirst(x -> x==3,",
        "arrayFirstIndex(x -> x==3,",
        f"hasAll([{to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)}], ",
        f"hasAny([{to_data_type(data_type,2)}, {to_data_type(data_type,1)}], ",
        f"hasSubstr([{to_data_type(data_type,2)}, {to_data_type(data_type,1)}], ",
    ]:
        if func in [
            "arrayMin(",
            "arrayMax(",
            "arraySum(",
            "arrayAvg(",
        ] and data_type in ["Decimal256(0)"]:
            exitcode = 44
            message = "Exception:"
            if check_clickhouse_version(">=23.2")(self):
                exitcode = 0
                message = ""

            with Scenario(f"Inline - {data_type} - {func})"):
                node.query(
                    f"SELECT {func}array({to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)})) FORMAT TabSeparated",
                    exitcode=exitcode,
                    message=message,
                )

            with Scenario(f"Table - {data_type} - {func})"):
                table_name = get_table_name()

                table(name=table_name, data_type=data_type)

                with When("I insert the output into the table"):
                    node.query(
                        f"INSERT INTO {table_name} SELECT {func}array({to_data_type(data_type,3)},"
                        f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)})) FORMAT TabSeparated",
                        exitcode=exitcode,
                        message=message,
                    )

                execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

        else:
            with Scenario(f"Inline - {data_type} - {func})"):
                if check_clickhouse_version(">=23.10")(self):
                    self.context.snapshot_id = "tests.post23.10"
                execute_query(
                    f"SELECT {func}array({to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)}))"
                )

            with Scenario(f"Table - {data_type} - {func})"):
                table_name = get_table_name()

                table(name=table_name, data_type=data_type)

                with When("I insert the output into the table"):
                    node.query(
                        f"INSERT INTO {table_name} SELECT {func}array({to_data_type(data_type,3)},"
                        f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}))"
                    )

                execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in ["arrayDifference(", "arrayCumSum(", "arrayCumSumNonNegative("]:
        if data_type in ["Decimal256(0)"]:
            exitcode = 44
        else:
            exitcode = 43

        message = "Exception:"
        if check_clickhouse_version(">=23.2")(self) and data_type in ["Decimal256(0)"]:
            exitcode = 0
            message = ""

        with Scenario(f"Inline - {data_type} - {func})"):
            if check_clickhouse_version(">=23.2")(self) and data_type in [
                "Decimal256(0)"
            ]:
                exitcode = 0
                message = ""

            if check_clickhouse_version(">=23.4")(self) and data_type in [
                "UInt256",
                "UInt128",
                "Int256",
                "Int128",
            ]:
                exitcode = 0
                message = ""

            node.query(
                f"SELECT {func}array({to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)})) FORMAT TabSeparated",
                exitcode=exitcode,
                message=message,
            )

        with Scenario(f"Table - {data_type} - {func})"):
            table_name = get_table_name()
            message = "Exception:"
            if check_clickhouse_version(">=23.2")(self) and data_type in [
                "Decimal256(0)"
            ]:
                exitcode = 70

            if check_clickhouse_version(">=23.4")(self) and data_type in [
                "UInt256",
                "UInt128",
                "Int256",
                "Int128",
            ]:
                exitcode = 43
                message = "Exception:"

            table(name=table_name, data_type=data_type)

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)})) FORMAT TabSeparated",
                    exitcode=exitcode,
                    message=message,
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in ["arrayElement"]:
        with Scenario(f"Inline - {data_type} - {func}"):
            execute_query(
                f"""
                SELECT {func}(array({to_data_type(data_type,3)}, {to_data_type(data_type,2)}, {to_data_type(data_type,1)}), 1)
                """
            )

        with Scenario(f"Table - {data_type} - {func}"):
            table_name = get_table_name()

            table(name=table_name, data_type=data_type)

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}(array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}), 1)"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in ["arrayPushBack", "arrayPushFront"]:
        with Scenario(f"Inline - {data_type} - {func}"):
            execute_query(
                f"SELECT {func}(array({to_data_type(data_type,3)}, {to_data_type(data_type,2)},"
                f"{to_data_type(data_type,1)}), {to_data_type(data_type,1)})"
            )

        with Scenario(f"Table - {data_type} - {func}"):
            table_name = get_table_name()

            table(name=table_name, data_type=f"Array({data_type})")

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}(array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}), {to_data_type(data_type,1)})"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in ["arrayResize", "arraySlice"]:
        with Scenario(f"Inline - {data_type} - {func}"):
            execute_query(
                f"SELECT {func}(array({to_data_type(data_type,3)},"
                f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}), 1)"
            )

        with Scenario(f"Table - {data_type} - {func}"):
            table_name = get_table_name()

            table(name=table_name, data_type=f"Array({data_type})")

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}(array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}), 1)"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    for func in ["has", "indexOf", "countEqual"]:
        with Scenario(f"Inline - {data_type} - {func}"):
            execute_query(
                f"SELECT {func}(array({to_data_type(data_type,3)},"
                f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}), NULL)"
            )

        with Scenario(f"Table - {data_type} - {func}"):
            table_name = get_table_name()

            table(name=table_name, data_type=data_type)

            with When("I insert the output into the table"):
                node.query(
                    f"INSERT INTO {table_name} SELECT {func}(array({to_data_type(data_type,3)},"
                    f"{to_data_type(data_type,2)}, {to_data_type(data_type,1)}), NULL)"
                )

            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")


@TestOutline(Suite)
@Requirements(
    RQ_SRS_020_ClickHouse_Extended_Precision_Tuple("1.0"),
)
def tuple_func(self, data_type, node=None):
    """Check tuple functions with extended precision data types."""

    if node is None:
        node = self.context.node

    with Scenario(f"Creating a tuple with {data_type}"):
        node.query(
            f"SELECT tuple({to_data_type(data_type,1)}, {to_data_type(data_type,1)}, {to_data_type(data_type,1)}) FORMAT TabSeparated"
        )

    with Scenario(f"Creating a tuple with {data_type} on a table"):
        table_name = get_table_name()

        table(
            name=table_name, data_type=f"Tuple({data_type}, {data_type}, {data_type})"
        )

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT tuple({to_data_type(data_type,1)},"
                f"{to_data_type(data_type,1)}, {to_data_type(data_type,1)})"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"tupleElement with {data_type}"):
        node.query(
            f"SELECT tupleElement(({to_data_type(data_type,1)}, {to_data_type(data_type,1)}), 1) FORMAT TabSeparated"
        )

    with Scenario(f"tupleElement with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type=data_type)

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT tupleElement(({to_data_type(data_type,1)}, {to_data_type(data_type,1)}), 1)"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"untuple with {data_type}"):
        node.query(
            f"SELECT untuple(({to_data_type(data_type,1)},)) FORMAT TabSeparated"
        )

    with Scenario(f"untuple with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type=data_type)

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT untuple(({to_data_type(data_type,1)},))"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"tupleHammingDistance with {data_type}"):
        node.query(
            f"SELECT tupleHammingDistance(({to_data_type(data_type,1)}, {to_data_type(data_type,1)}),"
            f"({to_data_type(data_type,2)}, {to_data_type(data_type,2)})) FORMAT TabSeparated"
        )

    with Scenario(f"tupleHammingDistance with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type=data_type)

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT tupleHammingDistance(({to_data_type(data_type,1)},"
                f"{to_data_type(data_type,1)}), ({to_data_type(data_type,2)}, {to_data_type(data_type,2)})) FORMAT TabSeparated"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")


@TestOutline(Suite)
@Requirements(
    RQ_SRS_020_ClickHouse_Extended_Precision_Map_Supported("1.0"),
    RQ_SRS_020_ClickHouse_Extended_Precision_Map_NotSupported("1.0"),
)
def map_func(self, data_type, node=None):
    """Check Map functions with extended precision data types."""

    if node is None:
        node = self.context.node

    with Scenario(f"Creating a map with {data_type}"):
        node.query(
            f"SELECT map('key1', {to_data_type(data_type,1)}, 'key2', {to_data_type(data_type,2)}) FORMAT TabSeparated"
        )

    with Scenario(f"Creating a map with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type=f"Map(String, {data_type})")

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT map('key1', {to_data_type(data_type,1)}, 'key2', {to_data_type(data_type,2)})"
            )

        execute_query(f"SELECT * FROM {table_name}")

    with Scenario(f"mapAdd with {data_type}"):
        sql = (
            f"SELECT mapAdd(([{to_data_type(data_type,1)}, {to_data_type(data_type,2)}],"
            f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]),"
            f"([{to_data_type(data_type,1)}, {to_data_type(data_type,2)}],"
            f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]))"
        )
        if data_type.startswith("Decimal"):
            node.query(sql, exitcode=43, message="Exception:")
        else:
            execute_query(sql)

    with Scenario(f"mapAdd with {data_type} on a table"):
        table_name = get_table_name()

        table(
            name=table_name, data_type=f"Tuple(Array({data_type}), Array({data_type}))"
        )

        with When("I insert the output into a table"):
            sql = (
                f"INSERT INTO {table_name} SELECT mapAdd(("
                f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}],"
                f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]),"
                f"([{to_data_type(data_type,1)}, {to_data_type(data_type,2)}],"
                f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]))"
            )
            exitcode, message = 0, None

            if data_type.startswith("Decimal"):
                exitcode, message = 43, "Exception:"
            node.query(sql, exitcode=exitcode, message=message)

        execute_query(f"""SELECT * FROM {table_name} ORDER BY a ASC""")

    with Scenario(f"mapSubtract with {data_type}"):
        sql = (
            f"SELECT mapSubtract(("
            f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}],"
            f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]),"
            f"([{to_data_type(data_type,1)}, {to_data_type(data_type,2)}],"
            f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]))"
        )

        if data_type.startswith("Decimal"):
            node.query(sql, exitcode=43, message="Exception:")
        else:
            execute_query(sql)

    with Scenario(f"mapSubtract with {data_type} on a table"):
        table_name = get_table_name()

        table(
            name=table_name, data_type=f"Tuple(Array({data_type}), Array({data_type}))"
        )

        with When("I insert the output into a table"):
            sql = (
                f"INSERT INTO {table_name} SELECT mapSubtract(([{to_data_type(data_type,1)},"
                f"{to_data_type(data_type,2)}], [{to_data_type(data_type,1)},"
                f"{to_data_type(data_type,2)}]), ([{to_data_type(data_type,1)},"
                f"{to_data_type(data_type,2)}], [{to_data_type(data_type,1)}, {to_data_type(data_type,2)}]))"
            )
            exitcode, message = 0, None

            if data_type.startswith("Decimal"):
                exitcode, message = 43, "Exception:"
            node.query(sql, exitcode=exitcode, message=message)

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"mapPopulateSeries with {data_type}"):
        sql = (
            f"SELECT mapPopulateSeries([1,2,3], [{to_data_type(data_type,1)},"
            f"{to_data_type(data_type,2)}, {to_data_type(data_type,3)}], 5) "
            f"FORMAT TabSeparated"
        )

        exitcode, message = 0, None
        if data_type.startswith("Decimal") or check_clickhouse_version("<21.9")(self):
            (exitcode, message) = (
                (44, "Exception:")
                if check_clickhouse_version("<22.3")(self)
                else (43, "Exception:")
            )
        node.query(sql, exitcode=exitcode, message=message)

    with Scenario(f"mapPopulateSeries with {data_type} on a table"):
        table_name = get_table_name()

        table(
            name=table_name, data_type=f"Tuple(Array({data_type}), Array({data_type}))"
        )

        with When("I insert the output into a table"):
            sql = (
                f"INSERT INTO {table_name} SELECT mapPopulateSeries([1,2,3],"
                f"[{to_data_type(data_type,1)}, {to_data_type(data_type,2)}, {to_data_type(data_type,3)}], 5)"
            )

            exitcode, message = 0, None
            if data_type.startswith("Decimal"):
                (exitcode, message) = (
                    (44, "Exception:")
                    if check_clickhouse_version("<22.3")(self)
                    else (43, "Exception:")
                )
            node.query(sql, exitcode=exitcode, message=message)

        if check_clickhouse_version(">=21.9")(self):
            execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"mapContains with {data_type}"):
        node.query(
            f"SELECT mapContains( map('key1', {to_data_type(data_type,1)},"
            f"'key2', {to_data_type(data_type,2)}), 'key1') FORMAT TabSeparated"
        )

    with Scenario(f"mapContains with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type=data_type)

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT mapContains( map('key1', {to_data_type(data_type,1)},"
                f"'key2', {to_data_type(data_type,2)}), 'key1')"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"mapKeys with {data_type}"):
        node.query(
            f"SELECT mapKeys( map('key1', {to_data_type(data_type,1)}, 'key2', {to_data_type(data_type,2)})) FORMAT TabSeparated"
        )

    with Scenario(f"mapKeys with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type="Array(String)")

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT mapKeys( map('key1', {to_data_type(data_type,1)},"
                f"'key2', {to_data_type(data_type,2)}))"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")

    with Scenario(f"mapValues with {data_type}"):
        node.query(
            f"SELECT mapValues( map('key1', {to_data_type(data_type,1)}, 'key2', {to_data_type(data_type,2)})) FORMAT TabSeparated"
        )

    with Scenario(f"mapValues with {data_type} on a table"):
        table_name = get_table_name()

        table(name=table_name, data_type=f"Array({data_type})")

        with When("I insert the output into a table"):
            node.query(
                f"INSERT INTO {table_name} SELECT mapValues( map('key1', {to_data_type(data_type,1)},"
                f"'key2', {to_data_type(data_type,2)}))"
            )

        execute_query(f"SELECT * FROM {table_name} ORDER BY a ASC")


@TestFeature
@Name("array, tuple, map")
@Examples(
    "data_type",
    [
        ("Int128",),
        ("Int256",),
        ("UInt128",),
        ("UInt256",),
        ("Decimal256(0)",),
    ],
)
def feature(self, node="clickhouse1", stress=None, parallel=None):
    """Check that array, tuple, and map functions work with
    extended precision data types.
    """
    self.context.node = self.context.cluster.node(node)

    with allow_experimental_bigint(self.context.node):
        for example in self.examples:
            (data_type,) = example

            with Feature(data_type):
                Suite(test=array_func)(data_type=data_type)
                Suite(test=tuple_func)(data_type=data_type)

                with Given("I allow experimental map type"):
                    allow_experimental_map_type()

                Suite(test=map_func)(data_type=data_type)
