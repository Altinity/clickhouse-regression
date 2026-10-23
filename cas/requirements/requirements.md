# SRS-048 ClickHouse Content-Addressed Storage
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
    * 4.1 [Generic](#generic)
        * 4.1.1 [RQ.SRS-048.CAS](#rqsrs-048cas)
        * 4.1.2 [RQ.SRS-048.CAS.NotATableEngine](#rqsrs-048casnotatableengine)
    * 4.2 [Configuration](#configuration)
        * 4.2.1 [RQ.SRS-048.CAS.Disk.Configuration](#rqsrs-048casdiskconfiguration)
        * 4.2.2 [RQ.SRS-048.CAS.Disk.MetadataType](#rqsrs-048casdiskmetadatatype)
        * 4.2.3 [RQ.SRS-048.CAS.Disk.ServerRootId](#rqsrs-048casdiskserverrootid)
        * 4.2.4 [RQ.SRS-048.CAS.Disk.ServerRootId.Unique](#rqsrs-048casdiskserverrootidunique)
        * 4.2.5 [RQ.SRS-048.CAS.Disk.ServerRootId.Validation](#rqsrs-048casdiskserverrootidvalidation)
        * 4.2.6 [RQ.SRS-048.CAS.Disk.ServerRootId.Ownership](#rqsrs-048casdiskserverrootidownership)
        * 4.2.7 [RQ.SRS-048.CAS.Disk.ServerRootId.Rejoin](#rqsrs-048casdiskserverrootidrejoin)
        * 4.2.8 [RQ.SRS-048.CAS.Disk.Pool](#rqsrs-048casdiskpool)
        * 4.2.9 [RQ.SRS-048.CAS.Disk.Inline](#rqsrs-048casdiskinline)
        * 4.2.10 [RQ.SRS-048.CAS.Policy](#rqsrs-048caspolicy)
        * 4.2.11 [RQ.SRS-048.CAS.Disk.Settings](#rqsrs-048casdisksettings)
        * 4.2.12 [RQ.SRS-048.CAS.Disk.CoreSettings](#rqsrs-048casdiskcoresettings)
        * 4.2.13 [RQ.SRS-048.CAS.Disk.LeaseTiming](#rqsrs-048casdiskleasetiming)
        * 4.2.14 [RQ.SRS-048.CAS.Disk.Staging](#rqsrs-048casdiskstaging)
        * 4.2.15 [RQ.SRS-048.CAS.Disk.ConnectionReuse](#rqsrs-048casdiskconnectionreuse)
        * 4.2.16 [RQ.SRS-048.CAS.Disk.BlobHash](#rqsrs-048casdiskblobhash)
        * 4.2.17 [RQ.SRS-048.CAS.Disk.Backends](#rqsrs-048casdiskbackends)
    * 4.3 [Object Model](#object-model)
        * 4.3.1 [RQ.SRS-048.CAS.ObjectModel](#rqsrs-048casobjectmodel)
        * 4.3.2 [RQ.SRS-048.CAS.ObjectModel.Blobs](#rqsrs-048casobjectmodelblobs)
        * 4.3.3 [RQ.SRS-048.CAS.ObjectModel.Manifests](#rqsrs-048casobjectmodelmanifests)
        * 4.3.4 [RQ.SRS-048.CAS.ObjectModel.Refs](#rqsrs-048casobjectmodelrefs)
        * 4.3.5 [RQ.SRS-048.CAS.ObjectModel.Immutability](#rqsrs-048casobjectmodelimmutability)
        * 4.3.6 [RQ.SRS-048.CAS.ObjectModel.PhysicalRefs](#rqsrs-048casobjectmodelphysicalrefs)
        * 4.3.7 [RQ.SRS-048.CAS.ObjectModel.Catalog](#rqsrs-048casobjectmodelcatalog)
        * 4.3.8 [RQ.SRS-048.CAS.ObjectModel.FormatGeneration](#rqsrs-048casobjectmodelformatgeneration)
        * 4.3.9 [RQ.SRS-048.CAS.ObjectModel.ManifestLimits](#rqsrs-048casobjectmodelmanifestlimits)
    * 4.4 [Write Path](#write-path)
        * 4.4.1 [RQ.SRS-048.CAS.Write.Publish](#rqsrs-048caswritepublish)
        * 4.4.2 [RQ.SRS-048.CAS.Write.BlobMaterialization](#rqsrs-048caswriteblobmaterialization)
        * 4.4.3 [RQ.SRS-048.CAS.Write.BlobPublishRetries](#rqsrs-048caswriteblobpublishretries)
        * 4.4.4 [RQ.SRS-048.CAS.Write.CommitOutcome](#rqsrs-048caswritecommitoutcome)
        * 4.4.5 [RQ.SRS-048.CAS.Write.PartRename](#rqsrs-048caswritepartrename)
        * 4.4.6 [RQ.SRS-048.CAS.Write.HashCollision](#rqsrs-048caswritehashcollision)
    * 4.5 [Read Path](#read-path)
        * 4.5.1 [RQ.SRS-048.CAS.Read](#rqsrs-048casread)
        * 4.5.2 [RQ.SRS-048.CAS.Read.ManifestValidation](#rqsrs-048casreadmanifestvalidation)
        * 4.5.3 [RQ.SRS-048.CAS.Read.Caches](#rqsrs-048casreadcaches)
        * 4.5.4 [RQ.SRS-048.CAS.Read.DirectoryProbes](#rqsrs-048casreaddirectoryprobes)
        * 4.5.5 [RQ.SRS-048.CAS.Read.InFlight](#rqsrs-048casreadinflight)
        * 4.5.6 [RQ.SRS-048.CAS.Read.ReadOnly](#rqsrs-048casreadreadonly)
    * 4.6 [MergeTree Compatibility](#mergetree-compatibility)
        * 4.6.1 [RQ.SRS-048.CAS.MergeTree](#rqsrs-048casmergetree)
        * 4.6.2 [RQ.SRS-048.CAS.MergeTree.Transparency](#rqsrs-048casmergetreetransparency)
        * 4.6.3 [RQ.SRS-048.CAS.MergeTree.Engines](#rqsrs-048casmergetreeengines)
        * 4.6.4 [RQ.SRS-048.CAS.MergeTree.InsertSelect](#rqsrs-048casmergetreeinsertselect)
        * 4.6.5 [RQ.SRS-048.CAS.MergeTree.Merge](#rqsrs-048casmergetreemerge)
        * 4.6.6 [RQ.SRS-048.CAS.MergeTree.Replicated](#rqsrs-048casmergetreereplicated)
        * 4.6.7 [RQ.SRS-048.CAS.MergeTree.PartTypes](#rqsrs-048casmergetreeparttypes)
        * 4.6.8 [RQ.SRS-048.CAS.MergeTree.Alter.Schema](#rqsrs-048casmergetreealterschema)
        * 4.6.9 [RQ.SRS-048.CAS.MergeTree.Mutations](#rqsrs-048casmergetreemutations)
        * 4.6.10 [RQ.SRS-048.CAS.MergeTree.LightweightDelete](#rqsrs-048casmergetreelightweightdelete)
        * 4.6.11 [RQ.SRS-048.CAS.MergeTree.PatchParts](#rqsrs-048casmergetreepatchparts)
        * 4.6.12 [RQ.SRS-048.CAS.MergeTree.Projections](#rqsrs-048casmergetreeprojections)
        * 4.6.13 [RQ.SRS-048.CAS.MergeTree.TTL](#rqsrs-048casmergetreettl)
        * 4.6.14 [RQ.SRS-048.CAS.MergeTree.Transactions](#rqsrs-048casmergetreetransactions)
        * 4.6.15 [RQ.SRS-048.CAS.MergeTree.RestartDurability](#rqsrs-048casmergetreerestartdurability)
        * 4.6.16 [RQ.SRS-048.CAS.MergeTree.Rename](#rqsrs-048casmergetreerename)
        * 4.6.17 [RQ.SRS-048.CAS.MergeTree.Alter](#rqsrs-048casmergetreealter)
        * 4.6.18 [RQ.SRS-048.CAS.MergeTree.Alter.Column](#rqsrs-048casmergetreealtercolumn)
        * 4.6.19 [RQ.SRS-048.CAS.MergeTree.Alter.Update](#rqsrs-048casmergetreealterupdate)
        * 4.6.20 [RQ.SRS-048.CAS.MergeTree.Alter.Delete](#rqsrs-048casmergetreealterdelete)
        * 4.6.21 [RQ.SRS-048.CAS.MergeTree.Alter.OrderBy](#rqsrs-048casmergetreealterorderby)
        * 4.6.22 [RQ.SRS-048.CAS.MergeTree.Alter.SampleBy](#rqsrs-048casmergetreealtersampleby)
        * 4.6.23 [RQ.SRS-048.CAS.MergeTree.Alter.Index](#rqsrs-048casmergetreealterindex)
        * 4.6.24 [RQ.SRS-048.CAS.MergeTree.Alter.Projection](#rqsrs-048casmergetreealterprojection)
        * 4.6.25 [RQ.SRS-048.CAS.MergeTree.Alter.Constraint](#rqsrs-048casmergetreealterconstraint)
        * 4.6.26 [RQ.SRS-048.CAS.MergeTree.Alter.TTL](#rqsrs-048casmergetreealterttl)
        * 4.6.27 [RQ.SRS-048.CAS.MergeTree.Alter.Statistics](#rqsrs-048casmergetreealterstatistics)
        * 4.6.28 [RQ.SRS-048.CAS.MergeTree.Alter.Setting](#rqsrs-048casmergetreealtersetting)
        * 4.6.29 [RQ.SRS-048.CAS.MergeTree.Alter.Comment](#rqsrs-048casmergetreealtercomment)
        * 4.6.30 [RQ.SRS-048.CAS.MergeTree.Alter.ApplyDeletedMask](#rqsrs-048casmergetreealterapplydeletedmask)
        * 4.6.31 [RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches](#rqsrs-048casmergetreealterapplypatches)
        * 4.6.32 [RQ.SRS-048.CAS.MergeTree.MaterializedView](#rqsrs-048casmergetreematerializedview)
    * 4.7 [Partition And Part Operations](#partition-and-part-operations)
        * 4.7.1 [RQ.SRS-048.CAS.Partition.AlterAllowList](#rqsrs-048caspartitionalterallowlist)
        * 4.7.2 [RQ.SRS-048.CAS.Partition.Replace](#rqsrs-048caspartitionreplace)
        * 4.7.3 [RQ.SRS-048.CAS.Partition.AttachFrom](#rqsrs-048caspartitionattachfrom)
        * 4.7.4 [RQ.SRS-048.CAS.Partition.Attach](#rqsrs-048caspartitionattach)
        * 4.7.5 [RQ.SRS-048.CAS.Partition.Detach](#rqsrs-048caspartitiondetach)
        * 4.7.6 [RQ.SRS-048.CAS.Partition.DetachAttach](#rqsrs-048caspartitiondetachattach)
        * 4.7.7 [RQ.SRS-048.CAS.Partition.MoveToTable](#rqsrs-048caspartitionmovetotable)
        * 4.7.8 [RQ.SRS-048.CAS.Partition.Drop](#rqsrs-048caspartitiondrop)
        * 4.7.9 [RQ.SRS-048.CAS.Partition.DropDetached](#rqsrs-048caspartitiondropdetached)
        * 4.7.10 [RQ.SRS-048.CAS.Partition.Forget](#rqsrs-048caspartitionforget)
        * 4.7.11 [RQ.SRS-048.CAS.Partition.Fetch](#rqsrs-048caspartitionfetch)
        * 4.7.12 [RQ.SRS-048.CAS.Partition.Freeze](#rqsrs-048caspartitionfreeze)
        * 4.7.13 [RQ.SRS-048.CAS.Partition.Unfreeze](#rqsrs-048caspartitionunfreeze)
        * 4.7.14 [RQ.SRS-048.CAS.Partition.Clone](#rqsrs-048caspartitionclone)
        * 4.7.15 [RQ.SRS-048.CAS.Partition.ClearColumn](#rqsrs-048caspartitionclearcolumn)
        * 4.7.16 [RQ.SRS-048.CAS.Partition.ClearIndex](#rqsrs-048caspartitionclearindex)
        * 4.7.17 [RQ.SRS-048.CAS.Partition.RewriteParts](#rqsrs-048caspartitionrewriteparts)
        * 4.7.18 [RQ.SRS-048.CAS.Partition.Update](#rqsrs-048caspartitionupdate)
        * 4.7.19 [RQ.SRS-048.CAS.Partition.Delete](#rqsrs-048caspartitiondelete)
        * 4.7.20 [RQ.SRS-048.CAS.Partition.MoveToDisk](#rqsrs-048caspartitionmovetodisk)
        * 4.7.21 [RQ.SRS-048.CAS.Partition.Export](#rqsrs-048caspartitionexport)
    * 4.8 [Backup And Restore](#backup-and-restore)
        * 4.8.1 [RQ.SRS-048.CAS.Backup](#rqsrs-048casbackup)
        * 4.8.2 [RQ.SRS-048.CAS.Restore](#rqsrs-048casrestore)
        * 4.8.3 [RQ.SRS-048.CAS.Backup.SameEndpointCopy](#rqsrs-048casbackupsameendpointcopy)
    * 4.9 [Shared Pool](#shared-pool)
        * 4.9.1 [RQ.SRS-048.CAS.SharedPool](#rqsrs-048cassharedpool)
        * 4.9.2 [RQ.SRS-048.CAS.SharedPool.Deduplication](#rqsrs-048cassharedpooldeduplication)
        * 4.9.3 [RQ.SRS-048.CAS.SharedPool.IndependentRefs](#rqsrs-048cassharedpoolindependentrefs)
        * 4.9.4 [RQ.SRS-048.CAS.SharedPool.NodeCrash](#rqsrs-048cassharedpoolnodecrash)
        * 4.9.5 [RQ.SRS-048.CAS.SharedPool.MountRecovery](#rqsrs-048cassharedpoolmountrecovery)
        * 4.9.6 [RQ.SRS-048.CAS.SharedPool.TerminalLifecycle](#rqsrs-048cassharedpoolterminallifecycle)
    * 4.10 [Replication Relink](#replication-relink)
        * 4.10.1 [RQ.SRS-048.CAS.Relink](#rqsrs-048casrelink)
        * 4.10.2 [RQ.SRS-048.CAS.Relink.HappyPath](#rqsrs-048casrelinkhappypath)
        * 4.10.3 [RQ.SRS-048.CAS.Relink.DetachedFetch](#rqsrs-048casrelinkdetachedfetch)
        * 4.10.4 [RQ.SRS-048.CAS.Relink.CrossPool.ByteFallback](#rqsrs-048casrelinkcrosspoolbytefallback)
        * 4.10.5 [RQ.SRS-048.CAS.Relink.AttachPartitionFrom](#rqsrs-048casrelinkattachpartitionfrom)
        * 4.10.6 [RQ.SRS-048.CAS.Relink.ReplacePartition](#rqsrs-048casrelinkreplacepartition)
        * 4.10.7 [RQ.SRS-048.CAS.Relink.VersionMix](#rqsrs-048casrelinkversionmix)
        * 4.10.8 [RQ.SRS-048.CAS.Relink.ConfirmRace](#rqsrs-048casrelinkconfirmrace)
        * 4.10.9 [RQ.SRS-048.CAS.Relink.StalledPublish](#rqsrs-048casrelinkstalledpublish)
        * 4.10.10 [RQ.SRS-048.CAS.Relink.RecursionBrake](#rqsrs-048casrelinkrecursionbrake)
        * 4.10.11 [RQ.SRS-048.CAS.Relink.OfferIntegrity](#rqsrs-048casrelinkofferintegrity)
        * 4.10.12 [RQ.SRS-048.CAS.Relink.Placement](#rqsrs-048casrelinkplacement)
        * 4.10.13 [RQ.SRS-048.CAS.Relink.UnavailableTarget](#rqsrs-048casrelinkunavailabletarget)
        * 4.10.14 [RQ.SRS-048.CAS.Relink.FormatVersion](#rqsrs-048casrelinkformatversion)
        * 4.10.15 [RQ.SRS-048.CAS.Relink.GCBackstop](#rqsrs-048casrelinkgcbackstop)
    * 4.11 [Garbage Collection](#garbage-collection)
        * 4.11.1 [RQ.SRS-048.CAS.GC](#rqsrs-048casgc)
        * 4.11.2 [RQ.SRS-048.CAS.GC.NoLoss](#rqsrs-048casgcnoloss)
        * 4.11.3 [RQ.SRS-048.CAS.GC.ReclaimAfterDrop](#rqsrs-048casgcreclaimafterdrop)
        * 4.11.4 [RQ.SRS-048.CAS.GC.Run](#rqsrs-048casgcrun)
        * 4.11.5 [RQ.SRS-048.CAS.GC.Rebuild](#rqsrs-048casgcrebuild)
        * 4.11.6 [RQ.SRS-048.CAS.GC.Sharded](#rqsrs-048casgcsharded)
        * 4.11.7 [RQ.SRS-048.CAS.GC.RefSnaplog](#rqsrs-048casgcrefsnaplog)
        * 4.11.8 [RQ.SRS-048.CAS.GC.StopStart](#rqsrs-048casgcstopstart)
        * 4.11.9 [RQ.SRS-048.CAS.GC.Phases](#rqsrs-048casgcphases)
        * 4.11.10 [RQ.SRS-048.CAS.GC.Budgets](#rqsrs-048casgcbudgets)
        * 4.11.11 [RQ.SRS-048.CAS.GC.ReadAhead](#rqsrs-048casgcreadahead)
        * 4.11.12 [RQ.SRS-048.CAS.GC.OrphanManifests](#rqsrs-048casgcorphanmanifests)
        * 4.11.13 [RQ.SRS-048.CAS.GC.NamespaceJanitor](#rqsrs-048casgcnamespacejanitor)
        * 4.11.14 [RQ.SRS-048.CAS.GC.DeleteAuthority](#rqsrs-048casgcdeleteauthority)
        * 4.11.15 [RQ.SRS-048.CAS.GC.DryRun](#rqsrs-048casgcdryrun)
        * 4.11.16 [RQ.SRS-048.CAS.Fsck](#rqsrs-048casfsck)
        * 4.11.17 [RQ.SRS-048.CAS.Fsck.Online](#rqsrs-048casfsckonline)
    * 4.12 [Day-2 Operations](#day-2-operations)
        * 4.12.1 [RQ.SRS-048.CAS.DropPoolMember](#rqsrs-048casdroppoolmember)
        * 4.12.2 [RQ.SRS-048.CAS.DropPoolMember.ReadonlyRejected](#rqsrs-048casdroppoolmemberreadonlyrejected)
        * 4.12.3 [RQ.SRS-048.CAS.Forget](#rqsrs-048casforget)
        * 4.12.4 [RQ.SRS-048.CAS.Tools](#rqsrs-048castools)
    * 4.13 [Fault Recovery](#fault-recovery)
        * 4.13.1 [RQ.SRS-048.CAS.Fault.LostPartRecovery](#rqsrs-048casfaultlostpartrecovery)
        * 4.13.2 [RQ.SRS-048.CAS.Fault.LazyLoad.S3Outage](#rqsrs-048casfaultlazyloads3outage)
        * 4.13.3 [RQ.SRS-048.CAS.Fault.FailClosed](#rqsrs-048casfaultfailclosed)
    * 4.14 [Cache](#cache)
        * 4.14.1 [RQ.SRS-048.CAS.Cache](#rqsrs-048cascache)
        * 4.14.2 [RQ.SRS-048.CAS.Cache.Hits](#rqsrs-048cascachehits)
    * 4.15 [Observability And Access](#observability-and-access)
        * 4.15.1 [RQ.SRS-048.CAS.Observability](#rqsrs-048casobservability)
        * 4.15.2 [RQ.SRS-048.CAS.Observability.SystemTables](#rqsrs-048casobservabilitysystemtables)
        * 4.15.3 [RQ.SRS-048.CAS.Observability.Mounts](#rqsrs-048casobservabilitymounts)
        * 4.15.4 [RQ.SRS-048.CAS.Observability.GCLog](#rqsrs-048casobservabilitygclog)
        * 4.15.5 [RQ.SRS-048.CAS.Observability.EventLog](#rqsrs-048casobservabilityeventlog)
        * 4.15.6 [RQ.SRS-048.CAS.Observability.ProfileEvents](#rqsrs-048casobservabilityprofileevents)
        * 4.15.7 [RQ.SRS-048.CAS.Access](#rqsrs-048casaccess)
    * 4.16 [Restrictions And Non-Goals](#restrictions-and-non-goals)
        * 4.16.1 [RQ.SRS-048.CAS.Restrictions.BackendCapabilities](#rqsrs-048casrestrictionsbackendcapabilities)
        * 4.16.2 [RQ.SRS-048.CAS.Restrictions.ConditionalWriteRetries](#rqsrs-048casrestrictionsconditionalwriteretries)
        * 4.16.3 [RQ.SRS-048.CAS.Restrictions.BackendToken](#rqsrs-048casrestrictionsbackendtoken)
        * 4.16.4 [RQ.SRS-048.CAS.Restrictions.ZeroCopy](#rqsrs-048casrestrictionszerocopy)
        * 4.16.5 [RQ.SRS-048.CAS.Restrictions.UniqueKey](#rqsrs-048casrestrictionsuniquekey)
        * 4.16.6 [RQ.SRS-048.CAS.Restrictions.NonMergeTree](#rqsrs-048casrestrictionsnonmergetree)
        * 4.16.7 [RQ.SRS-048.CAS.Restrictions.Backup.TempHardLinks](#rqsrs-048casrestrictionsbackuptemphardlinks)
        * 4.16.8 [RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot](#rqsrs-048casrestrictionsbackupnativesnapshot)
        * 4.16.9 [RQ.SRS-048.CAS.Restrictions.Encryption](#rqsrs-048casrestrictionsencryption)
        * 4.16.10 [RQ.SRS-048.CAS.Restrictions.Azure](#rqsrs-048casrestrictionsazure)
        * 4.16.11 [RQ.SRS-048.CAS.Restrictions.GCS](#rqsrs-048casrestrictionsgcs)
        * 4.16.12 [RQ.SRS-048.CAS.Restrictions.LocalBackend](#rqsrs-048casrestrictionslocalbackend)
        * 4.16.13 [RQ.SRS-048.CAS.Restrictions.WideParts](#rqsrs-048casrestrictionswideparts)
* 5 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

Content-addressed storage ([CAS]) is an **opt-in object-storage disk backend** for
the [MergeTree] engine family. It is selected with
`metadata_type = cas` on an `object_storage` disk. It does **not**
introduce a new table engine.

Ordinary `MergeTree` and `ReplicatedMergeTree` tables keep their SQL surface and
logical part lifecycle. **All mainstream MergeTree features that work on ordinary
object-storage disks are expected to work on [CAS]** (insert/select,
materialized views, merge, mutations, projections, TTL, transactions, the
documented [MergeTree]
`ALTER TABLE` surface (columns, mutations, keys, indexes, projections,
constraints, TTL, statistics, settings, comments, apply-deleted-mask /
apply-patches, and partition ALTER including ATTACH / REPLACE / MOVE /
DETACH / DROP / FETCH / FREEZE / FORGET / CLEAR / REWRITE), backup on
Atomic DBs, replication), except where this [SRS] explicitly lists a restriction.
[CAS] changes only the physical representation of parts in a shared object-store
**pool**:

* immutable **blobs** keyed by content hash;
* immutable **part manifests** listing the files of one part;
* mutable **refs** that map part names to manifests under a per-server ownership
  namespace (`cas_server_root_id`).

Replicas that mount the same pool can **relink** (adopt a peer's manifest by
reference) instead of copying part bytes. Background **garbage collection** is
the only path authorized to delete blob bodies and the only
reachability-driven path that deletes manifest bodies. Writers may exact-delete
their own never-precommitted manifests, and pool-member decommission may remove
the retired member's private debris.

This [SRS] specifies the product requirements that the Altinity regression suite
exercises. Product architecture and operations live in the
[CAS documentation] (`docs/en/antalya/cas/`, plus the [SYSTEM CAS] page and the
[CAS system tables]). Upstream integration inventory is summarized in
[`cas/docs/CAS-INTEGRATION-TESTS.md`](../docs/CAS-INTEGRATION-TESTS.md).

**Status:** experimental. The on-disk format and the SQL surface can still change
between releases. Core read/write/ref/GC paths exist; release readiness is gated
by the live backlog in the product docs.

## Terminology

* **CAS** — content-addressed storage disk backend (`metadata_type = cas`).
* **Pool** — shared object-store bucket/prefix. Blob reuse is pool-global;
  relink eligibility is the minted `cas_pool_uuid`, not endpoint-plus-prefix
  string equality.
* **cas_server_root_id** — durable per-server ownership identity inside a pool.
  Distinct from the pool endpoint; must be unique among concurrent writers.
  The unprefixed spelling `server_root_id` is accepted for a bounded migration
  period and reported at startup.
* **Blob** — immutable content-addressed object under `blobs/...`.
* **Manifest** — immutable description of one MergeTree part's files.
* **Ref** — logical mutable mapping from a part name to a manifest. Physical
  state is reconstructed from append-only logs, snapshots, and checkpoints
  under an opaque namespace `life_id`.
* **Relink** — replication path that publishes a local ref to an already-present
  peer manifest instead of transferring part bytes.
* **GC** — background garbage collection that reclaims objects with no live
  ownership, without deleting objects still named by a committed reference.

## Requirements

### Generic

#### RQ.SRS-048.CAS
version: 1.0

[ClickHouse] SHALL support content-addressed storage as an object-storage disk
backend for the [MergeTree] engine family.

#### RQ.SRS-048.CAS.NotATableEngine
version: 1.0

[ClickHouse] SHALL expose [CAS] as a disk / storage-policy choice, not as a
separate table engine. Users SHALL create ordinary `MergeTree` /
`ReplicatedMergeTree` (and MergeTree-family) tables on a [CAS] disk or policy.

### Configuration

#### RQ.SRS-048.CAS.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support configuring a [CAS] disk in
`<storage_configuration><disks>` with `type = object_storage`, an object-storage
type such as `s3` or `local`, and [CAS]-specific settings including
`metadata_type = cas` and `cas_server_root_id`. The recommended production
shape layers a `type = cache` disk over the [CAS] disk and points the storage
policy at the cached disk.

Example:

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            <cas>
                <type>object_storage</type>
                <object_storage_type>s3</object_storage_type>
                <metadata_type>cas</metadata_type>
                <cas_server_root_id>{replica}</cas_server_root_id>
                <endpoint>https://bucket.s3.amazonaws.com/cas/</endpoint>
            </cas>
            <cas_cache>
                <type>cache</type>
                <disk>cas</disk>
                <path>/var/lib/clickhouse/cas_cache/</path>
                <max_size>10Gi</max_size>
            </cas_cache>
        </disks>
        <policies>
            <cas>
                <volumes>
                    <main>
                        <disk>cas_cache</disk>
                    </main>
                </volumes>
            </cas>
        </policies>
    </storage_configuration>
</clickhouse>
```

#### RQ.SRS-048.CAS.Disk.MetadataType
version: 1.0

[ClickHouse] SHALL enable content-addressed storage when
`metadata_type` is set to `cas` on an object-storage disk.

#### RQ.SRS-048.CAS.Disk.ServerRootId
version: 1.0

[ClickHouse] SHALL require a configured `cas_server_root_id` that identifies the
server's durable ownership tree inside the pool. Omitting the setting SHALL be a
startup error. The value MAY expand macros (for example `{replica}`) and SHALL
remain stable across restarts for that server's membership in the pool. The
unprefixed spelling `server_root_id` SHALL be accepted for a bounded migration
period and reported at startup; a key written in both spellings SHALL be
rejected.

#### RQ.SRS-048.CAS.Disk.ServerRootId.Unique
version: 1.0

[ClickHouse] SHALL fail closed when two servers attempt to mount the same pool
with the same `cas_server_root_id` as concurrent writers, instead of allowing
both to mutate the same ref namespace. A colliding identity SHALL be refused at
the owner-claim / mount-lease gate.

#### RQ.SRS-048.CAS.Disk.ServerRootId.Validation
version: 2.0

[ClickHouse] SHALL require a `cas_server_root_id` to be a single path
component, and SHALL reject an id that is empty, exceeds 255 bytes, contains
`/`, or equals `.`, `..`, `_files`, or `_manifests`. Validation SHALL run after
macro expansion, so a template that expands to a value containing `/` SHALL be
rejected. An id containing `/` SHALL be rejected even when it already owns its
owner object in the pool: the disk SHALL refuse to open, and `SYSTEM CAS DROP
POOL MEMBER` and `clickhouse-disks cas-drop-member` SHALL refuse it as a
victim. Invalid syntax SHALL fail with `BAD_ARGUMENTS`.

#### RQ.SRS-048.CAS.Disk.ServerRootId.Ownership
version: 2.0

[ClickHouse] SHALL bind each `cas_server_root_id` to one durable
`server_uuid` through an owner claim. A different UUID or a lost owner identity
over non-empty state SHALL fail closed with `CORRUPTED_DATA`. A tombstoned
owner SHALL refuse to mount, except through the documented rejoin of
[RQ.SRS-048.CAS.Disk.ServerRootId.Rejoin](#rqsrs-048casdiskserverrootidrejoin).

The owner object SHALL carry an `owner_life` counter that every owner write
bumps with `If-Match`, plus a `retirement_verified` flag. A mount SHALL record
the life it started under and SHALL re-read the owner after every slot claim —
at start and at self-remount — requiring its own UUID, that same life, and no
tombstone; otherwise it SHALL fence its own slot body and fail. A self-remount
that finds the owner at another life SHALL end the remount loop in
`identity_lost` without allocating a writer epoch, and only a restart SHALL
pick up the current life. A starter MAY reclaim a foreign terminal slot body
only after a fresh owner read shows its own UUID, the recorded life, and no
tombstone; a live foreign body SHALL stay refused as a foreign owner.

Writer-epoch allocation SHALL be unique between two processes that share one
`server_uuid`: every counter write SHALL carry a fresh allocation nonce, so an
ambiguous write SHALL NOT be adopted as the other process's write by byte
equality. Epochs SHALL be strictly increasing per `cas_server_root_id` across
lives. A member whose epoch counter is missing SHALL be refused rather than
repaired.

`owner_life`, `retirement_verified`, and the allocation nonce SHALL be optional
plain keys that an older reader skips; an owner without `owner_life` SHALL read
as life 0.

#### RQ.SRS-048.CAS.Disk.ServerRootId.Rejoin
version: 1.0

[ClickHouse] SHALL let a `cas_server_root_id` retired by
`SYSTEM CAS DROP POOL MEMBER` rejoin its pool as an **empty** member on the
next server start, under the same or a new `server_uuid`, without a hand-edited
owner object. The rejoin SHALL move the owner to a new life with `If-Match`,
SHALL continue the existing epoch counter, and SHALL log a warning naming the
old and new UUID and life. With a new `server_uuid`, the mount body SHALL be
rewritten for that UUID before the owner is claimed. Local table definitions of
a rejoined member SHALL attach with no rows.

Rejoin SHALL be refused, with a message that names the cause and the
recovery, when any of these holds: the caller is a self-remount; the
`server_uuid` is zero; the `epoch` or `mount` object is absent (checked first,
so such an id is never offered a decommission rerun); the retirement is not
verified; the slot is still held; data of the previous life remains; or the
owner or slot changes on every decision. A refusal for remaining data SHALL
name the part left behind and, for catalog rows and manifests, SHALL point at
`SYSTEM CAS GC RUN` on the [GC] leader. An id whose control objects are gone
SHALL require a new `cas_server_root_id`.

Decommission SHALL therefore be permanent for the member's **data**, not for
its identity.

#### RQ.SRS-048.CAS.Disk.Pool
version: 1.0

[ClickHouse] SHALL treat the object-storage endpoint (bucket and prefix) as the
shared [CAS] pool for blob reuse among servers that mount that endpoint with
distinct `cas_server_root_id` values. Relink eligibility SHALL use the minted
`cas_pool_uuid`, not endpoint-plus-prefix string equality.

#### RQ.SRS-048.CAS.Disk.Inline
version: 1.1

[ClickHouse] SHALL support selecting a [CAS] disk via the inline `disk = disk(...)`
table setting as well as via a named disk in storage configuration.

Creating a custom disk SHALL NOT block other disk creations or disk and
storage-policy lookups, so several [CAS] custom disks that each wait out a
stale mount lease at server start SHALL wait in parallel rather than one after
another, and a `system.disks` read during such a wait SHALL still answer.
Concurrent requests for one custom disk SHALL share a single open, and a failed
creation SHALL NOT be cached: the next request SHALL create the disk again.

#### RQ.SRS-048.CAS.Policy
version: 1.0

[ClickHouse] SHALL support selecting [CAS] disks through storage policies in
`<storage_configuration><policies>`, consistent with other object-storage disks.
When a `type = cache` disk wraps [CAS], the policy volume SHALL name the cache
disk, not the raw [CAS] disk.

#### RQ.SRS-048.CAS.Disk.Settings
version: 1.0

[ClickHouse] SHALL read [CAS]-owned disk settings from the `cas_` config-key
namespace and leave every other key in the disk block to the object-storage or
generic disk layer. A misspelled `cas_` key SHALL be rejected. Unprefixed
spellings of [CAS] settings SHALL be accepted for a bounded period and reported
at startup. `skip_access_check` and `gcs_max_conditional_put_bytes` SHALL remain
unprefixed (they belong to the generic disk / S3 client layers).

#### RQ.SRS-048.CAS.Disk.CoreSettings
version: 1.0

[ClickHouse] SHALL support the documented core [CAS] disk settings:

* `cas_scratch_path`
* `cas_gc_enabled` and `cas_gc_interval_sec`
* `cas_mount_lease_ttl_ms` and `cas_mount_renew_period_ms`
* `cas_gc_snapshot_generations_to_keep` and `cas_gc_shards`
* `cas_part_folder_cache_bytes`, `cas_part_folder_cache_max_entries`, and
  `cas_part_folder_cache_max_entry_bytes`
* `cas_manifest_decode_cache_bytes`
* `cas_gc_meta_pool_size` and `cas_gc_io_concurrency`
* `cas_attempt_timeout_ms` and `cas_lease_safety_margin_ms`
* `cas_unsafe_remount_no_delay`
* `cas_staging_backend`

The server-wide `cas_blob_upload_pool_size` setting SHALL control parallel blob
uploads and SHALL reject zero. `cas_gc_read_concurrency` SHALL be rejected
without an alias; the supported name is `cas_gc_io_concurrency`.

#### RQ.SRS-048.CAS.Disk.LeaseTiming
version: 2.0

[ClickHouse] SHALL validate mount-lease timing before opening a writable disk.
With `cap` equal to `cas_attempt_timeout_ms` when `connect_timeout_ms = 0`, or
otherwise `min(connect_timeout_ms, cas_attempt_timeout_ms)`, and
`envelope = cas_attempt_timeout_ms + 2 * cap`, both of these conditions SHALL
hold:

* `envelope + cas_lease_safety_margin_ms < cas_mount_lease_ttl_ms`
* `cas_mount_renew_period_ms + 2 * envelope + cas_lease_safety_margin_ms <
  cas_mount_lease_ttl_ms`

`cas_mount_lease_ttl_ms` SHALL be a per-server setting: how long this server
may keep writing after its last confirmed renewal. Every observer of a mount
slot — the [GC] floor, a same-server restart, and a self-remount reclaim —
SHALL wait at least the lease the holder declares in its slot body before
treating an unchanged slot token as a dead holder, so a server configured with
a longer TTL SHALL NOT be fenced inside its own right to write by an observer
configured with a shorter one. A slot body whose timestamps are missing,
equal, or reversed SHALL declare a lease of zero, so no observer waits less
than its own rule. Mixed values SHALL be safe in any order and SHALL NOT
require stopping every pool member to change.

#### RQ.SRS-048.CAS.Disk.Staging
version: 2.0

[ClickHouse] SHALL support `cas_staging_backend = local` and
`cas_staging_backend = s3`. S3 staging SHALL require native same-store copy on
a writable mount and SHALL fail closed rather than silently fall back to local
staging when that capability is unavailable.

An aborted transaction SHALL delete its S3 staging object on a best-effort
basis, as a commit does, instead of leaving it until the next mount of the same
`cas_server_root_id`. An S3 staging key SHALL carry the writer epoch
(`staging/<cas_server_root_id>/<epoch>/<random>.tmp`), and the startup sweep
SHALL delete only earlier epochs, so a paused older process SHALL NOT delete
its successor's staging. An upload killed mid-way is invisible to object `LIST`
and is never swept by [CAS]; operators SHALL configure the bucket's
`AbortIncompleteMultipartUpload` lifecycle rule.

#### RQ.SRS-048.CAS.Disk.ConnectionReuse
version: 1.0

[ClickHouse] SHALL accept generic object-storage connection settings in a [CAS]
disk block. The documented production configuration SHOULD use
`http_keep_alive_timeout = 30` and `http_keep_alive_max_requests = 10000` to
avoid exhausting ephemeral ports during wide-part and merge workloads.

#### RQ.SRS-048.CAS.Disk.BlobHash
version: 1.0

[ClickHouse] SHALL support selecting the pool blob content-hash function with
`cas_blob_hash` (`cityhash128` default, `xxh3-128`, or `sha256`). The algorithm
SHALL be recorded in the pool at creation; a mismatching config SHALL be refused
at mount. `cas_blob_hash_allow_new` SHALL be the explicit opt-in that admits a
second algorithm into an existing pool.

#### RQ.SRS-048.CAS.Disk.Backends
version: 1.0

[ClickHouse] SHALL support [CAS] on AWS S3 (`ETag` conditional dialect) and on
the `local` object-storage backend (single-node / demo). Google Cloud Storage
SHALL use the generation-token dialect (`http_client = gcs_hmac` or
`gcp_oauth`). Other S3-compatible stores SHALL be admitted only when the mount
capability probe confirms they enforce conditional operations. Azure Blob is
specified under
[RQ.SRS-048.CAS.Restrictions.Azure](#rqsrs-048casrestrictionsazure).

### Object Model

#### RQ.SRS-048.CAS.ObjectModel
version: 1.0

[ClickHouse] SHALL store [MergeTree] parts on a [CAS] disk as content-addressed
objects in the pool, consisting of blobs, part manifests, refs, and a blob
condemnation-marker sidecar, rather than as ordinary per-table part path copies
alone. There is no [CAS] state in Keeper; pool bookkeeping lives in the bucket.

#### RQ.SRS-048.CAS.ObjectModel.Blobs
version: 1.0

[ClickHouse] SHALL store content-addressed file payloads as immutable blob
objects under a pool-global `blobs/` prefix, keyed by content hash, so identical
bytes MAY be shared across tables and servers in the same pool.

#### RQ.SRS-048.CAS.ObjectModel.Manifests
version: 1.0

[ClickHouse] SHALL store an immutable part manifest that lists the files
belonging to one [MergeTree] part and their blob (or inline) placements.

#### RQ.SRS-048.CAS.ObjectModel.Refs
version: 1.0

[ClickHouse] SHALL maintain logical mutable refs that map part names to
manifests. Refs SHALL be the mutable layer that changes when parts are created,
merged, mutated, or dropped. Their physical state SHALL use the append-only
ref-stream representation specified by
[RQ.SRS-048.CAS.ObjectModel.PhysicalRefs](#rqsrs-048casobjectmodelphysicalrefs).

#### RQ.SRS-048.CAS.ObjectModel.Immutability
version: 1.0

[ClickHouse] SHALL treat blobs and manifests as immutable after publish. Logical
part changes SHALL produce new parts (and therefore new manifests / ref updates)
rather than rewriting existing blob or manifest identities in place.

#### RQ.SRS-048.CAS.ObjectModel.PhysicalRefs
version: 1.1

[ClickHouse] SHALL persist logical refs as append-only `_log` records with
compacted `_snap` snapshots and `_ckpt` checkpoints under opaque namespace
`life_id` values. Dropping and recreating a logical namespace name SHALL mint a
new `life_id`; an old physical life SHALL NOT alias the new namespace.
`cas_server_root_id` SHALL root ownership, manifest, loose-root, and staging
subtrees, but SHALL NOT be embedded in ref-stream keys.

A namespace runtime admitted from a cold path SHALL NOT be published for a
life retired while that admission was in flight, and a runtime whose recovered
state is terminal SHALL be refused. A retirement observed during a cold
admission SHALL make the admission fail with a retryable error that re-reads
the catalog, so a table dropped and re-created under the same UUID SHALL NOT
acknowledge files into a dead life that the janitor then deletes.

#### RQ.SRS-048.CAS.ObjectModel.Catalog
version: 1.0

[ClickHouse] SHALL keep one pool-wide namespace catalog object as the sole
authority for which namespaces exist, read on every [GC] fold round and every
ref-table recovery and mutated by one token-compare-and-swap write per
lifecycle transition. Its entries SHALL be canonically ordered by namespace
bytes, strictly ascending and without a duplicate name, enforced by both the
encoder and the decoder, so an out-of-order or duplicate-keyed catalog SHALL
NOT become durable.

Each row SHALL carry the namespace name, a state of `Creating`, `Live`, or
`Removing`, a nonzero never-reused `life_id`, the creating writer's fence
identity (required for `Creating`, forbidden otherwise), and the [GC] round
observed when removal began (required for `Removing`, absent otherwise). State
values SHALL be append-only on the wire, never renumbered or repurposed, so a
catalog written by one build stays readable by another.

A row SHALL advance `Creating` to `Live` to `Removing` to absent. A stalled
`Creating` row SHALL NOT be stolen while its creator fence is still live, and
SHALL be completed by a fresh opener only once that fence is provably dead. A
namespace name SHALL become creatable again only after its previous row is
completely gone, and SHALL then take a brand-new `life_id`.

#### RQ.SRS-048.CAS.ObjectModel.FormatGeneration
version: 1.0

[ClickHouse] SHALL record a `min_reader_generation` in the pool and SHALL
refuse to mount a pool whose recorded generation is newer than the generation
this build can read. A ref log that carries a record of a generation above 1
(currently `Move`, see
[RQ.SRS-048.CAS.Write.PartRename](#rqsrs-048caswritepartrename)) SHALL be
stamped with that generation, and the first writable mount by a build that
emits it SHALL raise the pool's `min_reader_generation` once. Raising the
generation SHALL be one-way, so a build that predates it can no longer mount
that pool and operators SHALL upgrade every server in a pool before the first
writable mount.

#### RQ.SRS-048.CAS.ObjectModel.ManifestLimits
version: 1.0

[ClickHouse] SHALL apply write-path backpressure before publishing a part
manifest and reject one that exceeds any documented limit: 1,048,576 entries,
256 MiB of encoded text, 16 MiB of total inline content, or 1 MiB for one
inline entry.

### Write Path

#### RQ.SRS-048.CAS.Write.Publish
version: 1.1

[ClickHouse] SHALL publish one logical part in this durable order:

1. stage and create the immutable manifest;
2. append the ref precommit;
3. materialize or adopt every required blob;
4. promote the precommit to a committed ref.

Promotion SHALL validate the live precommit and its dependency proofs. It
SHALL reuse the proof recorded when the manifest was staged instead of reading
the manifest back, and cleanup of an abandoned staged manifest SHALL delete it
by the recorded incarnation without a preliminary `HEAD`. Manifest staging
SHALL NOT race the orphan sweep into deleting a committed manifest. An
unresolved append or promotion SHALL be treated as an uncertain outcome and
reconciled or retried; it SHALL NOT be treated as proof that the write did not
land. Which of the three commit outcomes a failure reports is specified by
[RQ.SRS-048.CAS.Write.CommitOutcome](#rqsrs-048caswritecommitoutcome).

#### RQ.SRS-048.CAS.Write.BlobMaterialization
version: 2.0

[ClickHouse] SHALL begin each blob materialization attempt with `HEAD` and
SHALL adopt a present body only when the freshness marker read after that
`HEAD` reads `Clean`. A present body whose marker is absent SHALL be
republished like an absent body and SHALL NOT be adopted by backfilling the
marker: [GC] can delete a body and then its marker between the two reads, so
an absent marker is not proof that the body is live. A `Condemned` body SHALL
be republished under a new incarnation. An absent body SHALL be published
unconditionally, and a retry SHALL restart from `HEAD`. A backend token used
for exact deletion SHALL continue to identify the same content for that
incarnation (`TOKEN` implies `CONTENT`). A publication started on an absent
marker SHALL be counted in `CASMetaAbsentRepublish`.

[GC] SHALL remove a condemned marker together with its body even when the
graduation gate re-stamped that marker at a later round, so a marker SHALL NOT
outlive the body it describes.

#### RQ.SRS-048.CAS.Write.BlobPublishRetries
version: 1.0

[ClickHouse] SHALL send each object-creating request of a blob publication at
most once. `PutObject`, `CopyObject`, and `CompleteMultipartUpload` SHALL NOT
be resent by the object-storage client, because a resend carries the same
bytes and therefore the same backend token, which can resurrect an incarnation
that [GC] has already condemned and deleted and leave a committed reference
without data. `CreateMultipartUpload`, `UploadPart`, and `UploadPartCopy`
SHALL keep their ordinary retries, so a large multipart blob still survives
throttling. A copy made under the single-attempt rule SHALL use native
same-store copy only and SHALL reject any other copy mode with
`BAD_ARGUMENTS`.

Retry SHALL happen one level up: the [CAS] publish loop SHALL re-observe the
key per
[RQ.SRS-048.CAS.Write.BlobMaterialization](#rqsrs-048caswriteblobmaterialization)
and publish a fresh envelope under a new incarnation tag. Each failed attempt
SHALL be counted in `CASBlobPublishAttemptFailed`, and a publication that ends
in an exception after a failed attempt in `CASBlobPublishGaveUp`. The first
failed attempt SHALL be logged below `Warning`, so a single retried failure
does not reach a client that requested warning-level logs.

#### RQ.SRS-048.CAS.Write.CommitOutcome
version: 1.0

[ClickHouse] SHALL state, in the error of a failed ref-log commit, which of
three outcomes applies, so a client can tell whether retrying may duplicate
the write:

* the transaction is durable and only the `_ckpt` frontier publish failed;
* the outcome is unknown;
* the write is not durable.

The original error SHALL be kept inside that message. A give-up while
publishing the checkpoint SHALL report its real cause — policy deadline,
lease deadline, or unresolved — rather than a generic contention message.
This requirement constrains the message, not the behavior: error codes for
`DB::Exception` SHALL be unchanged.

#### RQ.SRS-048.CAS.Write.PartRename
version: 1.0

[ClickHouse] SHALL rename a committed part on a [CAS] disk with a single
ref-log owner `Move` record rather than by republishing the part manifest, so
a rename costs no additional manifest write and no ref drop. A ref log that
carries a `Move` SHALL be stamped manifest format generation 2 per
[RQ.SRS-048.CAS.ObjectModel.FormatGeneration](#rqsrs-048casobjectmodelformatgeneration).
An ownership conflict raised on that path SHALL use `CAS_OWNERSHIP_CONFLICT`
and SHALL be counted in `CASOwnershipConflict`.

#### RQ.SRS-048.CAS.Write.HashCollision
version: 1.0

[ClickHouse] SHALL use hash equality as blob identity and SHALL NOT claim that a
`HEAD`-only adoption compares the stored body with the incoming payload.
`cityhash128` SHALL remain the compatibility default, while `sha256` SHALL be
the documented choice when mutually untrusted writers share a pool or
collision resistance is required.

### Read Path

#### RQ.SRS-048.CAS.Read
version: 1.0

[ClickHouse] SHALL resolve a part ref to its immutable manifest and serve each
file from its manifest entry. Inline entries SHALL require no additional
object-store request. Blob entries SHALL use a ranged `GET` bounded to the blob
payload, excluding the blob envelope. Verbatim files SHALL use a plain object
read.

#### RQ.SRS-048.CAS.Read.ManifestValidation
version: 1.0

[ClickHouse] SHALL read and validate a manifest body before caching it. A live
ref naming a missing manifest SHALL raise `FILE_DOESNT_EXIST`; a manifest whose
decoded `ref` or `root_namespace_id` does not match the requested manifest key
SHALL raise `CORRUPTED_DATA`.

#### RQ.SRS-048.CAS.Read.Caches
version: 1.0

[ClickHouse] SHALL cache decoded manifests by immutable `ManifestId` and
part-folder views by part-ref key. A validated cache hit SHALL perform no
object-store request. Setting `cas_manifest_decode_cache_bytes = 0` or
`cas_part_folder_cache_bytes = 0` SHALL disable the corresponding retention
without weakening validation. Promote and repoint SHALL invalidate the
part-folder view, and concurrent cold readers of one view SHALL coalesce into a
single build.

#### RQ.SRS-048.CAS.Read.DirectoryProbes
version: 1.0

[ClickHouse] SHALL answer `existsDirectory` and `listDirectory` inside a
resolved part from the part manifest: a plain file is not a directory, while a
nested directory exists and lists its children. These probes SHALL NOT issue
an object-store `LIST`. Paths that cannot be resolved as a part MAY use the
ordinary listing fallback. Part-load listing cost SHALL not grow with the
number of files in each part.

#### RQ.SRS-048.CAS.Read.InFlight
version: 1.0

A part still inside an open write transaction SHALL NOT be visible through the
ordinary ref resolve. [ClickHouse] SHALL serve a read of such a part through
the explicit read-your-writes overlay of that transaction, so a writer sees its
own uncommitted files while other readers do not. The bare part directory
SHALL report as absent in that overlay, so cleanup of a rejected temporary part
is never mistaken for a real, resolvable part.

#### RQ.SRS-048.CAS.Read.ReadOnly
version: 1.0

A read-only or diagnostic [CAS] opener SHALL NOT claim mount ownership,
schedule [GC], or mint writer state. The backend SHALL reject mutating metadata
operations with a `READONLY`-class error even when a caller bypasses an
ordinary facade check.

### MergeTree Compatibility

[CAS] is a transparent storage backend for the [MergeTree] family: SQL surface
and logical part semantics remain those of [MergeTree]; only the physical layout
differs. Unless a requirement in
[Restrictions And Non-Goals](#restrictions-and-non-goals) says otherwise,
features that work for [MergeTree] on ordinary object-storage disks SHALL work
on [CAS].

#### RQ.SRS-048.CAS.MergeTree
version: 1.0

[ClickHouse] SHALL support the [MergeTree] engine family on a [CAS] disk without
requiring CAS-specific DDL beyond disk / policy selection.

#### RQ.SRS-048.CAS.MergeTree.Transparency
version: 1.0

[ClickHouse] SHALL preserve ordinary [MergeTree] logical behavior for tables on
a [CAS] disk. User-visible query results, part lifecycle semantics, and
supported `ALTER` / partition operations SHALL match non-CAS [MergeTree] unless
an explicit [CAS] restriction applies. [CAS] MUST NOT invent a separate SQL
dialect for everyday table use.

#### RQ.SRS-048.CAS.MergeTree.Engines
version: 1.0

[ClickHouse] SHALL support the mainstream [MergeTree] engine family on a [CAS]
disk, including at least:

* `MergeTree`
* `ReplicatedMergeTree`
* `ReplacingMergeTree` / `ReplicatedReplacingMergeTree`
* `SummingMergeTree` / `ReplicatedSummingMergeTree`
* `AggregatingMergeTree` / `ReplicatedAggregatingMergeTree`
* `CollapsingMergeTree` / `ReplicatedCollapsingMergeTree`
* `VersionedCollapsingMergeTree` / `ReplicatedVersionedCollapsingMergeTree`

#### RQ.SRS-048.CAS.MergeTree.InsertSelect
version: 1.0

[ClickHouse] SHALL support `INSERT` and `SELECT` on [MergeTree] tables stored on
a [CAS] disk with the same logical results as on a non-CAS disk for the same
data.

#### RQ.SRS-048.CAS.MergeTree.Merge
version: 1.0

[ClickHouse] SHALL support merges (`OPTIMIZE` / background merges) of parts on a
[CAS] disk. After merge, logical table contents SHALL remain correct and unused
source parts SHALL become eligible for [GC] reclaim when no longer referenced.

#### RQ.SRS-048.CAS.MergeTree.Replicated
version: 1.0

[ClickHouse] SHALL support `ReplicatedMergeTree` tables on a shared [CAS] pool
so that replicas converge to the same logical data while each replica owns its
own ref namespace under a distinct `cas_server_root_id`.

#### RQ.SRS-048.CAS.MergeTree.PartTypes
version: 2.0

[ClickHouse] SHALL support Wide, Compact, and Packed [MergeTree] parts on a
[CAS] disk. Projections, patch parts, detached parts, temporary parts, and
frozen/shadow parts SHALL be representable in the [CAS] object model.

#### RQ.SRS-048.CAS.MergeTree.Alter.Schema
version: 1.0

[ClickHouse] SHALL support schema-changing `ALTER TABLE` operations on
[CAS]-backed [MergeTree] tables (for example add / drop / modify / rename
column, codec changes) with the same logical outcome as on non-CAS storage,
implemented via the ordinary new-part / drop-old-part [MergeTree] path.
The full [MergeTree] `ALTER TABLE` catalog is specified under
[RQ.SRS-048.CAS.MergeTree.Alter](#rqsrs-048casmergetreealter).

#### RQ.SRS-048.CAS.MergeTree.Mutations
version: 1.0

[ClickHouse] SHALL support mutations on [CAS]-backed [MergeTree] tables. Where
Wide-part carry-forward applies, unchanged column blobs MAY be re-referenced
without re-upload; logical mutation results SHALL match non-CAS behavior.

#### RQ.SRS-048.CAS.MergeTree.LightweightDelete
version: 1.0

[ClickHouse] SHALL support lightweight deletes on [CAS]-backed [MergeTree]
tables with correct logical visibility of deleted rows.

#### RQ.SRS-048.CAS.MergeTree.PatchParts
version: 1.0

[ClickHouse] SHALL support patch parts on [CAS]-backed [MergeTree] tables and
SHALL preserve patch-part durability across server restart.

#### RQ.SRS-048.CAS.MergeTree.Projections
version: 1.0

[ClickHouse] SHALL support [MergeTree] projections on a [CAS] disk. Projection
files SHALL be stored as nested entries of the parent part manifest (not as an
independently GC'd projection ref namespace), and projection query results SHALL
match non-CAS behavior.

#### RQ.SRS-048.CAS.MergeTree.TTL
version: 1.0

[ClickHouse] SHALL support TTL delete and TTL move rules on [CAS]-backed
[MergeTree] tables with correct logical data removal or relocation semantics.
Cross-disk TTL / `MOVE PARTITION ... TO DISK|VOLUME` onto or off [CAS] MAY be
subject to additional verification constraints documented under restrictions.

#### RQ.SRS-048.CAS.MergeTree.Transactions
version: 1.0

[ClickHouse] SHALL support [MergeTree] transactions / MVCC metadata on a [CAS]
disk through the content-addressed transactional mutable-file capability, so
that transaction metadata files (for example `txn_version.txt`) are carried as
ordinary manifest entries and atomically repointed with the part ref.

#### RQ.SRS-048.CAS.MergeTree.RestartDurability
version: 1.0

[ClickHouse] SHALL preserve committed [CAS]-backed table data and applicable
mutation / patch-part / projection state across ClickHouse server restart.

#### RQ.SRS-048.CAS.MergeTree.Rename
version: 1.0

[ClickHouse] SHALL support `RENAME TABLE` by republishing every ref and
verbatim file into the destination namespace and then dropping the old
namespace. The operation SHALL be idempotent and re-drivable after failure, but
need not be atomic across the two namespaces.

#### RQ.SRS-048.CAS.MergeTree.Alter
version: 1.0

[ClickHouse] SHALL support the documented `ALTER TABLE` modifiers for the
[MergeTree] family on a [CAS] disk with the same logical outcome as on
non-CAS [MergeTree] storage, except where this [SRS] lists a restriction.
There SHALL be no [CAS]-specific SQL dialect for these commands.

The catalog follows the upstream [ALTER](https://clickhouse.com/docs/reference/statements/alter)
index. Commands that create mutations (`UPDATE`, `DELETE`, `MATERIALIZE *`,
`CLEAR INDEX` / `CLEAR STATISTICS` / `CLEAR PROJECTION`, `APPLY DELETED MASK`,
`APPLY PATCHES`, `REWRITE PARTS`, and similar) SHALL rewrite parts through the
ordinary [MergeTree] mutation path (new parts / new refs). Metadata-only
commands SHALL not invent a separate [CAS] rewrite of immutable blobs.

Partition commands are additionally gated by
[RQ.SRS-048.CAS.Partition.AlterAllowList](#rqsrs-048caspartitionalterallowlist).
View, RBAC, named-collection, and `ALTER DATABASE` statements are out of
scope for [CAS] table storage.

#### RQ.SRS-048.CAS.MergeTree.Alter.Column
version: 1.0

[ClickHouse] SHALL support column `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `ADD COLUMN [IF NOT EXISTS] ... [AFTER ... | FIRST]`
* `DROP COLUMN [IF EXISTS] ...`
* `RENAME COLUMN [IF EXISTS] ... TO ...`
* `CLEAR COLUMN [IF EXISTS] ... IN PARTITION ...`
* `COMMENT COLUMN [IF EXISTS] ...`
* `MODIFY COLUMN` / `ALTER COLUMN ... TYPE` (type, default, codec, TTL,
  statistics, column settings, `FIRST` / `AFTER`)
* `MODIFY COLUMN ... REMOVE` (`DEFAULT`, `ALIAS`, `MATERIALIZED`, `CODEC`,
  `COMMENT`, `TTL`, `SETTINGS`)
* `MODIFY COLUMN ... MODIFY SETTING ...`
* `MODIFY COLUMN ... RESET SETTING ...`
* `MODIFY COLUMN ... ADD ENUM VALUES ...`
* `MATERIALIZE COLUMN ... [IN PARTITION ... | IN PARTITION ID ...]`

Logical results SHALL match non-CAS [MergeTree]. `MATERIALIZE COLUMN` SHALL
be implemented as a mutation. Key-column rename / type-change limitations
SHALL match upstream [MergeTree] (not [CAS]-specific).

#### RQ.SRS-048.CAS.MergeTree.Alter.Update
version: 1.0

[ClickHouse] SHALL support heavyweight

```sql
ALTER TABLE [db.]table UPDATE column1 = expr1 [, ...] [IN PARTITION partition_expr] WHERE filter_expr
```

on [CAS]-backed [MergeTree] tables as a mutation. Logical updated values
SHALL match non-CAS behavior. Updating columns used in the primary or
partition key SHALL remain unsupported, as on non-CAS [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.Delete
version: 1.0

[ClickHouse] SHALL support heavyweight

```sql
ALTER TABLE [db.]table DELETE [IN PARTITION partition_expr] WHERE filter_expr
```

on [CAS]-backed [MergeTree] tables as a mutation. Logical row removal SHALL
match non-CAS behavior. This requirement covers `ALTER TABLE ... DELETE`,
not `DELETE FROM` lightweight deletes
([RQ.SRS-048.CAS.MergeTree.LightweightDelete](#rqsrs-048casmergetreelightweightdelete)).

#### RQ.SRS-048.CAS.MergeTree.Alter.OrderBy
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MODIFY ORDER BY ...` on
[CAS]-backed [MergeTree] tables as a metadata-only change of the sorting
key (primary key unchanged), with the same restrictions as non-CAS
[MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.SampleBy
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MODIFY SAMPLE BY ...` and
`ALTER TABLE ... REMOVE SAMPLE BY` on [CAS]-backed [MergeTree] tables as
metadata-only sampling-key changes, with the same primary-key containment
rules as non-CAS [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.Index
version: 1.0

[ClickHouse] SHALL support data-skipping-index `ALTER TABLE` actions on
[CAS]-backed [MergeTree] tables:

* `ADD INDEX [IF NOT EXISTS] ... TYPE ... [GRANULARITY ...] [FIRST | AFTER ...]`
* `DROP INDEX [IF EXISTS] ...`
* `MATERIALIZE INDEX [IF EXISTS] ... [IN PARTITION ...]`
* `CLEAR INDEX [IF EXISTS] ... [IN PARTITION ...]`

`ADD INDEX` SHALL update metadata. `MATERIALIZE INDEX`, `DROP INDEX`, and
`CLEAR INDEX` SHALL follow upstream mutation / file-removal semantics.
Logical skip-index behavior SHALL match non-CAS [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.Projection
version: 1.0

[ClickHouse] SHALL support projection `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `ADD PROJECTION [IF NOT EXISTS] ...`
* `DROP PROJECTION [IF EXISTS] ...`
* `MATERIALIZE PROJECTION [IF EXISTS] ... [IN PARTITION ...]`
* `CLEAR PROJECTION [IF EXISTS] ... [IN PARTITION ...]`
* `MODIFY PROJECTION [IF EXISTS] ... ( SELECT ... ) WITH SETTINGS (...)`

Projection files SHALL remain nested entries of the parent part manifest
([RQ.SRS-048.CAS.MergeTree.Projections](#rqsrs-048casmergetreeprojections)).
Query results that use the projection SHALL match non-CAS behavior.

`MODIFY PROJECTION` only applies to [ClickHouse] >= 26.9, where the command
was added to the parser. Older builds, including the 26.6-based Antalya
build, reject it with `SYNTAX_ERROR` on non-CAS [MergeTree] as well, so
scenarios covering it SHALL be skipped there.

#### RQ.SRS-048.CAS.MergeTree.Alter.Constraint
version: 1.0

[ClickHouse] SHALL support constraint `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `ADD CONSTRAINT [IF NOT EXISTS] ... {CHECK | ASSUME} ...`
* `DROP CONSTRAINT [IF EXISTS] ...`
* `MODIFY CONSTRAINT [IF EXISTS] ... {CHECK | ASSUME} ...`

These commands SHALL change table metadata immediately and SHALL NOT
re-check existing rows, matching non-CAS [MergeTree].

`MODIFY CONSTRAINT` only applies to [ClickHouse] >= 26.7, where the command
was added to the parser. Older builds, including the 26.6-based Antalya
build, reject it with `SYNTAX_ERROR` on non-CAS [MergeTree] as well, so
scenarios covering it SHALL be skipped there.

#### RQ.SRS-048.CAS.MergeTree.Alter.TTL
version: 1.0

[ClickHouse] SHALL support table-TTL `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `MODIFY TTL ...`
* `REMOVE TTL`
* `MATERIALIZE TTL`

`MODIFY TTL` / `REMOVE TTL` SHALL update metadata. `MATERIALIZE TTL` SHALL
force TTL application as a mutation. Column TTL SHALL be covered by
`MODIFY COLUMN ... TTL` /
[RQ.SRS-048.CAS.MergeTree.Alter.Column](#rqsrs-048casmergetreealtercolumn).
Logical delete / move-to-volume TTL semantics SHALL match
[RQ.SRS-048.CAS.MergeTree.TTL](#rqsrs-048casmergetreettl).

#### RQ.SRS-048.CAS.MergeTree.Alter.Statistics
version: 1.0

[ClickHouse] SHALL support column-statistics `ALTER TABLE` actions on
[CAS]-backed [MergeTree] tables:

* `ADD STATISTICS [IF NOT EXISTS] ... TYPE ...`
* `MODIFY STATISTICS ... TYPE ...`
* `DROP STATISTICS [IF EXISTS] ...`
* `CLEAR STATISTICS [IF EXISTS] ...`
* `MATERIALIZE STATISTICS (ALL | [IF EXISTS] ...)`

Metadata commands SHALL match non-CAS behavior. `MATERIALIZE STATISTICS`
and `CLEAR STATISTICS` SHALL follow upstream mutation semantics.

#### RQ.SRS-048.CAS.MergeTree.Alter.Setting
version: 1.0

[ClickHouse] SHALL support table-setting `ALTER TABLE` actions on
[CAS]-backed [MergeTree] tables:

* `MODIFY SETTING setting_name = value [, ...]`
* `RESET SETTING setting_name [, ...]`

These commands SHALL apply only to [MergeTree] table settings, matching
non-CAS behavior.

#### RQ.SRS-048.CAS.MergeTree.Alter.Comment
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MODIFY COMMENT '...'` on
[CAS]-backed [MergeTree] tables, including clearing the comment with an
empty string. On `ReplicatedMergeTree`, comment changes MAY remain
replica-local, matching upstream [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.ApplyDeletedMask
version: 1.0

[ClickHouse] SHALL support

```sql
ALTER TABLE [db.]table APPLY DELETED MASK [IN PARTITION partition_id]
```

on [CAS]-backed [MergeTree] tables as a mutation that physically removes
rows marked by lightweight delete (`_row_exists = 0`), with the same
logical outcome as on non-CAS storage.

#### RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches
version: 1.0

[ClickHouse] SHALL support

```sql
ALTER TABLE [db.]table APPLY PATCHES [IN PARTITION partition_id]
```

on [CAS]-backed [MergeTree] tables as a mutation that materializes pending
lightweight-update patch parts into data parts, with the same logical
outcome as on non-CAS storage.

#### RQ.SRS-048.CAS.MergeTree.MaterializedView
version: 1.0

[ClickHouse] SHALL support materialized views when the source table, the
`TO` destination, or the view's inner [MergeTree] is stored on a [CAS] disk.
Logical results SHALL match non-CAS [MergeTree].

* `INSERT` into the source SHALL apply the view `SELECT` and write that
  result to the `TO` table, or to the inner table when the view declares
  its own `ENGINE`. Parts SHALL land on the destination table's disk or
  storage policy, which MAY differ from the source.
* `POPULATE` SHALL load rows already in the source into a view that
  declares its own `ENGINE`. A later `INSERT` SHALL append only the new
  result. Declaring both `TO` and `POPULATE` SHALL be rejected, matching
  non-CAS [MergeTree].
* A `SELECT` that filters, rewrites, or joins another [CAS] table SHALL
  write that result, including aggregate states into an
  `AggregatingMergeTree` destination. `SummingMergeTree` and
  `ReplacingMergeTree` destinations SHALL collapse view-written rows on
  merge, and a destination projection SHALL be built for view-written parts.
* Several views on one source, and a view whose source is another view's
  destination, SHALL each receive the insert, with or without
  `parallel_view_processing`.
* A multi-block `INSERT ... SELECT` and concurrent inserts into the source
  SHALL write every row to the destination exactly once.
* If the view `SELECT` throws, the `INSERT` SHALL fail and the destination
  SHALL not receive that block. The source keeps the block, matching
  non-CAS [MergeTree]. With `materialized_views_ignore_errors` the insert
  SHALL succeed without writing to the failing view. Both tables SHALL pass
  `CHECK TABLE` afterwards.
* A retried insert that the source deduplicates (by
  `insert_deduplication_token` with `non_replicated_deduplication_window`,
  or by a `ReplicatedMergeTree` retry on another replica) SHALL NOT write
  the block to the destination again.
* `ALTER TABLE ... MODIFY QUERY` SHALL change what later inserts write.
  `DETACH` / `ATTACH` and `RENAME` of the view, and a server restart, SHALL
  keep the rows on its [CAS] storage and SHALL keep later inserts
  propagating
  ([RQ.SRS-048.CAS.MergeTree.RestartDurability](#rqsrs-048casmergetreerestartdurability),
  [RQ.SRS-048.CAS.MergeTree.Rename](#rqsrs-048casmergetreerename)).
* `DETACH`, `ATTACH`, `MOVE PARTITION ... TO TABLE`, and `DROP PARTITION`
  on a [CAS] destination SHALL work while the view keeps writing to it.
* A refreshable view SHALL replace a [CAS] `TO` table or inner table with
  the current result on each refresh, or add the result with `APPEND`.
  Refreshing identical bytes SHALL keep sharing one blob through [GC].
* `ALTER TABLE ... UPDATE`, `ALTER TABLE ... DELETE`, and lightweight
  `DELETE` on the source SHALL leave rows the view already wrote unchanged.
* Lightweight `UPDATE` SHALL write a patch part on the [CAS] table it
  targets, whether that is the source, the `TO` destination, or the inner
  table, and SHALL NOT change the other side. The table needs
  `enable_block_number_column` and `enable_block_offset_column`, matching
  non-CAS [MergeTree]. A read SHALL return the
  patched values. The same read with `apply_patch_parts = 0` SHALL return
  the part as it was inserted. `ALTER TABLE ... APPLY PATCHES` SHALL fold
  the patch into a data part on [CAS]. The patch part MAY stay active
  afterwards, matching non-CAS [MergeTree]. The patch part SHALL survive a
  server restart. Patching a column SHALL NOT rewrite a blob the other
  table still shares
  ([RQ.SRS-048.CAS.MergeTree.PatchParts](#rqsrs-048casmergetreepatchparts),
  [RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches](#rqsrs-048casmergetreealterapplypatches)).
* With `check_referential_table_dependencies` enabled, `DROP` of the
  source or the destination SHALL be rejected while the view still
  references that table. With the setting left at its default, that `DROP`
  is allowed, matching non-CAS [MergeTree]. `DROP` of the view SHALL stop
  later inserts from propagating and SHALL leave both tables queryable.
  After the view is gone, `DROP` of the source SHALL leave the destination
  readable.
* Identical column bytes the view writes into the same pool SHALL share a
  blob with the source
  ([RQ.SRS-048.CAS.ObjectModel.Blobs](#rqsrs-048casobjectmodelblobs)).
  Different bytes SHALL be stored again. [GC] SHALL NOT delete a blob the
  destination still names
  ([RQ.SRS-048.CAS.GC.NoLoss](#rqsrs-048casgcnoloss)), and SHALL reclaim it
  after the last owner is dropped
  ([RQ.SRS-048.CAS.GC.ReclaimAfterDrop](#rqsrs-048casgcreclaimafterdrop)),
  including after `TRUNCATE` and after `DROP` of a view, which drops its
  inner table. A blob that [GC] has condemned but not yet deleted SHALL be
  kept when the view writes the same bytes again, and [GC] rounds that
  overlap inserts through the view SHALL NOT lose data.
  A view that writes into a different pool SHALL publish into that pool,
  and reclaiming one pool SHALL leave the other pool's copy readable.
* With `ReplicatedMergeTree` source and destination, creating the view on
  every replica SHALL make an `INSERT` on one replica visible in the
  destination on every replica after replication. A replicated inner
  table on [CAS] SHALL replicate the same way.
* An `INSERT` through a `Distributed` table SHALL run each shard's view on
  the rows routed to that shard.

Merges of parts the view wrote are specified by
[RQ.SRS-048.CAS.MergeTree.Merge](#rqsrs-048casmergetreemerge).

### Partition And Part Operations

Same-disk / same-pool partition and part DDL MUST remain correct on [CAS]
tables. The product allow-list in `MergeTreeData::checkAlterPartitionIsPossible`
for `MetadataStorageType::ContentAddressed` is the authoritative gate for which
partition commands are admitted.

Replication-queue relink for the same operations is covered under
[Replication Relink](#replication-relink).

#### RQ.SRS-048.CAS.Partition.AlterAllowList
version: 1.1

[ClickHouse] SHALL allow the following partition commands on a [CAS] disk and
SHALL reject unsupported partition commands fail-closed:

* `DETACH PARTITION` / `DETACH PART`
* `DROP PARTITION` / `DROP PART`
* `DROP DETACHED PARTITION` / `DROP DETACHED PART`
* `FORGET PARTITION`
* `ATTACH PARTITION` / `ATTACH PART`
* `REPLACE PARTITION` / `ATTACH PARTITION ... FROM`
* `MOVE PARTITION` (including `MOVE PARTITION ... TO TABLE`)
* `FETCH PARTITION` / `FETCH PART`
* `FREEZE PARTITION` / `FREEZE`
* `UNFREEZE PARTITION` / `UNFREEZE`
* `EXPORT PART` / `EXPORT PARTITION`
  ([RQ.SRS-048.CAS.Partition.Export](#rqsrs-048caspartitionexport))

`DROP` / `DETACH` / `ATTACH` / `ATTACH FROM` SHALL accept `PARTITION ALL`
where upstream [MergeTree] does. Partition-scoped mutations
(`CLEAR COLUMN` / `CLEAR INDEX`, `UPDATE` / `DELETE IN PARTITION`,
`REWRITE PARTS`) are specified under the following requirements and are
not limited to this allow-list when they use the ordinary mutation path.

#### RQ.SRS-048.CAS.Partition.Replace
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... REPLACE PARTITION ... FROM ...`
between [MergeTree] tables on the same [CAS] pool with correct partition
contents on the destination and without deleting the replaced partition from
the source.

#### RQ.SRS-048.CAS.Partition.AttachFrom
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... ATTACH PARTITION ... FROM ...`
between [MergeTree] tables on the same [CAS] pool so that the destination gains
the partition and the source retains it.

#### RQ.SRS-048.CAS.Partition.Attach
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... ATTACH PARTITION` /
`ATTACH PART` of previously detached parts on a [CAS]-backed table so that
attached data becomes readable and survives restart.

#### RQ.SRS-048.CAS.Partition.Detach
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DETACH PARTITION` /
`DETACH PART` on a [CAS]-backed table so that detached data is no longer
queryable from the active table while remaining available under the detached
namespace for later attach or drop.

#### RQ.SRS-048.CAS.Partition.DetachAttach
version: 1.0

[ClickHouse] SHALL support `DETACH PARTITION` / `ATTACH PARTITION` round-trips
on a [CAS]-backed [MergeTree] table without logical data loss.

#### RQ.SRS-048.CAS.Partition.MoveToTable
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MOVE PARTITION ... TO TABLE ...`
between [MergeTree] tables on the same [CAS] pool so that the partition leaves
the source and appears on the destination with unchanged contents.

#### RQ.SRS-048.CAS.Partition.Drop
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DROP PARTITION` / `DROP PART` on a
[CAS]-backed table. Dropped part refs SHALL be removed and their blobs /
manifests SHALL become eligible for [GC] when no other ownership remains.
Logical drop semantics SHALL match non-CAS [MergeTree] (including documented
weak guarantees when `DROP PART` races a concurrent merge).

#### RQ.SRS-048.CAS.Partition.DropDetached
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DROP DETACHED PARTITION` /
`DROP DETACHED PART` on a [CAS]-backed table when `allow_drop_detached` permits
the command.

#### RQ.SRS-048.CAS.Partition.Forget
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... FORGET PARTITION` on
`ReplicatedMergeTree` tables stored on [CAS]. The command manipulates Keeper
partition metadata and SHALL NOT require rewriting or deleting [CAS] part blobs
as part of the forget itself.

#### RQ.SRS-048.CAS.Partition.Fetch
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... FETCH PARTITION` /
`FETCH PART` (including fetch into detached) for `ReplicatedMergeTree` tables
on a [CAS] disk. When the peer shares the same pool, fetch MAY use relink;
otherwise it SHALL use ordinary byte fetch. Logical fetched data SHALL match
the source.

#### RQ.SRS-048.CAS.Partition.Freeze
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... FREEZE PARTITION` / `FREEZE` on a
[CAS]-backed table by materializing readable file bytes in a separate shadow
namespace. The shadow namespace SHALL be a [GC] reachability root scoped under
the creating server's `cas_server_root_id`, so one server's `UNFREEZE` cannot
reach another server's snapshots in the same pool.

#### RQ.SRS-048.CAS.Partition.Unfreeze
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... UNFREEZE PARTITION` / `UNFREEZE` on
a [CAS]-backed table by removing the corresponding shadow refs without deleting
blobs still referenced by live table ownership.

#### RQ.SRS-048.CAS.Partition.Clone
version: 1.0

[ClickHouse] SHALL support partition / part clone paths used by attach, replace,
and cross-disk operations as one whole-part disk transaction. Same-pool attach
and replace paths MAY republish refs over shared blobs. `FREEZE` SHALL follow
[RQ.SRS-048.CAS.Partition.Freeze](#rqsrs-048caspartitionfreeze) and materialize
its separate shadow namespace.

#### RQ.SRS-048.CAS.Partition.ClearColumn
version: 1.0

[ClickHouse] SHALL support
`ALTER TABLE ... CLEAR COLUMN ... IN PARTITION ...` on a [CAS]-backed
[MergeTree] table, resetting the column in that partition to default
values with the same logical outcome as on non-CAS storage.

#### RQ.SRS-048.CAS.Partition.ClearIndex
version: 1.0

[ClickHouse] SHALL support
`ALTER TABLE ... CLEAR INDEX ... IN PARTITION ...` on a [CAS]-backed
[MergeTree] table, removing skip-index files for that partition without
dropping the index description, matching non-CAS behavior.

#### RQ.SRS-048.CAS.Partition.RewriteParts
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... REWRITE PARTS` and
`ALTER TABLE ... REWRITE PARTS IN PARTITION ...` on a [CAS]-backed
[MergeTree] table, rewriting parts with current table settings and
preserving logical table contents.

#### RQ.SRS-048.CAS.Partition.Update
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... UPDATE ... IN PARTITION ...`
(and `IN PARTITION ID '...'`) on a [CAS]-backed [MergeTree] table as a
partition-scoped mutation, matching
[RQ.SRS-048.CAS.MergeTree.Alter.Update](#rqsrs-048casmergetreealterupdate).

#### RQ.SRS-048.CAS.Partition.Delete
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DELETE IN PARTITION ...`
(and `IN PARTITION ID '...'`) on a [CAS]-backed [MergeTree] table as a
partition-scoped mutation, matching
[RQ.SRS-048.CAS.MergeTree.Alter.Delete](#rqsrs-048casmergetreealterdelete).

#### RQ.SRS-048.CAS.Partition.MoveToDisk
version: 1.0

[ClickHouse] SHALL support
`ALTER TABLE ... MOVE PARTITION|PART ... TO DISK|VOLUME '...'` on
[CAS]-backed [MergeTree] tables when the destination is admitted by the
table storage policy. This is the documented migration path onto and off
[CAS] (including a cache-over-[CAS] disk named in the policy). Moving a
partition off [CAS] SHALL make the abandoned blobs eligible for [GC]
without deleting them synchronously. Commands that the partition
allow-list does not admit SHALL fail closed.

#### RQ.SRS-048.CAS.Partition.Export
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... EXPORT PART` and
`ALTER TABLE ... EXPORT PARTITION` from a [CAS]-backed `ReplicatedMergeTree`
source to a supported destination such as Iceberg, with the same exported rows
as from a non-CAS disk. `partition_exports` SHALL be a reserved table-level
directory, so its descriptor SHALL NOT be parsed as a part name.

### Backup And Restore

#### RQ.SRS-048.CAS.Backup
version: 1.0

[ClickHouse] SHALL support `BACKUP` of [CAS]-backed [MergeTree] tables on Atomic
(UUID) databases via the pointer-holding backup path, preserving logical table
contents for a subsequent restore. This is ordinary [ClickHouse] `BACKUP`, not
the unshipped native [CAS] snapshot / mirror design
([RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot](#rqsrs-048casrestrictionsbackupnativesnapshot)).

#### RQ.SRS-048.CAS.Restore
version: 1.0

[ClickHouse] SHALL support `RESTORE` of [CAS]-backed [MergeTree] table backups
produced through the supported backup path, restoring queryable logical contents
equivalent to the backed-up table.

#### RQ.SRS-048.CAS.Backup.SameEndpointCopy
version: 1.0

[ClickHouse] SHALL back up a [CAS]-backed table to an `S3(...)` or `Disk(...)`
destination that sits on the same S3 endpoint as the pool. Because a blob
entry is a range inside a blob envelope rather than a whole object, the backup
SHALL copy the payload with a ranged server-side copy rather than copying the
envelope. A blob payload of 5 MiB or smaller SHALL fall back to a buffered
read-and-write copy, since S3 ranged part copy has a 5 MiB minimum part size.
Restored contents SHALL match
[RQ.SRS-048.CAS.Restore](#rqsrs-048casrestore).

### Shared Pool

#### RQ.SRS-048.CAS.SharedPool
version: 1.0

[ClickHouse] SHALL allow multiple servers to mount one [CAS] pool concurrently
when each server uses a distinct `cas_server_root_id`.

#### RQ.SRS-048.CAS.SharedPool.Deduplication
version: 1.0

[ClickHouse] SHALL deduplicate identical blob content across servers that share
one pool so that writing the same bytes does not require storing a second pool
copy of that blob.

#### RQ.SRS-048.CAS.SharedPool.IndependentRefs
version: 1.0

[ClickHouse] SHALL keep each server's refs independent under its
`cas_server_root_id` even when those refs resolve to the same shared blobs.

#### RQ.SRS-048.CAS.SharedPool.NodeCrash
version: 1.0

[ClickHouse] SHALL keep the shared pool and surviving servers consistent when
one pool member process crashes or is killed, without corrupting surviving
members' committed data.

#### RQ.SRS-048.CAS.SharedPool.MountRecovery
version: 1.0

[ClickHouse] SHALL fence local writes when mount-lease renewal reaches a
terminal or unresolved outcome, enter the `TransientNotLive` lifecycle, and
schedule self-remount under a fresh `writer_epoch`. Every durable write or
delete SHALL recheck its captured fence generation before completion. A
confirmed foreign holder, successor, same-pair conflict, or fenced epoch SHALL
fail closed and SHALL NOT be adopted as this process's renewal.

#### RQ.SRS-048.CAS.SharedPool.TerminalLifecycle
version: 1.0

[ClickHouse] SHALL treat `identity_lost`, `vanished(replaced)`, and
`vanished(forgotten)` as terminal, absorbing pool lifecycles. A transient
remount SHALL retry with bounded backoff when the probe is inconclusive and
return to `live` only after a valid claim and renewal under the fresh epoch.

### Replication Relink

#### RQ.SRS-048.CAS.Relink
version: 1.0

[ClickHouse] SHALL support fetch-by-relink for `ReplicatedMergeTree` replicas
that mount the same [CAS] pool: a receiving replica MAY publish a local ref to
the sender's manifest instead of transferring all part bytes, when the relink
protocol succeeds. The receiver SHALL advertise the `cas_pool_uuid` of every
writable [CAS] pool in its storage policy, and the sender SHALL offer relink
only when its disk's pool uuid occurs in that set.

#### RQ.SRS-048.CAS.Relink.HappyPath
version: 1.0

[ClickHouse] SHALL complete the relink happy path by publishing the receiver
precommit first, confirming the source still holds the offered manifest, then
promoting the receiver's committed ref. Only a literal confirm-proven answer
SHALL authorize promotion. Logical data SHALL be identical on both replicas
without requiring a full byte copy of already-present blobs.

#### RQ.SRS-048.CAS.Relink.DetachedFetch
version: 1.0

[ClickHouse] SHALL use relink when fetching a part or partition into detached
status on a same-pool replica (`FETCH PART` / `FETCH PARTITION` into detached),
subject to the same pool-identity rules as ordinary fetch.

#### RQ.SRS-048.CAS.Relink.CrossPool.ByteFallback
version: 1.0

[ClickHouse] SHALL fall back to ordinary byte fetch when sender and receiver do
not share the same [CAS] `cas_pool_uuid`, when the sender predates the confirm
protocol, or when a mechanism failure proves that promotion did not commit
(for example an absent precommit or ref conflict). It SHALL not claim a
metadata-only relink in those cases. An unavailable or unproven confirmation is
an uncertain outcome governed by
[RQ.SRS-048.CAS.Relink.ConfirmRace](#rqsrs-048casrelinkconfirmrace), not a byte
fallback. Byte-fetched files SHALL still content-address and deduplicate on
arrival.

#### RQ.SRS-048.CAS.Relink.AttachPartitionFrom
version: 1.0

[ClickHouse] SHALL support `ATTACH PARTITION FROM` such that a subsequent
replication queue fetch on a same-pool replica MAY relink rather than copy
bytes, while preserving correct logical partition contents.

#### RQ.SRS-048.CAS.Relink.ReplacePartition
version: 1.0

[ClickHouse] SHALL support `REPLACE PARTITION` on a non-empty destination such
that a subsequent same-pool replica queue fetch MAY relink, while preserving
correct logical partition contents on all replicas.

#### RQ.SRS-048.CAS.Relink.VersionMix
version: 1.0

[ClickHouse] SHALL serve ordinary byte fetch to a peer that cannot participate
in the relink confirm protocol (protocol version below the confirm promise,
currently 11), instead of leaving that peer unable to obtain the part.

#### RQ.SRS-048.CAS.Relink.ConfirmRace
version: 1.0

[ClickHouse] SHALL refuse unsafe promotion when the source cannot prove it still
holds the offered manifest (unproven, missing cookie, timeout, or transport
error). The receiver SHALL throw and retry later and SHALL NOT promote or
immediately re-request bytes from that same uncertain source.

#### RQ.SRS-048.CAS.Relink.StalledPublish
version: 1.0

[ClickHouse] SHALL protect source blobs during a stalled publish and SHALL NOT
commit a receiver ref when promotion cannot complete safely.

#### RQ.SRS-048.CAS.Relink.RecursionBrake
version: 1.0

[ClickHouse] SHALL bound relink recursion: a byte-fetch fallback SHALL re-invoke
the fetch with relink disabled so the receiver stops advertising its pool uuid
and the relink path cannot be entered twice for one fetch.

#### RQ.SRS-048.CAS.Relink.OfferIntegrity
version: 1.0

[ClickHouse] SHALL resolve the sender manifest bytes and confirmation token
from one source-ref view. The receiver SHALL trust only the decoded manifest
entry list from the wire; it SHALL derive the destination namespace and ref
locally and ignore the sender's manifest id, namespace, and payload digest.
Protocol version 11 SHALL mean that the receiver promises to confirm before
promotion.

#### RQ.SRS-048.CAS.Relink.Placement
version: 1.0

For a same-pool offer, [ClickHouse] SHALL place the fetched part on the first
writable policy disk that belongs to the offered pool, ahead of ordinary volume
order, JBOD balancing, `max_data_part_size_bytes`, and TTL destination rules.
TTL placement SHALL be deferred to the background mover. A read-only pool SHALL
be advertised only when another disk for that pool is writable.

#### RQ.SRS-048.CAS.Relink.UnavailableTarget
version: 1.0

When relink placement selects a pool disk whose mount is not live, [ClickHouse]
SHALL fail the fetch and let the replication queue retry. It SHALL NOT silently
choose a different disk and transfer bytes. A peer that predates multi-pool
advertisement MAY use byte fetch during a rolling upgrade.

#### RQ.SRS-048.CAS.Relink.FormatVersion
version: 1.0

[ClickHouse] SHALL fail closed when a relink offer uses an unknown newer
manifest format. Until a documented compatibility path exists, it SHALL NOT
silently degrade that offer to byte fetch.

#### RQ.SRS-048.CAS.Relink.GCBackstop
version: 1.0

A successful confirmation SHALL prove only that the source held the exact
manifest at confirm time; it SHALL NOT be interpreted as proof that a later
[GC] fold observed the receiver's new edge through an eventually consistent
listing. `cas-fsck` SHALL detect and report a reachable-but-absent object as the
operator backstop for that documented gap.

### Garbage Collection

#### RQ.SRS-048.CAS.GC
version: 1.0

[ClickHouse] SHALL provide background garbage collection for a [CAS] pool that
reclaims objects no longer named by live ownership.

#### RQ.SRS-048.CAS.GC.NoLoss
version: 1.0

[ClickHouse] SHALL NOT delete a blob or manifest while any committed reference
or required ownership still names it. A dangling reference (live ref, missing
object) SHALL be treated as a data-loss invariant violation.

#### RQ.SRS-048.CAS.GC.ReclaimAfterDrop
version: 1.0

[ClickHouse] SHALL reclaim unreferenced blobs and part metadata after
`DROP TABLE ... SYNC` (and equivalent removal of the last owners) once [GC]
completes, returning the pool prefixes toward an empty / baseline state for
that dropped ownership. Reclamation SHALL require at least two full [GC] rounds
past condemnation (the grace period is measured in rounds, not acks); a single
manual `SYSTEM CAS GC RUN` SHALL NOT finish physical delete by itself.

#### RQ.SRS-048.CAS.GC.Run
version: 1.0

[ClickHouse] SHALL support a manual synchronous GC round via

```sql
SYSTEM CAS GC RUN [ON CLUSTER cluster_name] [disk_name];
```

When `disk_name` is omitted, one round SHALL run on every [CAS] disk on the
node. A manual run SHALL execute even if `SYSTEM CAS GC STOP` has paused the
background scheduler. It MAY acquire or renew GC leadership but SHALL NOT steal
leadership from a live leader. The command SHALL return one row per disk with
`disk`, `acquired_lease`, `deferred`, `round`, `candidates_marked`,
`objects_deleted`, `objects_absent`, `objects_replaced`, `objects_spared`,
`manifests_deleted`, `entries_condemned`, `entries_graduated`,
`entries_redeleted`, `entries_redelete_failed`, `fence_outs`, `anomalies`, and
`pending_candidates`, `pending_condemned`, and `pending_retired`.

#### RQ.SRS-048.CAS.GC.Rebuild
version: 1.0

[ClickHouse] SHALL support reconstructing conservative GC baseline state via

```sql
SYSTEM CAS GC REBUILD [FORCE] [ON CLUSTER cluster_name] disk_name;
```

and/or offline `clickhouse-disks ... cas-gc-rebuild`. `disk_name` SHALL be
required (no fan-out across every [CAS] disk). Rebuild SHALL refuse when
existing `gc/state` looks healthy unless `FORCE` is given, and SHALL refuse
(regardless of `FORCE`) when another GC leader holds the disk's lease.
Rebuild SHALL write only the GC plane and SHALL fail closed rather than delete
uncertain content; temporary over-protection (leaks) is preferred over data
loss. Rebuild SHALL be documented as disaster recovery: it does not directly
delete blobs, but incorrect rebuilt bookkeeping can authorize deletion in later
ordinary rounds.

#### RQ.SRS-048.CAS.GC.Sharded
version: 1.0

[ClickHouse] SHALL support sharded GC (`cas_gc_shards > 1`) such that GC work is
partitioned across shard buckets, completion is sealed per generation, and
reclaim remains free of dangle/loss under multi-replica pool use.
`cas_gc_shards` SHALL be recorded in the pool at first lease acquire; a
mismatching config SHALL be refused at mount.

#### RQ.SRS-048.CAS.GC.RefSnaplog
version: 1.0

[ClickHouse] SHALL implement the snapshot+log ref protocol lifecycle so that
after insert churn and table drop, unreclaimed objects become reclaimable and a
read-only `cas-fsck` pass can report a clean pool for the inspected window.

#### RQ.SRS-048.CAS.GC.StopStart
version: 1.0

[ClickHouse] SHALL support pausing and resuming the background GC scheduler on
one disk without affecting reads or writes:

```sql
SYSTEM CAS GC STOP [ON CLUSTER cluster_name] disk_name;
SYSTEM CAS GC START [ON CLUSTER cluster_name] disk_name;
```

`disk_name` SHALL be required. `STOP` SHALL be idempotent, SHALL stop in place
(the same scheduler instance resumes on `START`), and SHALL NOT stop a manual
`SYSTEM CAS GC RUN`. `START` SHALL NOT automatically restore GC leadership.
`STOP` SHALL work on a sick or non-live disk and return no result set. `START`
SHALL reject a decommissioned or uncertain pool with a typed error.

#### RQ.SRS-048.CAS.GC.Phases
version: 1.0

[ClickHouse] SHALL expose the current GC pipeline through ordered `Phase` rows
using these documented phase values:

1. `lease`
2. `pre_fold_ref_drain`
3. `heartbeat_floor`
4. `defer_decision`
5. `parent_seal_read`
6. `fold_ref_group`
7. `fold_seal_read`
8. `fold_ref_intake`
9. `fold_reduce`
10. `fold_seal_write`
11. `pending_deletes`
12. `meta_pool_wait`
13. `round_commit`
14. `handoff_reclaim`
15. `manifest_deletes`
16. `namespace_cleanup`
17. `ref_object_cleanup`
18. `orphan_sweep`

A follower SHALL emit only the phases it reaches and stop after `lease`. A
deferred leader round SHALL still drain eligible pre-fold work and run one
suppressed namespace-cleanup page, but SHALL not publish a fold generation.

#### RQ.SRS-048.CAS.GC.Budgets
version: 1.0

[ClickHouse] SHALL support the documented GC work controls:

* `cas_manifest_sweep_list_budget_keys`
* `cas_manifest_sweep_delete_budget_keys`
* `cas_gc_bulk_delete_chunk_keys`
* `cas_gc_round_graduation_budget`
* `cas_gc_round_redelete_budget`
* `cas_gc_round_sweep_namespace_budget`
* `cas_gc_round_sweep_recovery_op_budget`
* `cas_gc_round_ref_cleanup_budget`
* `cas_gc_round_prefix_wholesale_budget`
* `cas_gc_round_handoff_prefix_wholesale_budget`
* `cas_gc_round_outcome_entry_budget`

For `cas_gc_round_*` budgets, zero SHALL mean unbounded. For the manifest sweep,
a zero list budget SHALL disable the sweep and a zero delete budget SHALL permit
listing without nomination. `cas_gc_meta_pool_size` and
`cas_gc_bulk_delete_chunk_keys` SHALL reject zero.

#### RQ.SRS-048.CAS.GC.ReadAhead
version: 1.0

[GC] read-ahead SHALL cache results, never decisions: every take, decode,
counter, hold, and event SHALL stay at its own site, and a round run at
`cas_gc_io_concurrency = 1` SHALL reach the same verdicts as the same round run
concurrently. Read-ahead SHALL hint only ref-log ids that the round's own
`LIST` returned, so it SHALL NOT request the positions past an epoch seal,
which never exist. A log written after that `LIST` SHALL be taken inline, with
the same decision. Wasted hints SHALL be counted in `CASGCReadAheadWasted` and
useful ones in `CASGCReadAheadHit`.

A namespace's mount floor SHALL be resolved only from the server roots the
caller already listed under `gc/server-roots/`, instead of probing every `/`
prefix of the namespace name. A mount created after that listing SHALL be seen
only on the next listing, which is the conservative direction: an unresolved
floor SHALL retain, keep the barrier, or over-protect.

#### RQ.SRS-048.CAS.GC.OrphanManifests
version: 1.0

[ClickHouse] SHALL reclaim never-precommitted manifest bodies through the
orphan-manifest sweep. Eligibility SHALL use namespace watermarks and mount
floors, not object age alone. A namespace without deletion authority from a
valid mount lease SHALL retain its candidate manifests.

#### RQ.SRS-048.CAS.GC.NamespaceJanitor
version: 1.0

[ClickHouse] SHALL run a perpetual namespace janitor that reclaims the ref
stream and state objects (`_log`, `_snap`, `_ckpt`, `_files`) left under a dead
`life_id`. It SHALL work in bounded `LIST` pages under a per-round time budget,
and SHALL act whenever it next lists a key whose `life_id` a fresh catalog cut
no longer names, independently of and not gated on deletion of the catalog row.

The janitor SHALL be leak-only: it SHALL NOT fail a [GC] round, SHALL NOT block
round progress on an unreadable key, and a crash mid-page SHALL leave debris for
its next page rather than lose a live object. Its outstanding work SHALL be
observable as the `janitor-pending` state in `cas-fsck` and the
`namespace_janitor_pending`, `namespace_janitor_pending_bytes`, and
`namespace_janitor_pending_lives` counters of
[RQ.SRS-048.CAS.Fsck.Online](#rqsrs-048casfsckonline).

#### RQ.SRS-048.CAS.GC.DeleteAuthority
version: 2.0

[GC] SHALL be the only component that deletes blob bodies and the only
reachability-driven deleter of manifest bodies. A writer MAY exact-delete its
own never-precommitted manifest. Pool-member decommission MAY remove that
member's manifest debris, staging objects, and roots, but SHALL NOT
synchronously reclaim shared blob bodies, and SHALL keep the member's `owner`,
`epoch`, and `mount` control objects per
[RQ.SRS-048.CAS.DropPoolMember](#rqsrs-048casdroppoolmember).

Every delete of a retired blob body SHALL carry that object's backend token, so
a body replaced by a newer incarnation is never removed by an older round's
delete. On S3 those deletes MAY be issued as batched `DeleteObjects` requests
that carry a per-object `ETag`, bounded by `cas_gc_bulk_delete_chunk_keys`; a
batch SHALL NOT weaken the exact-token rule.

#### RQ.SRS-048.CAS.GC.DryRun
version: 1.0

[ClickHouse] SHALL support a write-free preview of the next GC round's deletes
via `clickhouse-disks ... cas-gc-dryrun` against a disk opened read-only. The
preview SHALL NOT claim a live mount lease. Away from quiescence the preview
MAY over-report; its output MUST NOT be used as a delete source.

#### RQ.SRS-048.CAS.Fsck
version: 1.0

[ClickHouse] SHALL provide an offline filesystem check
(`clickhouse-disks ... cas-fsck [--detail] [--timeout ...] [--namespace ...]
[--partial]`) that classifies `reachable`, `dangling`, `unreachable`,
`pending-gc`, `awaiting-gc`, `unaccounted`, `stale-edge`, `corrupted-run`,
`chain-broken`, `unchecked`, `lifeless-key`, `janitor-pending`, and related
object states for a [CAS] pool without mutating it. The tool SHALL open the disk
read-only and MUST NOT claim a live server's mount. Only `dangling` SHALL
directly mean data loss. `--detail` SHALL be the per-object listing; the SQL
form SHALL be summary-only.

#### RQ.SRS-048.CAS.Fsck.Online
version: 1.0

[ClickHouse] SHALL support an online consistency check against a running,
mounted [CAS] disk via

```sql
SYSTEM CAS FSCK [ON CLUSTER cluster_name] disk_name;
```

`disk_name` SHALL be required. The scan SHALL re-validate findings against a
fresh authoritative read and SHALL need no quiesce. The command SHALL return
one summary row including at least `reachable`, `dangling`, `unreachable`,
`pending_gc`, `awaiting_gc`, `unaccounted`, `stale_edge`, `corrupted_runs`,
`chain_broken`, `unchecked`, `lifeless_keys`, `namespace_janitor_pending`,
`namespace_janitor_pending_bytes`, `namespace_janitor_pending_lives`,
`ref_records_walked`, `physical_bytes`, `referenced_logical_bytes`,
`distinct_blobs`, and `total_blob_refs`.

### Day-2 Operations

#### RQ.SRS-048.CAS.DropPoolMember
version: 2.0

[ClickHouse] SHALL support decommissioning a dead pool member via

```sql
SYSTEM CAS DROP POOL MEMBER 'server_root_id' FROM DISK 'disk_name' [ON CLUSTER cluster_name];
```

and the offline twin `clickhouse-disks ... cas-drop-member <server_root_id>`.
The command SHALL claim the member's mount slot without waiting and SHALL
accept only a terminal slot: `terminated` (the member stopped cleanly) or
`fenced` (the disk's GC leader fenced its lease). A `live` or `expired` slot
SHALL be refused, so a hard-killed member SHALL NOT be removable until it is
fenced; the refusal SHALL name that wait — about one lease TTL plus one renew
period after the leader first saw the lease. The command SHALL fence that
`cas_server_root_id` from writing again, SHALL drop the member's table
namespaces, and SHALL mark the retirement verified only after drains are
confirmed. It SHALL emit ordinary ref-edge deltas rather than inventing GC
transitions, and SHALL NOT synchronously reclaim shared blob content.

The run SHALL delete only the member's **data**, and SHALL keep its `owner`,
`epoch`, and `mount` objects, so writer epochs stay strictly increasing per
`cas_server_root_id` across lives and a late tombstone cannot land on a live
successor. It SHALL proceed as: claim the victim's slot; tombstone the owner
at a new life on the admin's fenced mount plane, so no attempt is sent past the
admin's lease deadline; confirm the claim still holds, otherwise roll the
tombstone back on the unfenced control plane unless the owner was already
retired; drain the data on the fenced plane; write the farewell; then verify
the slot and owner and mark the retirement verified. When the tombstone's
outcome is unknown and the owner does not read back as tombstoned, the run
SHALL fail **without** writing its clean farewell, so the victim restarts only
after [GC] fences the slot rather than reclaiming it at once.

The operation SHALL be resumable and SHALL return `server_root_id`,
`namespaces_removed`, `namespaces_already_removed`, `committed_refs_removed`,
`precommits_removed`, `manifest_debris_removed`, `staging_objects_removed`,
`mountpoint_objects_removed`, `member_retired`, `warnings`, and
`namespaces_pending_gc`. `member_retired` SHALL be true only for a verified
mark; an owner that moved on to a later unretired life SHALL report false with
its own warning. Rows still removing after the drain SHALL be reported in
`namespaces_pending_gc`, which [GC] clears without a rerun. Non-empty
`warnings` SHALL leave the slot as a resumable anchor. A rerun SHALL be
advised only for a `retired` member whose retirement is not verified.

Whether the retired identity can come back is specified by
[RQ.SRS-048.CAS.Disk.ServerRootId.Rejoin](#rqsrs-048casdiskserverrootidrejoin).

#### RQ.SRS-048.CAS.DropPoolMember.ReadonlyRejected
version: 1.0

[ClickHouse] SHALL reject the SQL `SYSTEM CAS DROP POOL MEMBER` command against
a read-only [CAS] disk. The offline `cas-drop-member` tool SHALL open the disk
read-only and MUST NOT claim a live server's mount (the pool-admin claim
happens internally).

#### RQ.SRS-048.CAS.Forget
version: 1.0

[ClickHouse] SHALL support a node-local assertion that a [CAS] disk is
permanently gone via

```sql
SYSTEM CAS FORGET [ON CLUSTER cluster_name] disk_name;
```

`FORGET` SHALL work on a disk that is not live. It is an assertion, not a proof
of erasure: the disk SHALL stay registered, further store-class access SHALL
return a typed error, and a server restart SHALL re-register the name. This is
distinct from `SYSTEM CAS DROP POOL MEMBER`, which retires one pool member's
identity across the whole shared pool.

#### RQ.SRS-048.CAS.Tools
version: 1.0

[ClickHouse] SHALL provide `clickhouse-disks` commands `cas-fsck`, `cas-inspect`,
`cas-gc-dryrun`, `cas-gc-rebuild`, and `cas-drop-member`. All five SHALL require
the disk to be opened read-only and MUST NOT claim a live server's mount.
`cas-inspect` SHALL decode one raw object-storage key to JSON.

### Fault Recovery

#### RQ.SRS-048.CAS.Fault.LostPartRecovery
version: 1.0

[ClickHouse] SHALL heal via ordinary lost-part recovery when a replica is
terminated after ZooKeeper multi / coordination commit but before durable [CAS]
publish completes, without requiring a fixed sync timeout as the sole success
oracle.

#### RQ.SRS-048.CAS.Fault.LazyLoad.S3Outage
version: 2.0

[ClickHouse] SHALL retry table construction during asynchronous loading when
it fails on a transient [CAS] mount failure, so tables become available again
once the mount recovers, without a server restart. A permanent failure SHALL
stay terminal, lease fencing SHALL be preserved, and shutdown SHALL be able to
interrupt the recovery rather than wait indefinitely. This is the one
[CAS]-specific departure from the one-shot AsyncLoader design: a job that fails
for any other reason SHALL still remain `FAILED` until the server restarts or a
fresh load is issued for that table.

#### RQ.SRS-048.CAS.Fault.FailClosed
version: 1.0

[ClickHouse] SHALL fail closed under ambiguity on the write / promote / delete
paths: an operation that may have landed MUST NOT be treated as one that did
not, and uncertain deletes MUST be suppressed rather than assumed safe.

### Cache

#### RQ.SRS-048.CAS.Cache
version: 1.0

[ClickHouse] SHALL support composing a filesystem cache disk over a [CAS]
object-storage disk. Cache-over-[CAS] is the supported wrapper shape (see
[RQ.SRS-048.CAS.Disk.Configuration](#rqsrs-048casdiskconfiguration)).
`system.cas_mounts` SHALL list a row per configured disk name, so a cache
layered in front MAY appear twice under the same `cas_server_root_id`.

#### RQ.SRS-048.CAS.Cache.Hits
version: 1.0

[ClickHouse] SHALL serve repeated reads of the same [CAS] objects from the
local cache when cache-over-CAS is configured, without changing logical query
results.

### Observability And Access

#### RQ.SRS-048.CAS.Observability
version: 1.0

[ClickHouse] SHALL expose [CAS] operational state through documented system
tables, `CAS*` / `CASGC*` `ProfileEvents`, and the `SYSTEM CAS` command
surface so operators can observe pool membership, GC progress, and related
health signals.

#### RQ.SRS-048.CAS.Observability.SystemTables
version: 1.0

[ClickHouse] SHALL provide:

* `system.cas_mounts` — live per-mount view of every `cas_server_root_id` in
  the pool (not only the local server), including lease and lifecycle state.
* `system.cas_gc_log` — per-round `Start` / `Finish` / `Phase` rows correlated
  by `round_id`, for both scheduled and manual (`SYSTEM CAS GC RUN`) rounds.
* `system.cas_log` — per-decision event log (blob puts, dedup adoptions, ref
  transitions, GC retire decisions, dangling-access findings).

`system.cas_log` and `system.cas_gc_log` SHALL be created when the matching
server settings are specified (enabled by default in the shipped `config.xml`).

#### RQ.SRS-048.CAS.Observability.Mounts
version: 2.0

`system.cas_mounts` SHALL read live backend state on each query and skip a disk
whose backend read fails without hiding other disks. It SHALL expose mount
states `live`, `expired`, `terminated`, `fenced`, `retired`, and `corrupt`;
lifecycle states `live`, `not_live`, `identity_lost`, `vanished`,
`constructing`, and `shutdown`; vanish reasons `replaced` and `forgotten`; and
`lifecycle_detail` / `lifecycle_since`. Process-local columns including
`is_leader`, `pending_reclaim`, `last_success_age_seconds`, and
`wedged_namespace_count` SHALL be `NULL` on peer rows.

The table SHALL report a mount-lease renewal while it runs, so an operator can
tell a renewal retrying through an object-store outage from a renewal thread
that has died: `renewal_in_progress` (a renewal call is running),
`renewal_attempts` (physical `PUT`s sent by the current call), and
`last_renewal_error` (verb, key, and error class of the last refused request,
carrying no credentials and no bodies). A local failure of the resolve read,
which is not a request to the store, SHALL NOT be published there.

A decommissioned member SHALL read as `retired`, with `retirement_verified`
reporting 1 once the retirement is verified and 0 otherwise. There SHALL be no
`retiring` state.

#### RQ.SRS-048.CAS.Observability.GCLog
version: 1.0

`system.cas_gc_log` SHALL expose outcomes `Unknown`, `Success`, `NotALeader`,
`Deferred`, `Aborted`, `Stopped`, and `Error`; correlate rows with `round_id`;
and expose `phase`, `phase_duration_microseconds`, `phase_metrics`, and
per-row `ProfileEvents`. Monitoring SHALL key failures on `error_code` rather
than parsing `error` text. Work performed by helper threads MAY be absent from
one phase row's `ProfileEvents` and SHALL remain attributable through the
documented phase metrics and finish-row totals.

#### RQ.SRS-048.CAS.Observability.EventLog
version: 1.0

`system.cas_log` SHALL expose per-decision events including `blob_put`,
`blob_reuse_adopt`, `root_remove`, `indegree_zero`, `gc_retire_decision`,
`gc_recheck_verdict`, `blob_delete`, `dangling_access`, `corrupt_dangle`,
`watermark_renew`, and `mount_remount`, with the relevant pool, namespace,
object, token, and decision context.

#### RQ.SRS-048.CAS.Observability.ProfileEvents
version: 2.0

[ClickHouse] SHALL expose [CAS]-related `ProfileEvents` under the uppercase
`CAS` / `CASGC` prefix (blob, manifest, ref, mount-renewal/remount, and GC
counters) so operators can attribute pool I/O and diagnose mount-lease
recovery without reading server logs alone. The surface SHALL include ref
append/recovery failures, GC fence and anomaly counters, rollback cleanup
failures, and mount renewal/remount attempt, retry, success, loss, deadline,
and failure counters. Mount renewal attempts and retries SHALL be counted per
sent attempt rather than derived from the result of the call.

The surface SHALL include at least `CASMetaAbsentRepublish`
([RQ.SRS-048.CAS.Write.BlobMaterialization](#rqsrs-048caswriteblobmaterialization)),
`CASBlobPublishAttemptFailed` and `CASBlobPublishGaveUp`
([RQ.SRS-048.CAS.Write.BlobPublishRetries](#rqsrs-048caswriteblobpublishretries)),
`CASGCReadAheadWasted` and `CASGCReadAheadHit`
([RQ.SRS-048.CAS.GC.ReadAhead](#rqsrs-048casgcreadahead)), and `CASRefMove`
and `CASOwnershipConflict`
([RQ.SRS-048.CAS.Write.PartRename](#rqsrs-048caswritepartrename)).
`CASMetaAdoptBackfill` SHALL be gone; a dashboard that read it SHALL read
`CASMetaAbsentRepublish` instead.

#### RQ.SRS-048.CAS.Access
version: 1.0

[ClickHouse] SHALL enforce a distinct `GLOBAL SYSTEM` privilege for each
`SYSTEM CAS` verb: `GC RUN`, `GC REBUILD`, `GC STOP`, `GC START`, `FSCK`,
`FORGET`, and `DROP POOL MEMBER`. A read-only fsck grant SHALL be grantable
without the destructive verbs.

### Restrictions And Non-Goals

#### RQ.SRS-048.CAS.Restrictions.BackendCapabilities
version: 1.1

[ClickHouse] SHALL require an object store that provides the capabilities
needed by the [CAS] mount and delete protocols, checked by a capability probe
at every writable mount. Required capabilities include read-after-write,
conditional create (`If-None-Match: *`) for manifests and control objects,
conditional overwrite (`If-Match`) for mount leases and `gc/state`,
unconditional blob publication, exact-token delete (single or batched, per
[RQ.SRS-048.CAS.GC.DeleteAuthority](#rqsrs-048casgcdeleteauthority)), ranged
`GET`, and resumable `LIST`. Bucket versioning SHALL be disabled (a versioned or
confirmed-enabled versioning probe SHALL refuse a writable generation-token
mount). An inconclusive GCS versioning probe SHALL warn and continue, leaving
verification to the operator.
Object soft-delete MUST be disabled by the operator (not verified at mount).
When those capabilities are absent, mount SHALL fail closed rather than
silently run an unsafe configuration. `skip_access_check = true` SHALL be
refused on a writable generation-token (GCS) disk.

#### RQ.SRS-048.CAS.Restrictions.ConditionalWriteRetries
version: 1.1

Before admitting a writable mount, [ClickHouse] SHALL verify that the
object-storage client supports a single-HTTP-attempt retry profile for
conditional writes. A client with hidden conditional-write retries SHALL be
rejected because a retry can outlive the mount lease and obscure whether the
operation committed. Conditional retries SHALL occur only as explicit [CAS]
state-machine transitions. The same single-attempt rule applies per verb to
the unconditional object-creating requests of blob publication, specified by
[RQ.SRS-048.CAS.Write.BlobPublishRetries](#rqsrs-048caswriteblobpublishretries).

#### RQ.SRS-048.CAS.Restrictions.BackendToken
version: 1.0

The object store SHALL preserve `TOKEN` implies `CONTENT`: one observed ETag or
generation token SHALL NOT name different object content over time. Because the
mount capability probe cannot prove this property, operators SHALL use only a
backend whose token and exact-delete semantics satisfy the documented contract.

#### RQ.SRS-048.CAS.Restrictions.ZeroCopy
version: 1.0

[ClickHouse] SHALL NOT use classic zero-copy replication
(`allow_remote_fs_zero_copy_replication`) as the [CAS] sharing mechanism.
Same-pool sharing uses [CAS] refs and fetch-by-relink instead.
`supportZeroCopyReplication` SHALL report false for content-addressed disks.
[CAS] SHALL coexist with zero-copy: disks that do not set `metadata_type = cas`
keep their existing zero-copy behavior.

#### RQ.SRS-048.CAS.Restrictions.UniqueKey
version: 1.0

[ClickHouse] SHALL reject UNIQUE KEY / upsert [MergeTree] tables on non-local
disks, which includes [CAS]. UNIQUE KEY on [CAS] is out of scope while that
upstream fence remains.

#### RQ.SRS-048.CAS.Restrictions.NonMergeTree
version: 1.0

[CAS] is intended for the [MergeTree] engine family. Using a [CAS] disk as
generic storage for non-MergeTree engines, temporary-files disks, dictionary
SSD-cache backing, or Distributed spool is not a supported configuration and
MAY fail with `NOT_IMPLEMENTED` or an equivalent error.

#### RQ.SRS-048.CAS.Restrictions.Backup.TempHardLinks
version: 1.0

[ClickHouse] SHALL reject the temporary-hard-link `BACKUP` path on a [CAS] disk
(Ordinary / non-UUID databases that require that path). Operators SHALL use an
Atomic database so backup uses the pointer-holding path.

#### RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot
version: 1.0

The git-shaped [CAS] `snapshot` / `mirror` / `fetch` / `restore` design is
approved but not implemented and SHALL NOT be treated as wired into the
`BACKUP` / `RESTORE` SQL surface. Ordinary pointer-holding `BACKUP` /
`RESTORE` of [CAS] tables remains
[RQ.SRS-048.CAS.Backup](#rqsrs-048casbackup) /
[RQ.SRS-048.CAS.Restore](#rqsrs-048casrestore).

#### RQ.SRS-048.CAS.Restrictions.Encryption
version: 1.0

An `encrypted` disk wrapping a [CAS] disk is not supported. `CREATE TABLE` on
such a disk MAY succeed; the first `INSERT` SHALL fail (documented as
`Autocommit writes are not supported for content part files on a
content-addressed disk`). Cache-over-[CAS] is the supported wrapper; encryption
at rest currently has to come from the object store.

#### RQ.SRS-048.CAS.Restrictions.Azure
version: 1.0

Azure Blob as a [CAS] backend is not supported. Azure's REST API documents
equivalent conditional headers, but ClickHouse does not wire a [CAS]
conditional dialect for Azure, and the capability probe does not validate it.

#### RQ.SRS-048.CAS.Restrictions.GCS
version: 1.0

Google Cloud Storage's generation-token implementation is present, but the
credentialed real-GCS release gate is pending. Suites against a fake GCS
service SHALL NOT be treated as proof of Google's multipart, native-copy, or
exact-delete wire behavior. The GCS HMAC path SHALL reject server-side
encryption headers and unknown custom `x-amz-*` headers rather than guessing
`x-goog-*` equivalents. Operators SHALL account for GCS per-object-name write
limits on hot checkpoint and ref-catalog objects.

#### RQ.SRS-048.CAS.Restrictions.LocalBackend
version: 1.0

The `local` object-storage backend SHALL be treated as a single-node,
best-effort development backend. Blob publication MAY materialize a complete
blob in memory and serialize publication; it SHALL NOT be used as evidence of
production object-store concurrency or failure semantics.

#### RQ.SRS-048.CAS.Restrictions.WideParts
version: 1.0

Operators SHALL account for one object-store request per blob-backed column
file when opening wide parts. Very wide merges MAY exhaust local ephemeral
ports unless connection reuse and concurrency are configured appropriately.

## References

* [Git]
* [GitHub Repository]
* [Revision History]
* [ClickHouse]
* [MergeTree]
* [CAS]
* [SRS]
* [CAS documentation]
* [SYSTEM CAS]
* [CAS system tables]
* [CAS integration test inventory](../docs/CAS-INTEGRATION-TESTS.md)
* [ClickHouse ALTER](https://clickhouse.com/docs/reference/statements/alter)
* [ClickHouse ALTER COLUMN](https://clickhouse.com/docs/reference/statements/alter/column)
* [ClickHouse ALTER PARTITION](https://clickhouse.com/docs/reference/statements/alter/partition)

[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/cas/requirements/requirements.md
[ClickHouse]: https://clickhouse.com
[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree
[CAS]: #terminology
[SRS]: #introduction
[GC]: #terminology
[CAS documentation]: https://github.com/Altinity/ClickHouse/tree/antalya-26.6/docs/en/antalya/cas
[SYSTEM CAS]: https://github.com/Altinity/ClickHouse/blob/antalya-26.6/docs/en/sql-reference/statements/system.md
[CAS system tables]: https://github.com/Altinity/ClickHouse/tree/antalya-26.6/docs/en/operations/system-tables
