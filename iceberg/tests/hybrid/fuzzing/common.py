"""Shared harness for Hybrid query fuzzing (curated + upstream-derived)."""

import os

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table_as_select

import swarms.tests.steps.swarm_steps as swarm_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.hybrid as hybrid_steps


def load_queries_from_sql_file(sql_file_path):
    """Load SQL queries from a file; blocks are separated by blank lines."""
    with open(sql_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    queries = []
    for query_block in content.split("\n\n"):
        lines = [
            line
            for line in query_block.split("\n")
            if line.strip() and not line.strip().startswith("--")
        ]
        if lines:
            query = "\n".join(lines).strip()
            if query:
                queries.append(query)
    return queries


def substitute_table_names(query, substitutions):
    """Replace placeholders in a SQL template."""
    result = query
    for placeholder, value in substitutions.items():
        result = result.replace(placeholder, value)
    return result


def sql_path(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


@TestStep(Given)
def create_mt_iceberg_cluster_fuzz_hybrid(
    self,
    minio_root_user,
    minio_root_password,
    location_suffix="fuzz",
    row_count=100,
    node=None,
):
    """Iceberg (basic types) + MergeTree mirror + Hybrid remote(MT)+icebergCluster."""
    if node is None:
        node = self.context.node

    self.context.catalog = "rest"

    database_name = f"database_{getuid()}"
    location = f"s3://warehouse/data_hybrid_{location_suffix}"
    url = f"http://minio:9000/warehouse/data_hybrid_{location_suffix}"

    with By("create Iceberg table with basic types"):
        _, table_name, namespace = (
            swarm_steps.performance_iceberg_table_with_all_basic_data_types(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                s3_endpoint="http://localhost:9002",
                location=location,
                row_count=row_count,
            )
        )

    with By("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with By("create MergeTree mirror from Iceberg catalog table"):
        clickhouse_iceberg_table_name = (
            f"{database_name}.\\`{namespace}.{table_name}\\`"
        )
        merge_tree_table_name = f"merge_tree_table_{getuid()}"
        create_table_as_select(
            as_select_from=clickhouse_iceberg_table_name,
            table_name=merge_tree_table_name,
            partition_by="string_col",
        )

    with By("pick a watermark date from MergeTree"):
        date_value = node.query(
            f"SELECT date_col FROM {merge_tree_table_name} "
            f"WHERE date_col IS NOT NULL ORDER BY rand() LIMIT 1"
        ).output.strip()
        assert date_value, "expected at least one non-NULL date_col"

    with By("create Hybrid remote(MT) + icebergCluster"):
        hybrid_table_name = f"hybrid_table_{getuid()}"
        hybrid_steps.create_hybrid_table(
            table_name=hybrid_table_name,
            left_table_name=(
                f"remote('localhost', currentDatabase(), {merge_tree_table_name})"
            ),
            left_predicate=f"date_col <= '{date_value}'",
            right_table_name=(
                f"icebergCluster('replicated_cluster', '{url}', "
                f"'{minio_root_user}', '{minio_root_password}')"
            ),
            right_predicate=f"date_col > '{date_value}'",
        )

    return {
        "hybrid": hybrid_table_name,
        "merge_tree": merge_tree_table_name,
        "iceberg": clickhouse_iceberg_table_name,
        "date_value": date_value,
        "url": url,
    }


@TestStep(When)
def run_fuzz_queries(self, queries, substitutions, node=None, settings_suffix=""):
    """Run substituted queries; collect failures and hard-assert at the end."""
    if node is None:
        node = self.context.node

    failures = []

    with By(f"executing {len(queries)} fuzz queries"):
        for i, query_template in enumerate(queries, 1):
            query = substitute_table_names(query_template, substitutions)
            if settings_suffix and "SETTINGS" not in query.upper():
                query = f"{query.rstrip(';')} {settings_suffix}"
            with By(f"query {i}/{len(queries)}"):
                result = node.query(query, no_checks=True)
                if result.exitcode != 0:
                    output = (result.output or "").strip()
                    # Prefer the exception line when stdout also contains rows.
                    exc_line = next(
                        (
                            line.strip()
                            for line in output.splitlines()
                            if "DB::Exception" in line or "Code:" in line
                        ),
                        None,
                    )
                    snippet = (exc_line or output).replace("\n", " ")[:240]
                    note(f"query {i} failed (exit {result.exitcode}): {snippet}")
                    failures.append((i, snippet))

    with Then("all fuzz queries succeeded"):
        assert not failures, error(
            f"{len(failures)}/{len(queries)} fuzz queries failed: "
            + "; ".join(f"#{idx}: {msg}" for idx, msg in failures[:8])
            + (" ..." if len(failures) > 8 else "")
        )
