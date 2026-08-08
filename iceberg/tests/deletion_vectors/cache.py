"""Puffin files cache: session/server settings, invalidation, eviction,
DROP statement, RBAC, observability, concurrency, and entry isolation.

All profile events are read from system.query_log per log_comment so
concurrent activity cannot perturb the counts. Cache requirements are
verified on S3 (MinIO) storage; local files have no etag and bypass the
cache (EtagBypass)."""

import threading

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
        assert count == 90, error(f"count = {count}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_ServerSettings("1.0"))
def server_settings(self):
    """The cache server settings exist with documented defaults, the cache
    can be disabled by server setting, and the size is changeable without a
    restart."""
    node = self.context.node

    with Check("documented defaults"):
        for name, expected in DEFAULT_SERVER_SETTINGS.items():
            result = node.query(
                f"SELECT value FROM system.server_settings "
                f"WHERE name = '{name}' FORMAT TabSeparated"
            )
            assert result.output.strip() == expected, error(
                f"{name} = {result.output.strip()!r}, expected {expected!r}"
            )

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with When("the cache is disabled by server setting without a restart"):
        config_d.create_and_add(
            entries={"puffin_files_cache_size": "0"},
            config_file="puffin_cache_disabled.xml",
            restart=False,
            node=node,
        )
        node.query("SYSTEM RELOAD CONFIG")

    with Then(
        "results remain correct even with use_puffin_files_cache = 1"
    ):
        count = common.count_rows(
            table=table, settings=[("use_puffin_files_cache", "1")], node=node
        )
        assert count == 90, error(f"count = {count}")

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
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_EtagBypass("1.0"))
def etag_bypass(self):
    """Objects without an etag (local filesystem) bypass the cache: results
    stay correct and PuffinFilesCacheHits stays 0."""
    rows = 60
    deleted = list(range(0, rows, 4))

    with Given("a local-filesystem clone of a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 4 = 0"
        )
        local_dir = local_clone.clone_table_to_local(table=table)

    expected = common.expected_ids(rows, deleted)

    with When("the local table is read twice"):
        log_comments = []
        for _ in range(2):
            log_comment = common.unique_log_comment("local")
            ids = local_clone.read_local_ids(
                local_dir=local_dir, log_comment=log_comment
            )
            assert ids == expected, error(f"local read returned {len(ids)} rows")
            log_comments.append(log_comment)

    with Then("no read was served from the Puffin cache"):
        for log_comment in log_comments:
            events = common.get_puffin_events(log_comment=log_comment)
            assert events["PuffinFilesCacheHits"] == 0, error(
                f"local read hit the cache: {events}"
            )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Eviction("1.0"))
def eviction(self):
    """A cache smaller than the working set evicts entries while results
    remain correct; empty vectors are cached as explicit entries."""
    node = self.context.node

    with Given("the cache is limited to a single entry"):
        config_d.create_and_add(
            entries={"puffin_files_cache_max_entries": "1"},
            config_file="puffin_cache_one_entry.xml",
            restart=False,
            node=node,
        )
        node.query("SYSTEM RELOAD CONFIG")

    with And("two tables with deletion vectors"):
        table1 = common.table_with_deletion_vectors(rows=50)
        table2 = common.table_with_deletion_vectors(rows=50)

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
                assert count == 45, error(f"count = {count}")

    with Then("entries were evicted while results stayed correct"):
        weight_lost = metrics.get_profile_event(
            event="PuffinFilesCacheWeightLost", log_comment=log_comment, node=node
        )
        assert weight_lost > 0, error(
            f"PuffinFilesCacheWeightLost = {weight_lost}, expected evictions"
        )

    with Check("empty vectors are cached as explicit entries"):
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
            settings = [("use_iceberg_metadata_files_cache", "0")]
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
        assert common.count_rows(table=table) == 90, error()


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
            node.query(
                "SYSTEM DROP PUFFIN FILES CACHE", settings=[("user", user)]
            )

        with When("the specific privilege is replaced by the parent one"):
            node.query(f"REVOKE SYSTEM DROP PUFFIN FILES CACHE ON *.* FROM {user}")
            node.query(f"GRANT SYSTEM DROP CACHE ON *.* TO {user}")

        with Then("the parent SYSTEM DROP CACHE privilege suffices"):
            node.query(
                "SYSTEM DROP PUFFIN FILES CACHE", settings=[("user", user)]
            )

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

    with And("the asynchronous metrics reflect the resident entries"):
        for retry in retries(count=15, delay=1):
            with retry:
                cache_bytes = metrics.get_asynchronous_metric(
                    metric="PuffinFilesCacheBytes", node=node
                )
                cache_files = metrics.get_asynchronous_metric(
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
    wrong result."""
    rows = 100
    expected_count = 90

    with Given("a table with a cold deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)
        common.drop_puffin_cache()

    log_comments = [common.unique_log_comment(f"conc{i}") for i in range(2)]

    @TestStep(When)
    def read_with_comment(self, log_comment, barrier=None):
        # the barrier aligns the query starts so both are as close to the
        # same cold load as an external test can force; the scheduler may
        # still serialize them, in which case the assertion degrades to
        # "the second query was served from cache" — both satisfy the
        # single-load requirement
        if barrier is not None:
            barrier.wait(timeout=60)
        count = common.count_rows(
            table=table, settings=[("log_comment", log_comment)]
        )
        assert count == expected_count, error(f"count = {count}")

    with When("two queries read the cold vector concurrently"):
        barrier = threading.Barrier(2)
        with Pool(2) as pool:
            for log_comment in log_comments:
                When(
                    f"concurrent read {log_comment}",
                    test=read_with_comment,
                    parallel=True,
                    executor=pool,
                )(log_comment=log_comment, barrier=barrier)
            join()

    with Then("the vector was loaded exactly once across both queries"):
        total_reads = sum(
            metrics.get_profile_event(event="PuffinFilesRead", log_comment=lc)
            for lc in log_comments
        )
        assert total_reads == 1, error(
            f"PuffinFilesRead totals {total_reads} across both queries, "
            f"expected 1"
        )

    with When("a cache drop repeatedly races an in-flight load"):

        @TestStep(When)
        def racing_drop(self, barrier):
            barrier.wait(timeout=60)
            common.drop_puffin_cache()

        # a single attempt may not overlap; repeating the race makes an
        # actual drop-during-load overlap likely
        for attempt in range(3):
            common.drop_puffin_cache()
            race_comment = common.unique_log_comment(f"race{attempt}")
            race_barrier = threading.Barrier(2)
            with Pool(2) as pool:
                When(
                    f"read during drop, attempt {attempt}",
                    test=read_with_comment,
                    parallel=True,
                    executor=pool,
                )(log_comment=race_comment, barrier=race_barrier)
                When(
                    f"drop during read, attempt {attempt}",
                    test=racing_drop,
                    parallel=True,
                    executor=pool,
                )(barrier=race_barrier)
                join()

    with Then("the racing queries all returned the correct result"):
        # correctness was asserted inside every read; verify once more cold
        assert common.count_rows(table=table) == expected_count, error()


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

    @TestStep(When)
    def filtered_read(self, where_clause, expected):
        ids = common.select_ids(table=table, where_clause=where_clause)
        assert ids == expected, error(
            f"filter {where_clause!r} returned {len(ids)} rows, "
            f"expected {len(expected)}"
        )

    with When("many concurrent filtered queries share the cached vector"):
        with Pool(4) as pool:
            for where_clause, expected in filters.items():
                When(
                    f"filtered read {where_clause}",
                    test=filtered_read,
                    parallel=True,
                    executor=pool,
                )(where_clause=where_clause, expected=expected)
            join()


@TestFeature
@Name("cache")
def feature(self, minio_root_user, minio_root_password):
    """Puffin files cache."""
    Scenario(test=setting, flags=TE)()
    Scenario(test=server_settings, flags=TE)()
    Scenario(test=invalidation, flags=TE)()
    Scenario(test=etag_bypass, flags=TE)()
    Scenario(test=eviction, flags=TE)()
    Scenario(test=drop_statement, flags=TE)()
    Scenario(test=rbac, flags=TE)()
    Scenario(test=observability, flags=TE)()
    Scenario(test=concurrency, flags=TE)()
    Scenario(test=entry_isolation, flags=TE)()
