from testflows.core import *
from testflows.asserts import error

from helpers.tables import *
from helpers.datatypes import *
from helpers.common import getuid


def datatype_from_string(datatype_str):
    """Convert datatype string to Column datatype object."""
    datatype_str = datatype_str.strip()

    if "(" in datatype_str and datatype_str.endswith(")"):
        name_end = datatype_str.index("(")
        type_name = datatype_str[:name_end]
        args_str = datatype_str[name_end + 1 : -1]

        args = []
        depth, start = 0, 0
        for i, char in enumerate(args_str):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == "," and depth == 0:
                args.append(args_str[start:i].strip())
                start = i + 1
        if args_str[start:].strip():
            args.append(args_str[start:].strip())

        if type_name == "Nullable":
            return Nullable(datatype_from_string(args[0]))
        elif type_name == "Array":
            return Array(datatype_from_string(args[0]))
        elif type_name == "Map":
            if len(args) != 2:
                raise ValueError(f"Map requires 2 arguments, got {len(args)}")
            return Map(datatype_from_string(args[0]), datatype_from_string(args[1]))
        elif type_name == "Tuple":
            return Tuple([datatype_from_string(arg) for arg in args])
        elif type_name == "DateTime64":
            return DateTime64(int(args[0]))
        elif type_name in ("Decimal32", "Decimal64", "Decimal128", "Decimal256"):
            return globals()[type_name](int(args[0]))
        else:
            raise ValueError(f"Unknown parameterized type: {type_name}")

    type_map = {
        "Int8": Int8,
        "Int16": Int16,
        "Int32": Int32,
        "Int64": Int64,
        "Int128": Int128,
        "Int256": Int256,
        "UInt8": UInt8,
        "UInt16": UInt16,
        "UInt32": UInt32,
        "UInt64": UInt64,
        "UInt128": UInt128,
        "UInt256": UInt256,
        "Date": Date,
        "DateTime": DateTime,
        "String": String,
        "Float32": Float32,
        "Float64": Float64,
        "Bool": Boolean,
        "JSON": JSON,
    }
    if datatype_str not in type_map:
        raise ValueError(f"Unknown datatype: {datatype_str}")
    return type_map[datatype_str]()


def create_columns_from_config(base_columns, alias_columns):
    """Create Column objects from JSON configuration for left and right tables.

    If a column in alias_columns has an 'expression', it's created as an alias.
    If it has a 'datatype' instead, it's created as a regular column (not an alias).
    """
    columns = []

    for col in base_columns:
        columns.append(Column(name=col["name"], datatype=datatype_from_string(col["datatype"])))

    for col in alias_columns:
        if "expression" in col:
            columns.append(Column(name=col["name"], alias=col["expression"]))
        elif "datatype" in col:
            columns.append(Column(name=col["name"], datatype=datatype_from_string(col["datatype"])))
        else:
            raise ValueError(f"Alias column '{col['name']}' must have either 'expression' or 'datatype'")

    return columns


def create_hybrid_columns_from_config(base_columns, alias_columns, alias_columns_definition_for_hybrid_table=None):
    """Create Column objects for hybrid table definition. Uses
    alias_columns_definition_for_hybrid_table if it exists, otherwise uses alias_columns.
    """
    columns = []

    for col in base_columns:
        columns.append(Column(name=col["name"], datatype=datatype_from_string(col["datatype"])))

    if alias_columns_definition_for_hybrid_table is not None:
        alias_columns_to_use = alias_columns_definition_for_hybrid_table
    else:
        alias_columns_to_use = alias_columns

    for col in alias_columns_to_use:
        if "hybrid_type" not in col:
            raise ValueError(f"hybrid_type is required for alias column '{col['name']}'")
        columns.append(Column(name=col["name"], datatype=datatype_from_string(col["hybrid_type"])))

    return columns


def outline(
    self,
    alias_columns,
    watermark,
    expected,
    test_queries,
    base_columns=None,
    order_by=None,
    partition_by=None,
    left_base_columns=None,
    right_base_columns=None,
    left_alias_columns=None,
    right_alias_columns=None,
    alias_columns_definition_for_hybrid_table=None,
    node=None,
):
    """Common test outline for hybrid alias column tests."""
    if node is None:
        node = self.context.node

    with Given(f"Get base columns for each segment (default to shared base_columns if not specified)"):
        if left_base_columns is None:
            if base_columns:
                left_base_columns = base_columns
            else:
                assert False, f"base_columns or left_base_columns should be specified"
        if right_base_columns is None:
            if base_columns:
                right_base_columns = base_columns
            else:
                assert False, f"base_columns or right_base_columns should be specified"

    with And(f"Get alias columns for each segment (default to shared alias_columns if not specified)"):
        if left_alias_columns is None:
            left_alias_columns = alias_columns
        if right_alias_columns is None:
            right_alias_columns = alias_columns

    with And("create left table"):
        left_table_name = f"left_{getuid()}"
        right_table_name = f"right_{getuid()}"

        with By("get left segment columns"):
            left_segment_columns = create_columns_from_config(left_base_columns, left_alias_columns)

        with And("create left table"):
            left_table = create_table(
                name=left_table_name,
                engine="MergeTree",
                columns=left_segment_columns,
                order_by=order_by,
                partition_by=partition_by,
            )

        with And("populate left table with test data"):
            left_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create right table"):
        with By("get right segment columns"):
            right_segment_columns = create_columns_from_config(right_base_columns, right_alias_columns)

        with And("create right table"):
            right_table = create_table(
                name=right_table_name,
                engine="MergeTree",
                columns=right_segment_columns,
                order_by=order_by,
                partition_by=partition_by,
            )

        with And("populate right table with test data"):
            right_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create hybrid table"):
        hybrid_table_name = f"hybrid_{getuid()}"
        hybrid_columns = create_hybrid_columns_from_config(
            base_columns, alias_columns, alias_columns_definition_for_hybrid_table
        )

        left_table_func = f"remote('localhost', currentDatabase(), '{left_table_name}')"
        left_predicate = watermark["left_predicate"]
        right_table_func = f"remote('localhost', currentDatabase(), '{right_table_name}')"
        right_predicate = watermark["right_predicate"]
        hybrid_engine = f"Hybrid({left_table_func}, {left_predicate}, {right_table_func}, {right_predicate})"

        expected_exitcode = expected.get("exitcode") if expected else None
        expected_error_message = expected.get("error_message") if expected else None

        create_table(
            name=hybrid_table_name,
            engine=hybrid_engine,
            columns=hybrid_columns,
            settings=[("allow_experimental_hybrid_table", 1)],
            exitcode=expected_exitcode,
            message=expected_error_message,
        )

    if expected_exitcode:
        return

    if test_queries:
        with And("create reference MergeTree table (uses same column definition as hybrid)"):
            merge_tree_reference_table = f"reference_merge_tree_{getuid()}"
            merge_tree_reference_table_columns = create_hybrid_columns_from_config(
                base_columns, alias_columns, alias_columns_definition_for_hybrid_table
            )
            create_table(
                name=merge_tree_reference_table,
                engine="MergeTree",
                columns=merge_tree_reference_table_columns,
                order_by=order_by,
                partition_by=partition_by,
            )

        with And("populate reference table from left and right segment tables using watermark predicates"):
            # Get base column names for each segment (columns that can be inserted)
            left_column_names = [col["name"] for col in left_base_columns] + [col["name"] for col in left_alias_columns]
            right_column_names = [col["name"] for col in right_base_columns] + [
                col["name"] for col in right_alias_columns
            ]

            left_base_columns_str = ", ".join(left_column_names)
            right_base_columns_str = ", ".join(right_column_names)

            node.query(
                f"INSERT INTO {merge_tree_reference_table} ({left_base_columns_str}) SELECT {left_base_columns_str} FROM {left_table_name} WHERE {left_predicate}"
            )
            node.query(
                f"INSERT INTO {merge_tree_reference_table} ({right_base_columns_str}) SELECT {right_base_columns_str} FROM {right_table_name} WHERE {right_predicate}"
            )

        with Then("compare hybrid table results with MergeTree reference table"):
            for i, test_query_item in enumerate(test_queries, 1):
                if test_query_item is None:
                    continue

                if isinstance(test_query_item, dict):
                    test_query_template = test_query_item.get("query", "")
                    expected_exitcode = test_query_item.get("exitcode", None)
                    expected_message = test_query_item.get("message", None)
                else:
                    test_query_template = test_query_item
                    expected_exitcode = None
                    expected_message = None

                if not test_query_template:
                    continue

                with By(f"query {i}/{len(test_queries)}"):
                    reference_query = test_query_template.format(hybrid_table=merge_tree_reference_table)
                    test_query = test_query_template.format(hybrid_table=hybrid_table_name)

                    query_kwargs = {}
                    if expected_exitcode is not None:
                        query_kwargs["exitcode"] = expected_exitcode
                    if expected_message is not None:
                        query_kwargs["message"] = expected_message

                    if expected_exitcode is None or expected_exitcode == 0:
                        reference_result = node.query(reference_query).output
                        hybrid_result = node.query(test_query, **query_kwargs).output
                        assert hybrid_result == reference_result, error()
                    else:
                        node.query(test_query, **query_kwargs)
