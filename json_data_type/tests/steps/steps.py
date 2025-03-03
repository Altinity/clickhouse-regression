from testflows.core import *

from helpers.common import getuid

import json


class JsonColumn:
    def __init__(
        self,
        name,
        max_dynamic_paths=0,
        max_dynamic_types=0,
        type_hints=None,
        skip_hints=None,
        skip_regexp_hints=None,
    ):
        """
        Initialize a JSON column with metadata.

        :param name: Column name
        :param value: JSON object
        :param max_dynamic_paths: Maximum number of dynamic paths
        :param max_dynamic_types: Maximum number of dynamic types
        :param type_hints: Type hints for specific paths
        :param skip_hints: Paths to skip
        :param skip_regexp_hints: Set of regular expressions matching JSON paths to be excluded
        """
        self.name = name
        self.value = {}
        self.max_dynamic_paths = max_dynamic_paths
        self.max_dynamic_types = max_dynamic_types
        self.type_hints = type_hints or {}
        self.skip_hints = skip_hints or set()
        self.skip_regexp_hints = skip_regexp_hints or set()

    def add_skip_hint(self, path):
        """Mark a specific path to be skipped in ClickHouse."""
        self.skip_hints.add(path)

    def add_skip_regexp_hint(self, pattern):
        """Mark a regular expression path to be skipped in ClickHouse."""
        self.skip_regexp_hints.add(pattern)

    def generate_column_definition(self):
        """Generate a valid ClickHouse JSON column definition."""
        hints = []

        if self.max_dynamic_paths:
            hints.append(f"max_dynamic_paths={self.max_dynamic_paths}")
        if self.max_dynamic_types:
            hints.append(f"max_dynamic_types={self.max_dynamic_types}")

        if self.type_hints:
            hints.extend(
                f"{path} {type_name}" for path, type_name in self.type_hints.items()
            )

        if self.skip_hints:
            hints.extend(f"SKIP {path}" for path in self.skip_hints)

        if self.skip_regexp_hints:
            hints.extend(
                f"SKIP REGEXP '{pattern}'" for pattern in self.skip_regexp_hints
            )

        return f"{self.name} JSON({', '.join(hints)})"


@TestStep(Given)
def create_table_with_json_column(
    self, table_name=None, column_description=None, node=None
):
    """Create a table with one column of JSON type."""

    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = f"table_{getuid()}"

    try:
        node.query(
            f"""
            SET enable_json_type=1;
            CREATE TABLE {table_name} ({column_description})
            ENGINE = MergeTree 
            ORDER BY tuple();
            """
        )
        yield table_name

    finally:
        with Finally("drop table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestStep(Given)
def insert_json_to_table(
    self, table_name, json_object, column_name="json_col", node=None
):
    """Insert a JSON object into a table with a JSON column."""

    if node is None:
        node = self.context.node

    json_str = json.dumps(json_object, ensure_ascii=False).replace('"', '\\"')

    node.query(
        f"""
        INSERT INTO {table_name} ({column_name}) 
        VALUES ('{json_str}')
        """
    )
