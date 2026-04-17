"""EXPORT PARTITION and KILL EXPORT PARTITION helpers for the iceberg suite.

Adapted from the s3 export_partition steps. The main adjustments are:

* Waiting for completion is optional (some scenarios need to observe a
  ``PENDING`` state first).
* Supports a list of destination tables per call (useful for fan-out tests).

The experimental feature is enabled server-side via
``configs/clickhouse/config.d/export_partition.xml``, so no per-query
settings are required unless a scenario explicitly exercises a tunable
(retries, TTL, etc.) through ``settings`` / ``extra_settings``.
"""

from testflows.core import *

from iceberg.tests.export_partition.steps.common import (
    get_partition_ids,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
)


@TestStep(When)
def export_partition(
    self,
    source_table,
    destination_table,
    partition_id,
    node=None,
    settings=None,
    extra_settings=None,
    exitcode=0,
    message=None,
    wait_for_completion=True,
    wait_timeout=120,
):
    """Run a single ``ALTER TABLE ... EXPORT PARTITION ID ... TO TABLE ...``.

    Args:
        source_table: ReplicatedMergeTree source.
        destination_table: Iceberg destination (either an IcebergS3 table or
            a DataLakeCatalog-backed table).
        partition_id: Partition ID string (as stored in ``system.parts``).
        settings: Full settings list passed directly to ``node.query``; the
            default ``None`` sends the statement without any per-query
            overrides.
        extra_settings: Appended to ``settings`` when ``settings`` is not
            provided; a convenient way to tweak one knob without rebuilding
            the whole list.
        exitcode: Expected exit code for the ``ALTER`` statement. Use ``0``
            (default) for success, or a specific code (e.g. ``36`` for
            ``BAD_ARGUMENTS``) to assert synchronous rejection.
        message: Expected substring in the error output. Typically set
            together with ``exitcode`` when asserting rejection.
        wait_for_completion: If ``True`` and no rejection is expected, block
            until the row in ``system.replicated_partition_exports`` reaches
            ``COMPLETED``.
    """
    if node is None:
        node = self.context.node

    if settings is None and extra_settings:
        settings = list(extra_settings)

    expect_failure = exitcode != 0 or message is not None

    with By(
        f"running EXPORT PARTITION id '{partition_id}' from "
        f"{source_table} to {destination_table}"
    ):
        result = node.query(
            f"ALTER TABLE {source_table} "
            f"EXPORT PARTITION ID '{partition_id}' "
            f"TO TABLE {destination_table}",
            settings=settings,
            exitcode=exitcode,
            message=message,
            ignore_exception=expect_failure,
        )

    if wait_for_completion and not expect_failure:
        with And(f"waiting for export of partition '{partition_id}' to complete"):
            wait_for_export_status(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                expected_status="COMPLETED",
                timeout=wait_timeout,
                node=node,
            )

    return result


@TestStep(When)
def export_all_partitions(
    self,
    source_table,
    destination_table,
    node=None,
    settings=None,
    extra_settings=None,
    wait_for_completion=True,
    wait_timeout=120,
):
    """Export every active partition of ``source_table`` sequentially.

    Returns the list of partition IDs that were exported (useful for follow-up
    assertions against the destination).
    """
    if node is None:
        node = self.context.node

    partition_ids = get_partition_ids(table_name=source_table, node=node)

    for pid in partition_ids:
        export_partition(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=pid,
            node=node,
            settings=settings,
            extra_settings=extra_settings,
            wait_for_completion=wait_for_completion,
            wait_timeout=wait_timeout,
        )

    return partition_ids


@TestStep(When)
def kill_export_partition(
    self,
    source_table,
    destination_table,
    partition_id,
    node=None,
    exitcode=0,
):
    """Run ``KILL EXPORT PARTITION WHERE ...``."""
    if node is None:
        node = self.context.node
    no_checks = exitcode != 0

    return node.query(
        f"KILL EXPORT PARTITION WHERE "
        f"partition_id = '{partition_id}' "
        f"AND source_table = '{source_table}' "
        f"AND destination_table = '{destination_table}'",
        exitcode=exitcode,
        no_checks=no_checks,
    )
