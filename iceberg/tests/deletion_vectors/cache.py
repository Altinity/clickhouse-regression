"""Puffin files cache: session/server settings, invalidation, eviction,
DROP statement, RBAC, observability, concurrency, and entry isolation.

All profile events are read from system.query_log per log_comment so
concurrent activity cannot perturb the counts. Cache requirements are
verified on S3 (MinIO) storage; local files have no etag and are cached
by the remaining key components (EtagBypass)."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

from helpers.common import getuid
from helpers.config import config_d

import iceberg.tests.steps.spark as spark
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.puffin as puffin
import iceberg.tests.deletion_vectors.steps.manifest as manifest
import iceberg.tests.deletion_vectors.steps.local_clone as local_clone

DEFAULT_SERVER_SETTINGS = {
    "puffin_files_cache_policy": "SLRU",
    "puffin_files_cache_size": "536870912",
    "puffin_files_cache_max_entries": "5000",
    "puffin_files_cache_size_ratio": "0.5",
}


def expected_count(rows=100, step=10):
    """Surviving row count of the fixture default: *rows* rows with every
    *step*-th id deleted."""
    return len(common.expected_ids(rows, range(0, rows, step)))


@TestStep(When)
def cold_read(self, table, node=None, extra_settings=None):
    """Drop the Puffin cache and read the table once; returns the
    log_comment of the read."""
    common.drop_puffin_cache(node=node)
    log_comment = common.unique_log_comment("cold")
    settings = [("log_comment", log_comment)] + list(extra_settings or [])
    common.read_result(table=table, columns="count()", node=node, settings=settings)
    return log_comment


@TestStep(When)
def warm_read(self, table, node=None, extra_settings=None):
    """Read the table once without touching the cache; returns the
    log_comment of the read."""
    log_comment = common.unique_log_comment("warm")
    settings = [("log_comment", log_comment)] + list(extra_settings or [])
    common.read_result(table=table, columns="count()", node=node, settings=settings)
    return log_comment


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Setting("1.0"))
def setting(self):
    """use_puffin_files_cache defaults to 1; with the cache on, repeated
    reads are served from cache; with it off, every read re-fetches."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with And("the setting exists with default 1"):
        result = self.context.node.query(
            "SELECT value FROM system.settings "
            "WHERE name = 'use_puffin_files_cache' FORMAT TabSeparated"
        )
        assert result.output.strip() == "1", error(
            f"use_puffin_files_cache default is {result.output.strip()!r}"
        )

    with When("a cold read populates the cache"):
        cold_comment = cold_read(table=table)

    with Then("the cold read fetched the Puffin file"):
        events = common.get_puffin_events(log_comment=cold_comment)
        assert events["PuffinFilesRead"] > 0, error(f"cold read events: {events}")

    with When("the table is read again"):
        warm_comment = warm_read(table=table)

    with Then("the repeated query is served from cache"):
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(f"warm events: {events}")
        assert events["PuffinFilesRead"] == 0, error(f"warm events: {events}")

    with When("the cache is disabled by session setting"):
        disabled = [("use_puffin_files_cache", "0")]
        first = warm_read(table=table, extra_settings=disabled)
        second = warm_read(table=table, extra_settings=disabled)

    with Then("every read re-fetches and re-parses the vector"):
        for log_comment in (first, second):
            events = common.get_puffin_events(log_comment=log_comment)
            assert events["PuffinFilesRead"] > 0, error(
                f"read {log_comment} did not re-fetch: {events}"
            )

    with And("results stay correct with the cache off"):
        count = common.count_rows(
            table=table, settings=[("use_puffin_files_cache", "0")]
        )
        assert count == expected_count(), error(f"count = {count}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_ServerSettings("1.0"))
def server_settings(self):
    """The cache server settings exist with documented defaults, the cache
    can be disabled by server setting, and the size is changeable without a
    restart."""
    node = self.context.node

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with Then("the cache server settings exist with documented defaults"):
        for name, expected in DEFAULT_SERVER_SETTINGS.items():
            result = node.query(
                f"SELECT value FROM system.server_settings "
                f"WHERE name = '{name}' FORMAT TabSeparated"
            )
            assert result.output.strip() == expected, error(
                f"{name} = {result.output.strip()!r}, expected {expected!r}"
            )

    with When("the cache is disabled by server setting without a restart"):
        config_d.create_and_add(
            entries={"puffin_files_cache_size": "0"},
            config_file="puffin_cache_disabled.xml",
            restart=False,
            node=node,
        )
        node.query("SYSTEM RELOAD CONFIG")

    with Then("results remain correct even with use_puffin_files_cache = 1"):
        count = common.count_rows(
            table=table, settings=[("use_puffin_files_cache", "1")], node=node
        )
        assert count == expected_count(), error(f"count = {count}")

    with And("the live value is reported without a restart"):
        result = node.query(
            "SELECT value, changed FROM system.server_settings "
            "WHERE name = 'puffin_files_cache_size' FORMAT TabSeparated"
        )
        value, changed = result.output.split()
        assert value == "0" and changed == "1", error(
            f"live puffin_files_cache_size: value={value}, changed={changed}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Invalidation("1.0"))
def invalidation(self):
    """The cache never serves a stale vector: new commits use new Puffin
    paths, and replaced object content changes the etag part of the key —
    SYSTEM DROP PUFFIN FILES CACHE is never needed for correctness."""
    rows = 100

    with Given("a table with a cached deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )
        common.assert_visible_ids(
            table=table, ids=common.expected_ids(rows, range(0, rows, 10))
        )

    with When("a new commit produces a new Puffin path"):
        puffin_before = set(
            s3_objects.find_puffin_keys(table.namespace, table.table_name)
        )
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id IN (5, 15)",
        )
        puffin_after = set(
            s3_objects.find_puffin_keys(table.namespace, table.table_name)
        )
        assert puffin_after - puffin_before, error(
            "the new commit did not produce a new Puffin file"
        )

    with Then("the next read observes the new vector without any drop"):
        absent = set(range(0, rows, 10)) | {5, 15}
        common.assert_visible_ids(
            table=table, ids=[i for i in range(rows) if i not in absent]
        )

    with When(
        "the Puffin object is replaced in place with different content "
        "of identical shape (same offsets, length, and cardinality)"
    ):
        # deletes ids 3,13,...,93 instead — same count, same blob size,
        # so the manifest entry is unchanged and only the etag differs
        replaced = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )
        # the crafted replacement positions equal row ids only for a
        # single data file written in insertion order
        common.assert_data_file_count(table=replaced, count=1)
        common.assert_visible_ids(
            table=replaced, ids=common.expected_ids(rows, range(0, rows, 10))
        )
        manifest.replace_deletion_vector(
            namespace=replaced.namespace,
            table_name=replaced.table_name,
            payload=puffin.build_dv_payload(positions=list(range(3, rows, 10))),
        )

    with Then("the changed etag yields a fresh load, not the cached vector"):
        common.assert_visible_ids(
            table=replaced,
            ids=[i for i in range(rows) if i % 10 != 3],
            settings=common.FRESH_READ_SETTINGS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_EtagBypass("1.0"))
def etag_bypass(self):
    """The absence of an etag does not break the cache: local-filesystem
    objects are cached keyed by the remaining components (storage identity,
    path, blob offset and length, referenced data file, cardinalities), so
    a repeated read of the same local table is a warm hit with the same
    correct result."""
    rows = 60
    deleted = list(range(0, rows, 4))
    expected = common.expected_ids(rows, deleted)

    with Given("a local-filesystem clone of a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 4 = 0"
        )
        local_dir = local_clone.clone_table_to_local(table=table)

    with When("the local table is read from a cold cache"):
        common.drop_puffin_cache()
        cold_comment = common.unique_log_comment("local_cold")
        ids = local_clone.read_local_ids(local_dir=local_dir, log_comment=cold_comment)
        assert ids == expected, error(f"cold local read returned {len(ids)} rows")

    with Then("the cold read fetched the Puffin file"):
        events = common.get_puffin_events(log_comment=cold_comment)
        assert events["PuffinFilesRead"] > 0, error(f"cold local read: {events}")

    with When("the local table is read again"):
        warm_comment = common.unique_log_comment("local_warm")
        ids = local_clone.read_local_ids(local_dir=local_dir, log_comment=warm_comment)
        assert ids == expected, error(f"warm local read returned {len(ids)} rows")

    with Then("the warm read is served from the cache despite the missing etag"):
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(f"warm local read: {events}")
        assert events["PuffinFilesRead"] == 0, error(f"warm local read: {events}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Eviction("1.0"))
def eviction_under_pressure(self):
    """A cache smaller than the working set evicts entries while results
    remain correct."""
    node = self.context.node

    with Given("the cache is limited to a single entry"):
        config_d.create_and_add(
            entries={"puffin_files_cache_max_entries": "1"},
            config_file="puffin_cache_one_entry.xml",
            restart=False,
            node=node,
        )
        node.query("SYSTEM RELOAD CONFIG")

    rows = 50

    with And("two tables with deletion vectors"):
        table1 = common.table_with_deletion_vectors(rows=rows)
        table2 = common.table_with_deletion_vectors(rows=rows)

    with When("both vectors are read alternately from a cold cache"):
        common.drop_puffin_cache(node=node)
        log_comment = common.unique_log_comment("evict")
        for _ in range(2):
            for table in (table1, table2):
                count = common.count_rows(
                    table=table,
                    node=node,
                    settings=[("log_comment", log_comment)],
                )
                assert count == expected_count(rows), error(f"count = {count}")

    with Then("entries were evicted while results stayed correct"):
        weight_lost = metrics.get_profile_event(
            event="PuffinFilesCacheWeightLost", log_comment=log_comment, node=node
        )
        assert weight_lost > 0, error(
            f"PuffinFilesCacheWeightLost = {weight_lost}, expected evictions"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Eviction("1.0"))
def empty_vector_cached(self):
    """Empty vectors are cached as explicit entries."""
    node = self.context.node

    with Given("a table whose vector is replaced with an empty one"):
        table = common.table_with_deletion_vectors(rows=50)
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=[]),
            declared_cardinality=0,
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache(node=node)

    with When("the empty vector is read twice"):
        settings = common.FRESH_READ_SETTINGS
        first = warm_read(table=table, node=node, extra_settings=settings)
        second = warm_read(table=table, node=node, extra_settings=settings)

    with Then("the second read hits the cached empty entry"):
        events = common.get_puffin_events(log_comment=second, node=node)
        assert events["PuffinFilesCacheHits"] > 0, error(
            f"empty vector was not cached: {events}"
        )
        assert events["PuffinFilesRead"] == 0, error(
            f"empty vector was re-read: {events}"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Eviction("1.0"))
def eviction(self):
    """Eviction under a small cache and explicit caching of empty
    vectors."""
    Scenario(run=eviction_under_pressure)
    Scenario(run=empty_vector_cached)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_DropStatement("1.0"))
def drop_statement(self):
    """SYSTEM DROP PUFFIN FILES CACHE clears the cache: the next query
    records misses and re-reads, with an unchanged result."""
    with Given("a table with a warm Puffin cache"):
        table = common.table_with_deletion_vectors()
        cold_read(table=table)
        warm_comment = warm_read(table=table)
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(
            f"cache was not warm: {events}"
        )

    with When("the cache is dropped"):
        self.context.node.query("SYSTEM DROP PUFFIN FILES CACHE")

    with Then("the next query records misses and re-reads the Puffin file"):
        after_comment = warm_read(table=table)
        events = common.get_puffin_events(log_comment=after_comment)
        assert events["PuffinFilesCacheMisses"] > 0, error(f"events: {events}")
        assert events["PuffinFilesRead"] > 0, error(f"events: {events}")

    with And("the logical result is unchanged"):
        assert common.count_rows(table=table) == expected_count(), error()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_RBAC("1.0"))
def rbac(self):
    """SYSTEM DROP PUFFIN FILES CACHE requires its named privilege, the
    parent SYSTEM DROP CACHE suffices, and SHOW PRIVILEGES lists it."""
    node = self.context.node
    user = f"puffin_user_{getuid()}"

    try:
        with Given("a user with no SYSTEM privileges"):
            node.query(f"CREATE USER {user}")

        with Then("the drop statement is denied"):
            common.assert_query_error(
                query="SYSTEM DROP PUFFIN FILES CACHE",
                error_name="ACCESS_DENIED",
                settings=[("user", user)],
            )

        with When("the specific privilege is granted"):
            node.query(f"GRANT SYSTEM DROP PUFFIN FILES CACHE ON *.* TO {user}")

        with Then("the drop statement is allowed"):
            node.query("SYSTEM DROP PUFFIN FILES CACHE", settings=[("user", user)])

        with When("the specific privilege is replaced by the parent one"):
            node.query(f"REVOKE SYSTEM DROP PUFFIN FILES CACHE ON *.* FROM {user}")
            node.query(f"GRANT SYSTEM DROP CACHE ON *.* TO {user}")

        with Then("the parent SYSTEM DROP CACHE privilege suffices"):
            node.query("SYSTEM DROP PUFFIN FILES CACHE", settings=[("user", user)])

        with When("the parent privilege is replaced by the underscore spelling"):
            node.query(f"REVOKE SYSTEM DROP CACHE ON *.* FROM {user}")
            node.query(f"GRANT SYSTEM DROP PUFFIN_FILES_CACHE ON *.* TO {user}")

        with Then("both statement spellings are allowed under it"):
            node.query("SYSTEM DROP PUFFIN FILES CACHE", settings=[("user", user)])
            node.query("SYSTEM DROP PUFFIN_FILES_CACHE", settings=[("user", user)])

        with And("SHOW PRIVILEGES lists the privilege with its parent"):
            result = node.query(
                "SELECT parent_group FROM system.privileges "
                "WHERE privilege = 'SYSTEM DROP PUFFIN FILES CACHE' "
                "FORMAT TabSeparated"
            )
            assert result.output.strip() == "SYSTEM DROP CACHE", error(
                f"privilege listing: {result.output!r}"
            )

    finally:
        with Finally("drop the user"):
            node.query(f"DROP USER IF EXISTS {user}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Observability("1.0"))
def observability(self):
    """Cold reads increase misses/reads with non-zero read time, warm reads
    increase hits with zero reads, and the asynchronous metrics reflect the
    resident entries."""
    node = self.context.node

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with When("the table is read from a cold cache"):
        cold_comment = cold_read(table=table)

    with Then("misses and reads increased and read time is non-zero"):
        events = common.get_puffin_events(log_comment=cold_comment)
        assert events["PuffinFilesCacheMisses"] > 0, error(f"cold: {events}")
        assert events["PuffinFilesRead"] > 0, error(f"cold: {events}")
        assert events["PuffinFileReadMicroseconds"] > 0, error(f"cold: {events}")

    with And("the cache metrics reflect the resident entries"):
        # the cache registers PuffinFilesCacheBytes/Files as CurrentMetrics
        # (system.metrics), not asynchronous metrics
        for retry in retries(count=15, delay=1):
            with retry:
                cache_bytes = metrics.get_current_metric(
                    metric="PuffinFilesCacheBytes", node=node
                )
                cache_files = metrics.get_current_metric(
                    metric="PuffinFilesCacheFiles", node=node
                )
                assert cache_bytes > 0 and cache_files > 0, (
                    f"PuffinFilesCacheBytes={cache_bytes}, "
                    f"PuffinFilesCacheFiles={cache_files}"
                )

    with When("the table is read warm"):
        warm_comment = warm_read(table=table)

    with Then("hits increased and PuffinFilesRead stayed at 0"):
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(f"warm: {events}")
        assert events["PuffinFilesRead"] == 0, error(f"warm: {events}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Concurrency("1.0"))
def concurrency(self):
    """Two concurrent queries over the same cold vector both return correct
    results with a single load, and a racing cache drop never produces a
    wrong result.

    Concurrency comes from background clickhouse-client processes
    (common.run_queries_in_parallel), not a TestFlows Pool — executor
    teardown deterministically segfaults the stock python 3.12.3
    interpreter. The scheduler may still serialize the two queries, in
    which case the assertion degrades to "the second query was served from
    cache" — both orderings satisfy the single-load requirement."""
    rows = 100

    with Given("a table with a cold deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)
        common.drop_puffin_cache()

    log_comments = [common.unique_log_comment(f"conc{i}") for i in range(2)]

    def count_query(log_comment):
        return (
            f"SELECT count() FROM {table.sql_expr()} "
            f"SETTINGS log_comment = '{log_comment}'"
        )

    with When("two queries read the cold vector concurrently"):
        outputs = common.run_queries_in_parallel(
            queries=[count_query(log_comment) for log_comment in log_comments]
        )

    with Then("both returned the correct result"):
        assert outputs == [str(expected_count(rows))] * 2, error(
            f"concurrent outputs: {outputs}"
        )

    with And("the vector was loaded exactly once across both queries"):
        # a single load counts 2 PuffinFilesRead events (footer parse +
        # blob read), so exactly one load across both queries totals 2
        total_reads = sum(
            metrics.get_profile_event(event="PuffinFilesRead", log_comment=lc)
            for lc in log_comments
        )
        assert total_reads == 2, error(
            f"PuffinFilesRead totals {total_reads} across both queries, "
            f"expected 2 (one load)"
        )

    with When("a cache drop repeatedly races an in-flight cold load"):
        # a single attempt may not overlap; repeating the race makes an
        # actual drop-during-load overlap likely
        for attempt in range(3):
            common.drop_puffin_cache()
            race_comment = common.unique_log_comment(f"race{attempt}")
            outputs = common.run_queries_in_parallel(
                queries=[
                    count_query(race_comment),
                    "SYSTEM DROP PUFFIN FILES CACHE",
                ]
            )
            assert outputs[0] == str(expected_count(rows)), error(
                f"attempt {attempt}: read racing a drop returned {outputs[0]!r}"
            )

    with Then("a final cold read still returns the correct result"):
        assert common.count_rows(table=table) == expected_count(rows), error()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_EntryIsolation("1.0"))
def entry_isolation(self):
    """Concurrent queries with different filters over the same cached
    vector each return the same result as the equivalent single query — a
    hit returns a copy, so no query can mutate another's cached state."""
    rows = 100
    deleted = set(range(0, rows, 10))

    with Given("a table with a warm deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)
        cold_read(table=table)

    filters = {
        "id % 2 = 0": [i for i in range(rows) if i not in deleted and i % 2 == 0],
        "id % 2 = 1": [i for i in range(rows) if i not in deleted and i % 2 == 1],
        "id < 50": [i for i in range(rows) if i not in deleted and i < 50],
        "id >= 50": [i for i in range(rows) if i not in deleted and i >= 50],
    }

    with When("many concurrent filtered queries share the cached vector"):
        outputs = common.run_queries_in_parallel(
            queries=[
                f"SELECT id FROM {table.sql_expr()} "
                f"WHERE {where_clause} ORDER BY id"
                for where_clause in filters
            ]
        )

    with Then("each returns the same rows as the equivalent single query"):
        for (where_clause, expected), output in zip(filters.items(), outputs):
            ids = [int(line) for line in output.split() if line.strip()]
            assert ids == expected, error(
                f"filter {where_clause!r} returned {len(ids)} rows, "
                f"expected {len(expected)}"
            )


def snapshot_settings(snapshot):
    return [("iceberg_snapshot_id", str(snapshot["snapshot-id"]))]


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_SnapshotScopedEntries("1.0"))
def time_travel_between_snapshots(self):
    """Time travel with a warm cache: the cached vector of one snapshot is
    never applied to another snapshot's read, and revisiting an
    already-read snapshot is served from the cache — an entry of an
    immutable snapshot never needs invalidation."""
    rows = 100
    deleted = list(range(0, rows, 10))
    expected_b = common.expected_ids(rows, deleted)

    with Given("snapshot A inserts 100 rows, snapshot B deletes 10 via a vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )
        snapshots = s3_objects.get_snapshots(table.namespace, table.table_name)
        assert len(snapshots) == 2, error(f"expected 2 snapshots, got {len(snapshots)}")
        snapshot_a, snapshot_b = snapshots

    with When("a cold read of snapshot B caches its vector"):
        common.drop_puffin_cache()
        cold_comment = common.unique_log_comment("ttw_cold")
        result = common.read_result(
            table=table, columns="id", order_by="id", log_comment=cold_comment
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected_b, error(f"snapshot B returned {len(ids)} rows")
        events = common.get_puffin_events(log_comment=cold_comment)
        assert events["PuffinFilesRead"] > 0, error(f"cold read: {events}")

    with Then("a warm time travel to snapshot A does not apply the cached vector"):
        a_comment = common.unique_log_comment("ttw_a")
        result = common.read_result(
            table=table,
            columns="id",
            order_by="id",
            log_comment=a_comment,
            settings=snapshot_settings(snapshot_a),
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == list(range(rows)), error(
            f"snapshot A returned {len(ids)} rows — a warm vector from "
            f"snapshot B leaked into an earlier snapshot's read"
        )

    with And("snapshot A's read touched no Puffin file at all"):
        events = common.get_puffin_events(log_comment=a_comment)
        assert events["PuffinFilesRead"] == 0, error(f"snapshot A read: {events}")

    with And("revisiting snapshot B is served from the cache"):
        b_comment = common.unique_log_comment("ttw_b")
        result = common.read_result(
            table=table,
            columns="id",
            order_by="id",
            log_comment=b_comment,
            settings=snapshot_settings(snapshot_b),
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected_b, error(f"snapshot B revisit returned {len(ids)} rows")
        events = common.get_puffin_events(log_comment=b_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(f"B revisit: {events}")
        assert events["PuffinFilesRead"] == 0, error(f"B revisit: {events}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_SnapshotScopedEntries("1.0"))
def shared_file_blob_entries(self):
    """Two blobs of the same Puffin file are independent cache entries: a
    warm read applies each cached vector only to its own data file. If the
    entry key ignored the blob offset, the second blob's load would be
    served the first blob's vector and the row set would be wrong."""
    with Given(
        "a table with two data files and one DELETE producing vectors "
        "for both in a single commit"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[
                common.insert_range_statement(100),
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(100)",
                "DELETE FROM {table} WHERE id % 10 = 0",
            ],
        )

    deleted = list(range(0, 200, 10))
    expected = common.expected_ids(200, deleted)

    with And("both vectors live at distinct offsets of one Puffin file"):
        puffin_keys = s3_objects.find_puffin_keys(
            namespace=table.namespace, table_name=table.table_name
        )
        assert len(puffin_keys) == 1, error(
            f"expected one shared Puffin file, found {puffin_keys}"
        )
        dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
        offsets = {
            entry["entry"]["data_file"]["content_offset"] for entry in dv_entries
        }
        assert len(offsets) == 2, error(
            f"expected 2 distinct blob offsets, found {sorted(offsets)}"
        )

    with When("a cold read loads and caches both blobs"):
        common.drop_puffin_cache()
        common.assert_visible_ids(table=table, ids=expected)

    with Then("a warm read applies each cached blob to its own file only"):
        warm_comment = common.unique_log_comment("shared_warm")
        result = common.read_result(
            table=table, columns="id", order_by="id", log_comment=warm_comment
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected, error(
            f"warm read returned {len(ids)} rows — cached blobs of the same "
            f"Puffin file cross-contaminated"
        )
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] >= 2, error(f"warm read: {events}")
        assert events["PuffinFilesRead"] == 0, error(f"warm read: {events}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_SnapshotScopedEntries("1.0"))
def unrelated_commit_keeps_entries(self):
    """A commit that does not change existing vectors (an insert of new
    rows) keeps them warm: the next read of the new snapshot is served from
    the existing entries without re-fetching the unchanged Puffin file."""
    rows = 100

    with Given("a table with a warm deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)
        cold_read(table=table)

    with When("Spark commits an insert that touches no vector"):
        spark.insert_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            values="(1000, 'late'), (1001, 'late')",
        )

    with Then("the next read sees the new snapshot from the warm entries"):
        after_comment = common.unique_log_comment("keep_warm")
        result = common.read_result(
            table=table, columns="count()", log_comment=after_comment
        )
        count = int(result.output.strip())
        assert count == expected_count(rows) + 2, error(f"count = {count}")
        events = common.get_puffin_events(log_comment=after_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(f"post-insert: {events}")
        assert events["PuffinFilesRead"] == 0, error(
            f"post-insert read re-fetched an unchanged Puffin file: {events}"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_Cache_SnapshotScopedEntries("1.0"))
def snapshot_scoped_entries(self):
    """Snapshot immutability makes cached vectors snapshot-scoped: warm
    time travel, independent blob entries, and entries surviving unrelated
    commits."""
    Scenario(run=time_travel_between_snapshots)
    Scenario(run=shared_file_blob_entries)
    Scenario(run=unrelated_commit_keeps_entries)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_RevalidationNotBypassed("1.0"))
def revalidation_not_bypassed(self):
    """A warm cache never lets a read skip metadata validation: when the
    manifest declares a different cardinality for the same blob, the next
    read fails with the validation error a cold read produces — it is not
    served the previously cached vector. The Puffin cache is deliberately
    NOT dropped after the corruption."""
    rows = 100

    with Given("a table with a warm deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)
        cold_read(table=table)
        warm_comment = warm_read(table=table)
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] > 0, error(
            f"cache was not warm: {events}"
        )

    with When("the manifest declares a different cardinality for the same blob"):

        def lower_record_count(entry):
            entry["data_file"]["record_count"] = 7
            return entry

        manifest.mutate_manifest_entries(
            namespace=table.namespace,
            table_name=table.table_name,
            mutator=lower_record_count,
            content=manifest.MANIFEST_LIST_DELETES,
        )
        common.drop_iceberg_metadata_cache()

    with Then("the next read fails with the validation error, not a warm hit"):
        common.assert_query_error(
            query=f"SELECT * FROM {table.sql_expr()} FORMAT Null",
            error_name="BAD_ARGUMENTS",
            message_fragment="does not match expected cardinality",
            settings=list(common.FRESH_READ_SETTINGS),
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_ServerSettings("1.0"))
def max_entries_unlimited(self):
    """puffin_files_cache_max_entries = 0 means no limit on the number of
    entries, not disabled: vectors are still cached and served warm."""
    node = self.context.node
    rows = 50

    with Given("the entry limit is set to zero"):
        config_d.create_and_add(
            entries={"puffin_files_cache_max_entries": "0"},
            config_file="puffin_cache_zero_entries.xml",
            restart=False,
            node=node,
        )
        node.query("SYSTEM RELOAD CONFIG")

    with And("two tables with deletion vectors"):
        table1 = common.table_with_deletion_vectors(rows=rows)
        table2 = common.table_with_deletion_vectors(rows=rows)

    with When("both tables are read from a cold cache"):
        common.drop_puffin_cache(node=node)
        for table in (table1, table2):
            count = common.count_rows(table=table, node=node)
            assert count == expected_count(rows), error(f"count = {count}")

    with Then("both vectors are served warm — zero is unlimited, not disabled"):
        for table in (table1, table2):
            warm_comment = warm_read(table=table, node=node)
            events = common.get_puffin_events(log_comment=warm_comment, node=node)
            assert events["PuffinFilesCacheHits"] > 0, error(
                f"vector was not cached with max_entries = 0: {events}"
            )
            assert events["PuffinFilesRead"] == 0, error(
                f"vector was re-read with max_entries = 0: {events}"
            )


@TestFeature
@Name("cache")
def feature(self, minio_root_user, minio_root_password):
    """Puffin files cache."""
    Scenario(run=setting)
    Scenario(run=server_settings)
    Scenario(run=max_entries_unlimited)
    Scenario(run=invalidation)
    Scenario(run=etag_bypass)
    Suite(run=eviction)
    Suite(run=snapshot_scoped_entries)
    Scenario(run=revalidation_not_bypassed)
    Scenario(run=drop_statement)
    Scenario(run=rbac)
    Scenario(run=observability)
    Scenario(run=entry_isolation)
    Scenario(run=concurrency)
