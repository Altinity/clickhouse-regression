import pyarrow as pa
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder


class IcebergTestTable:
    def __init__(
        self,
        catalog,
        namespace,
        table_name,
        datatypes,
        location="s3://warehouse/data",
        partition_spec=None,
        sort_order=None,
    ):
        """
        catalog: Iceberg catalog
        namespace: table namespace
        table_name: table name
        datatypes: list of BaseIcebergTypeTest subclasses
        """
        self.catalog = catalog
        self.namespace = namespace
        self.table_name = table_name
        self.datatypes = datatypes
        self.partition_spec = partition_spec or PartitionSpec()
        self.sort_order = sort_order or SortOrder()

        self.fields = [
            NestedField(i + 1, dt.name, dt.iceberg_type, required=False)
            for i, dt in enumerate(self.datatypes)
        ]
        self.schema = Schema(*self.fields)

        self.table = self.catalog.create_table(
            identifier=f"{namespace}.{table_name}",
            schema=self.schema,
            location=location,
            partition_spec=self.partition_spec,
            sort_order=self.sort_order,
        )

        self.arrow_schema = pa.schema(
            [(dt.name, dt.arrow_type) for dt in self.datatypes]
        )

        self.rows = []

    def insert(self, rows_num=1):
        """Generate and insert rows into the Iceberg table."""
        new_rows = [
            {dt.name: dt.generate() for dt in self.datatypes} for _ in range(rows_num)
        ]
        self.table.append(pa.Table.from_pylist(new_rows, schema=self.arrow_schema))
        self.rows.extend(new_rows)
        return new_rows

    def expected_where_count(self, column_name, comparison_operator="=", value=None):
        """Compute expected number of rows matching the filter locally."""
        if value is None:
            return None

        ops = {
            "=": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }
        op_func = ops[comparison_operator]
        return sum(1 for row in self.rows if op_func(row[column_name], value))

    def expected_where_result(self, column_name, comparison_operator="=", value=None):
        """Compute expected number of rows matching the filter locally."""
        if value is None:
            return None

        ops = {
            "=": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }
        op_func = ops[comparison_operator]
        return "\n".join(
            [
                "\t".join(str(val) for val in row.values())
                for row in self.rows
                if op_func(row[column_name], value)
            ]
        )
