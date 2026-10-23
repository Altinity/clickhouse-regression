"""FREEZE / UNFREEZE on a CAS pool mounted by more than one server.

A CAS pool can be mounted by several servers, each owning the namespaces it
publishes under its own ``cas_server_root_id``. FREEZE publishes frozen parts
into a shadow namespace scoped under that same server root, so a frozen part's
manifest key names the server that froze it:

    live parts    cas/manifests/<server_root_id>/store/<uuid>@cas@/...
    frozen parts  cas/manifests/<server_root_id>/shadow/<backup>/store/<uuid>/...

Replicas of one table share a table UUID, so that server root is the only thing
in the path that tells one replica's snapshots from another's.

Each scenario gets a pool of its own, addressable by disk name, so a failure
cannot be blamed on another scenario's data.
"""

import uuid as uuid_module

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


@TestStep(Given)
@Name("a frozen table on a pool of its own, mounted by two servers")
def frozen_table(self, run_id, writer, nodes, partition=None):
    """Create a replicated table on a private pool, fill it, and freeze it.

    Every replica mounts the same pool under its own ``cas_server_root_id``,
    and an explicit table UUID makes the replicas agree on the table path the
    way ON CLUSTER would. With ``partition`` only that partition is frozen.

    Yields ``(table, backup_name, pool_prefix, disk_name, namespaces)``.
    """
    table_name = f"freeze_{run_id}"
    backup_name = f"backup_{run_id}"
    pool_prefix = f"data/{table_name}"
    disk_name = f"cas_{table_name}"

    create_replicated_cas_table(
        table_name=table_name,
        nodes=nodes,
        pool_prefix=pool_prefix,
        disk_name=disk_name,
        table_uuid=str(uuid_module.uuid4()),
    )
    insert_cas_partitions(table_name=table_name, node=writer)
    sync_replicas(table_name=table_name, nodes=nodes)

    before = settled_pool_snapshot(pool_prefix=pool_prefix)

    if partition is None:
        freeze_table(table_name=table_name, backup_name=backup_name, node=writer)
    else:
        freeze_partition(
            table_name=table_name,
            partition=partition,
            backup_name=backup_name,
            node=writer,
        )

    after = settled_pool_snapshot(pool_prefix=pool_prefix)

    manifests = backup_manifest_keys(after, backup_name=backup_name)
    added, _, rewritten = pool_difference(before, after)
    namespaces = namespaces_of(added + rewritten)

    note(f"backup manifests published by {writer.name}: {manifests}")
    note(f"namespaces the freeze wrote to: {namespaces}")

    assert manifests, error(
        f"FREEZE on {writer.name} published no manifest under "
        f"shadow/{backup_name}/, so there is no backup to reason about"
    )
    assert namespaces, error(
        f"FREEZE on {writer.name} wrote to no namespace, so the backup holds "
        "no refs and nothing below can be told apart"
    )

    yield table_name, backup_name, pool_prefix, disk_name, namespaces


@TestStep(When)
@Name("drop the table on every replica and collect garbage")
def drop_table_and_collect_garbage(self, table_name, disk, pool_prefix, nodes):
    """Drop the table everywhere, collect garbage, and return the settled pool.

    After this the only thing that can still hold the table's parts is a
    backup, so what remains is exactly what some backup is holding.
    """
    for node in nodes:
        node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    collect_garbage(disk=disk, nodes=nodes)

    return settled_pool_snapshot(pool_prefix=pool_prefix)


@TestScenario
@Name("a shadow namespace is scoped to the server that froze it")
@Requirements(
    RQ_SRS_048_CAS_Partition_Freeze("1.0"),
    RQ_SRS_048_CAS_SharedPool("1.0"),
    RQ_SRS_048_CAS_SharedPool_IndependentRefs("1.0"),
)
def shadow_namespace_is_scoped_to_the_freezing_server(self):
    """Check that frozen parts land under the freezing server's root only.

    This is what keeps one server's UNFREEZE away from another's snapshots:
    the backup name alone does not address a snapshot, the server root does.
    """
    nodes = self.context.nodes[:2]
    backup_owner, other_server = nodes[0], nodes[1]

    with Given("a frozen table on a pool of its own, mounted by two servers"):
        table, backup_name, pool_prefix, _, _ = frozen_table(
            run_id=getuid(), writer=backup_owner, nodes=nodes
        )

    with When("the pool is inspected"):
        snapshot = settled_pool_snapshot(pool_prefix=pool_prefix)
        roots = backup_server_roots(snapshot, backup_name=backup_name)
        note(f"server roots holding shadow/{backup_name}/: {roots}")

    with Then("only the server that froze owns the backup's manifests"):
        owner_root = cas_server_root_id(table, backup_owner)
        other_root = cas_server_root_id(table, other_server)

        assert roots == [owner_root], error(
            f"{backup_owner.name} froze the table, so shadow/{backup_name}/ "
            f"must sit under {owner_root} alone, but it is owned by {roots}"
        )

    with And(f"{other_server.name} holds nothing of that backup"):
        foreign = backup_manifest_keys(
            snapshot, backup_name=backup_name, server_root_id=other_root
        )

        assert not foreign, error(
            f"{other_server.name} took no backup, yet {foreign} is published "
            f"under its own server root {other_root}"
        )


@TestScenario
@Name("a backup outlives the table it was taken from")
@Requirements(
    RQ_SRS_048_CAS_Partition_Freeze("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
)
def backup_outlives_its_table(self):
    """Check that FREEZE holds the frozen parts against a drop and a collection."""
    nodes = self.context.nodes[:2]
    backup_owner = nodes[0]

    with Given("a frozen table on a pool of its own, mounted by two servers"):
        table, backup_name, pool_prefix, disk, _ = frozen_table(
            run_id=getuid(), writer=backup_owner, nodes=nodes
        )

    with When("the table is dropped everywhere and the pool collects garbage"):
        remaining = drop_table_and_collect_garbage(
            table_name=table, disk=disk, pool_prefix=pool_prefix, nodes=nodes
        )

    with Then("the frozen parts are still in the pool"):
        manifests = backup_manifest_keys(remaining, backup_name=backup_name)
        blobs = blob_keys(remaining)

        assert manifests and blobs, error(
            f"the backup did not outlive its table: {len(manifests)} manifests "
            f"and {len(blobs)} blobs are left, so a backup taken before a drop "
            "cannot be restored from"
        )


@TestScenario
@Name("releasing a backup releases its storage")
@Requirements(
    RQ_SRS_048_CAS_Partition_Unfreeze("1.0"),
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
)
def released_backup_releases_its_storage(self):
    """Check that nothing of a dropped table survives releasing its backup.

    A backup is the last thing holding the parts of a dropped table, so once it
    is released the pool must come back to empty. Anything still there is
    storage no statement can reach and no statement can free.
    """
    nodes = self.context.nodes[:2]
    backup_owner = nodes[0]

    with Given("a frozen table on a pool of its own, mounted by two servers"):
        table, backup_name, pool_prefix, disk, _ = frozen_table(
            run_id=getuid(), writer=backup_owner, nodes=nodes
        )

    with When("the server that took the backup releases it"):
        unfreeze_table(
            table_name=table, backup_name=backup_name, node=backup_owner
        )

    with And("the table is dropped everywhere and the pool collects garbage"):
        remaining = drop_table_and_collect_garbage(
            table_name=table, disk=disk, pool_prefix=pool_prefix, nodes=nodes
        )

    with Then("nothing of the table is left in the pool"):
        manifests = backup_manifest_keys(remaining, backup_name=backup_name)
        blobs = blob_keys(remaining)

        assert not manifests and not blobs, error(
            f"the table is gone and its backup is released, yet {len(blobs)} "
            f"blobs and {len(manifests)} manifests are still in the pool. "
            f"Blobs: {blobs}. Manifests: {manifests}"
        )


@TestScenario
@Name("a peer releasing the same name leaves the backup intact")
@Requirements(
    RQ_SRS_048_CAS_Partition_Freeze("1.0"),
    RQ_SRS_048_CAS_Partition_Unfreeze("1.0"),
    RQ_SRS_048_CAS_SharedPool("1.0"),
    RQ_SRS_048_CAS_SharedPool_IndependentRefs("1.0"),
)
def peer_release_leaves_the_backup_intact(self):
    """Check that UNFREEZE on a server that froze nothing is a no-op here.

    Both servers hold a replica of the same table on one pool and each owns a
    different ``cas_server_root_id``, so the peer has nothing of its own to
    release. The backup's namespaces must not change, and the frozen parts
    must still survive the drop that follows.
    """
    nodes = self.context.nodes[:2]
    backup_owner, other_server = nodes[0], nodes[1]

    with Given("a frozen table on a pool of its own, mounted by two servers"):
        table, backup_name, pool_prefix, disk, namespaces = frozen_table(
            run_id=getuid(), writer=backup_owner, nodes=nodes
        )

    with When("a server that took no backup releases the same name"):
        before = settled_pool_snapshot(pool_prefix=pool_prefix)
        unfreeze_table(
            table_name=table, backup_name=backup_name, node=other_server
        )
        after = settled_pool_snapshot(pool_prefix=pool_prefix)

    with Then("the backup's namespaces are untouched"):
        added, removed, rewritten = pool_difference(before, after)
        invaded = sorted(
            set(namespaces_of(added + removed + rewritten)) & set(namespaces)
        )

        assert not invaded, error(
            f"{other_server.name} took no backup, yet its UNFREEZE wrote into "
            f"{invaded} — the namespace holding the backup taken by "
            f"{backup_owner.name}. It added {added}, removed {removed} and "
            f"rewrote {rewritten}"
        )

    with And("the backup still survives the table being dropped"):
        remaining = drop_table_and_collect_garbage(
            table_name=table, disk=disk, pool_prefix=pool_prefix, nodes=nodes
        )
        manifests = backup_manifest_keys(remaining, backup_name=backup_name)
        blobs = blob_keys(remaining)

        assert manifests and blobs, error(
            f"the backup taken by {backup_owner.name} is unrestorable: "
            f"{len(manifests)} manifests and {len(blobs)} blobs are left after "
            f"{other_server.name} — which took no backup — released the same "
            "name"
        )


@TestScenario
@Name("releasing an unrelated name leaves the backup intact")
@Requirements(
    RQ_SRS_048_CAS_Partition_Unfreeze("1.0"),
)
def unrelated_name_leaves_the_backup_intact(self):
    """Check that releasing some other backup name leaves this backup alone.

    Read with the peer-release scenario this says where damage would come
    from: a shared backup name, or any UNFREEZE at all.
    """
    nodes = self.context.nodes[:2]
    backup_owner, other_server = nodes[0], nodes[1]
    unrelated_name = f"unrelated_{getuid()}"

    with Given("a frozen table on a pool of its own, mounted by two servers"):
        table, backup_name, pool_prefix, _, namespaces = frozen_table(
            run_id=getuid(), writer=backup_owner, nodes=nodes
        )

    with When("a server releases a backup name that was never taken"):
        before = settled_pool_snapshot(pool_prefix=pool_prefix)
        unfreeze_table(
            table_name=table, backup_name=unrelated_name, node=other_server
        )
        after = settled_pool_snapshot(pool_prefix=pool_prefix)

    with Then("the backup's namespaces are untouched"):
        added, removed, rewritten = pool_difference(before, after)
        invaded = sorted(
            set(namespaces_of(added + removed + rewritten)) & set(namespaces)
        )

        assert not invaded, error(
            f"releasing '{unrelated_name}' on {other_server.name} wrote into "
            f"{invaded} — the namespace holding an unrelated backup taken by "
            f"{backup_owner.name}. It added {added}, removed {removed} and "
            f"rewrote {rewritten}"
        )

    with And("the backup's manifests are still published"):
        manifests = backup_manifest_keys(after, backup_name=backup_name)

        assert manifests, error(
            f"releasing '{unrelated_name}' on {other_server.name} removed the "
            f"manifests of backup '{backup_name}'"
        )


@TestScenario
@Name("two servers freeze the same name independently")
@Requirements(
    RQ_SRS_048_CAS_Partition_Freeze("1.0"),
    RQ_SRS_048_CAS_Partition_Unfreeze("1.0"),
    RQ_SRS_048_CAS_SharedPool_IndependentRefs("1.0"),
)
def two_servers_freeze_the_same_name(self):
    """Check that one backup name on two servers is two separate snapshots.

    Both replicas freeze under the same name, so each publishes under its own
    server root. One server then releases, and only its own snapshot goes.
    """
    nodes = self.context.nodes[:2]
    first, second = nodes[0], nodes[1]

    with Given("a frozen table on a pool of its own, mounted by two servers"):
        table, backup_name, pool_prefix, disk, _ = frozen_table(
            run_id=getuid(), writer=first, nodes=nodes
        )

    with When("the second server freezes the same name"):
        freeze_table(table_name=table, backup_name=backup_name, node=second)
        after_both = settled_pool_snapshot(pool_prefix=pool_prefix)

    with Then("each server owns its own snapshot of that name"):
        roots = backup_server_roots(after_both, backup_name=backup_name)
        expected = sorted(
            [cas_server_root_id(table, first), cas_server_root_id(table, second)]
        )

        assert roots == expected, error(
            f"both servers froze '{backup_name}', so it must be owned by "
            f"{expected}, but it is owned by {roots}"
        )

    with When("the second server releases its own snapshot"):
        unfreeze_table(table_name=table, backup_name=backup_name, node=second)
        collect_garbage(disk=disk, nodes=nodes)
        after_release = settled_pool_snapshot(pool_prefix=pool_prefix)

    with Then("only the second server's snapshot is gone"):
        kept = backup_manifest_keys(
            after_release,
            backup_name=backup_name,
            server_root_id=cas_server_root_id(table, first),
        )
        released = backup_manifest_keys(
            after_release,
            backup_name=backup_name,
            server_root_id=cas_server_root_id(table, second),
        )

        assert kept, error(
            f"{second.name} released its own snapshot of '{backup_name}' and "
            f"took {first.name}'s with it"
        )
        assert not released, error(
            f"{second.name} released '{backup_name}' yet still holds "
            f"{released}"
        )


@TestScenario
@Name("freeze and unfreeze one partition")
@Requirements(
    RQ_SRS_048_CAS_Partition_Freeze("1.0"),
    RQ_SRS_048_CAS_Partition_Unfreeze("1.0"),
)
def freeze_and_unfreeze_one_partition(self):
    """Check that FREEZE PARTITION takes that partition alone and UNFREEZE PARTITION releases it.

    The table holds partitions 1, 2 and 3. A manifest key carries a build
    ordinal rather than a part name, so the oracle is the count: the backup
    must hold one manifest per active part of the frozen partition, and no
    more.
    """
    nodes = self.context.nodes[:2]
    backup_owner = nodes[0]
    frozen_partition = 2

    with Given("a table with one frozen partition on a pool of its own"):
        table, backup_name, pool_prefix, disk, _ = frozen_table(
            run_id=getuid(),
            writer=backup_owner,
            nodes=nodes,
            partition=frozen_partition,
        )

    with When("the pool is inspected"):
        snapshot = settled_pool_snapshot(pool_prefix=pool_prefix)
        manifests = backup_manifest_keys(snapshot, backup_name=backup_name)
        parts_in_partition = int(
            backup_owner.query(
                f"SELECT count() FROM system.parts WHERE table = '{table}' "
                f"AND partition = '{frozen_partition}' AND active"
            ).output.strip()
        )
        note(f"manifests under shadow/{backup_name}/: {manifests}")

    with Then("the backup holds the parts of that partition only"):
        assert len(manifests) == parts_in_partition, error(
            f"partition {frozen_partition} has {parts_in_partition} active "
            f"parts, but FREEZE PARTITION published {len(manifests)} "
            f"manifests: {manifests}"
        )

    with When("the owner releases that partition"):
        unfreeze_partition(
            table_name=table,
            partition=frozen_partition,
            backup_name=backup_name,
            node=backup_owner,
        )
        collect_garbage(disk=disk, nodes=nodes)
        after = settled_pool_snapshot(pool_prefix=pool_prefix)

    with Then("the backup name holds nothing"):
        remaining = backup_manifest_keys(after, backup_name=backup_name)

        assert not remaining, error(
            f"UNFREEZE PARTITION {frozen_partition} left {remaining} under "
            f"shadow/{backup_name}/"
        )

    with And("the table still has every row"):
        rows = int(
            backup_owner.query(f"SELECT count() FROM {table}").output.strip()
        )

        assert rows == 30, error(
            f"releasing the backup of partition {frozen_partition} left "
            f"{rows} rows in {table}, expected 30"
        )


@TestFeature
@Name("freeze isolation")
def feature(self):
    """FREEZE / UNFREEZE isolation between servers sharing a CAS pool.

    Every scenario runs even when an earlier one fails, so one bug cannot hide
    another.
    """
    Scenario(run=shadow_namespace_is_scoped_to_the_freezing_server, flags=TE)
    Scenario(run=backup_outlives_its_table, flags=TE)
    Scenario(run=released_backup_releases_its_storage, flags=TE)
    Scenario(run=peer_release_leaves_the_backup_intact, flags=TE)
    Scenario(run=unrelated_name_leaves_the_backup_intact, flags=TE)
    Scenario(run=two_servers_freeze_the_same_name, flags=TE)
    Scenario(run=freeze_and_unfreeze_one_partition, flags=TE)
