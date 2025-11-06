# SRS-044 Swarm Cluster Query Execution
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
    * 2.1 [Node Registration and Deregistration](#node-registration-and-deregistration)
        * 2.1.1 [RQ.SRS-044.Swarm.NodeRegistration](#rqsrs-044swarmnoderegistration)
        * 2.1.2 [RQ.SRS-044.Swarm.NodeRegistration.MultipleDiscoverySections](#rqsrs-044swarmnoderegistrationmultiplediscoverysections)
        * 2.1.3 [RQ.SRS-044.Swarm.NodeDeregistration](#rqsrs-044swarmnodederegistration)
    * 2.2 [Cluster Discovery](#cluster-discovery)
        * 2.2.1 [RQ.SRS-044.Swarm.ClusterDiscovery.Path](#rqsrs-044swarmclusterdiscoverypath)
        * 2.2.2 [RQ.SRS-044.Swarm.ClusterDiscovery.WrongPath](#rqsrs-044swarmclusterdiscoverywrongpath)
        * 2.2.3 [RQ.SRS-044.Swarm.ClusterDiscovery.MultiplePaths](#rqsrs-044swarmclusterdiscoverymultiplepaths)
    * 2.3 [Authentication Using Secret](#authentication-using-secret)
        * 2.3.1 [RQ.SRS-044.Swarm.ClusterDiscovery.Authentication](#rqsrs-044swarmclusterdiscoveryauthentication)
        * 2.3.2 [RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.WrongKey](#rqsrs-044swarmclusterdiscoveryauthenticationwrongkey)
        * 2.3.3 [RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.MultipleKeys](#rqsrs-044swarmclusterdiscoveryauthenticationmultiplekeys)
    * 2.4 [Query Processing](#query-processing)
        * 2.4.1 [RQ.SRS-044.Swarm.QueryProcessing.Planning](#rqsrs-044swarmqueryprocessingplanning)
        * 2.4.2 [RQ.SRS-044.Swarm.QueryProcessing.PartialQueriesExecution](#rqsrs-044swarmqueryprocessingpartialqueriesexecution)
    * 2.5 [Retry Mechanism](#retry-mechanism)
        * 2.5.1 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeFailure](#rqsrs-044swarmqueryprocessingretrymechanismnodefailure)
        * 2.5.2 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.ScaleDown](#rqsrs-044swarmqueryprocessingretrymechanismscaledown)
        * 2.5.3 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeLatency](#rqsrs-044swarmqueryprocessingretrymechanismnodelatency)
        * 2.5.4 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NetworkFailure](#rqsrs-044swarmqueryprocessingretrymechanismnetworkfailure)
    * 2.6 [Caching](#caching)
        * 2.6.1 [Local Disk Cache](#local-disk-cache)
            * 2.6.1.1 [RQ.SRS-044.Swarm.Caching.LocalDiskCache](#rqsrs-044swarmcachinglocaldiskcache)
            * 2.6.1.2 [RQ.SRS-044.Swarm.Caching.LocalDiskCacheConsistency](#rqsrs-044swarmcachinglocaldiskcacheconsistency)
            * 2.6.1.3 [RQ.SRS-044.Swarm.Caching.LocalDiskCachePerformance](#rqsrs-044swarmcachinglocaldiskcacheperformance)
            * 2.6.1.4 [RQ.SRS-044.Swarm.Caching.DiskCacheUpdates](#rqsrs-044swarmcachingdiskcacheupdates)
            * 2.6.1.5 [RQ.SRS-044.Swarm.Caching.DiskCacheNoDiskSpace](#rqsrs-044swarmcachingdiskcachenodiskspace)
        * 2.6.2 [Query Cache](#query-cache)
            * 2.6.2.1 [RQ.SRS-044.Swarm.Caching.QueryCache](#rqsrs-044swarmcachingquerycache)
            * 2.6.2.2 [RQ.SRS-044.Swarm.Caching.QueryCacheConsistency](#rqsrs-044swarmcachingquerycacheconsistency)
            * 2.6.2.3 [RQ.SRS-044.Swarm.Caching.QueryCachePerformance](#rqsrs-044swarmcachingquerycacheperformance)
            * 2.6.2.4 [RQ.SRS-044.Swarm.Caching.QueryCacheUpdates](#rqsrs-044swarmcachingquerycacheupdates)
            * 2.6.2.5 [RQ.SRS-044.Swarm.Caching.QueryCacheNoDiskSpace](#rqsrs-044swarmcachingquerycachenodiskspace)
        * 2.6.3 [Parquet Metadata Cache](#parquet-metadata-cache)
            * 2.6.3.1 [RQ.SRS-044.Swarm.Caching.ParquetMetadataCache](#rqsrs-044swarmcachingparquetmetadatacache)
            * 2.6.3.2 [RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheConsistency](#rqsrs-044swarmcachingparquetmetadatacacheconsistency)
            * 2.6.3.3 [RQ.SRS-044.Swarm.Caching.ParquetMetadataCachePerformance](#rqsrs-044swarmcachingparquetmetadatacacheperformance)
            * 2.6.3.4 [RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheUpdates](#rqsrs-044swarmcachingparquetmetadatacacheupdates)
            * 2.6.3.5 [RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheNoDiskSpace](#rqsrs-044swarmcachingparquetmetadatacachenodiskspace)
    * 2.7 [Settings](#settings)
        * 2.7.1 [RQ.SRS-044.Swarm.Settings.object_storage_max_nodes](#rqsrs-044swarmsettingsobject_storage_max_nodes)
    * 2.8 [Observer](#observer)
        * 2.8.1 [RQ.SRS-044.Swarm.ObserverNodes](#rqsrs-044swarmobservernodes)
    * 2.9 [RBAC](#rbac)
        * 2.9.1 [RQ.SRS-044.Swarm.RBAC.RowPolicy](#rqsrs-044swarmrbacrowpolicy)
        * 2.9.2 [RQ.SRS-044.Swarm.RBAC.ColumnPolicy](#rqsrs-044swarmrbaccolumnpolicy)
    * 2.10 [Performance](#performance)
        * 2.10.1 [RQ.SRS-044.Swarm.Performance](#rqsrs-044swarmperformance)
    * 2.11 [Joins](#joins)
        * 2.11.1 [RQ.SRS-044.Swarm.Joins](#rqsrs-044swarmjoins)
        * 2.11.2 [Standard Join Types](#standard-join-types)
            * 2.11.2.1 [RQ.SRS-044.Swarm.Joins.Inner](#rqsrs-044swarmjoinsinner)
            * 2.11.2.2 [RQ.SRS-044.Swarm.Joins.LeftOuter](#rqsrs-044swarmjoinsleftouter)
            * 2.11.2.3 [RQ.SRS-044.Swarm.Joins.RightOuter](#rqsrs-044swarmjoinsrightouter)
            * 2.11.2.4 [RQ.SRS-044.Swarm.Joins.FullOuter](#rqsrs-044swarmjoinsfullouter)
            * 2.11.2.5 [RQ.SRS-044.Swarm.Joins.Cross](#rqsrs-044swarmjoinscross)
        * 2.11.3 [ClickHouse-Specific Join Types](#clickhouse-specific-join-types)
            * 2.11.3.1 [RQ.SRS-044.Swarm.Joins.Semi](#rqsrs-044swarmjoinssemi)
            * 2.11.3.2 [RQ.SRS-044.Swarm.Joins.Anti](#rqsrs-044swarmjoinsanti)
            * 2.11.3.3 [RQ.SRS-044.Swarm.Joins.Any](#rqsrs-044swarmjoinsany)
            * 2.11.3.4 [RQ.SRS-044.Swarm.Joins.Asof](#rqsrs-044swarmjoinsasof)
            * 2.11.3.5 [RQ.SRS-044.Swarm.Joins.Paste](#rqsrs-044swarmjoinspaste)
        * 2.11.4 [Swarm Join Settings](#swarm-join-settings)
            * 2.11.4.1 [RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode](#rqsrs-044swarmjoinsswarmsettingsobject_storage_cluster_join_mode)
            * 2.11.4.2 [RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode.Allow](#rqsrs-044swarmjoinsswarmsettingsobject_storage_cluster_join_modeallow)
            * 2.11.4.3 [RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode.Local](#rqsrs-044swarmjoinsswarmsettingsobject_storage_cluster_join_modelocal)
            * 2.11.4.4 [RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode.Global](#rqsrs-044swarmjoinsswarmsettingsobject_storage_cluster_join_modeglobal)
        * 2.11.5 [General Join Settings](#general-join-settings)
            * 2.11.5.1 [RQ.SRS-044.Swarm.Joins.Settings.DefaultStrictness](#rqsrs-044swarmjoinssettingsdefaultstrictness)
            * 2.11.5.2 [RQ.SRS-044.Swarm.Joins.Settings.AnyJoinDistinct](#rqsrs-044swarmjoinssettingsanyjoindistinct)
            * 2.11.5.3 [RQ.SRS-044.Swarm.Joins.Settings.CrossToInnerRewrite](#rqsrs-044swarmjoinssettingscrosstoinnerrewrite)
            * 2.11.5.4 [RQ.SRS-044.Swarm.Joins.Settings.Algorithm](#rqsrs-044swarmjoinssettingsalgorithm)
            * 2.11.5.5 [RQ.SRS-044.Swarm.Joins.Settings.AnyTakeLastRow](#rqsrs-044swarmjoinssettingsanytakelastrow)
            * 2.11.5.6 [RQ.SRS-044.Swarm.Joins.Settings.UseNulls](#rqsrs-044swarmjoinssettingsusenulls)
            * 2.11.5.7 [RQ.SRS-044.Swarm.Joins.Settings.PartialMergeRows](#rqsrs-044swarmjoinssettingspartialmergerows)
            * 2.11.5.8 [RQ.SRS-044.Swarm.Joins.Settings.OnDiskMaxFiles](#rqsrs-044swarmjoinssettingsondiskmaxfiles)
            

## Introduction

This document describes the requirements for the [Ability Antalya] Swarm Cluster functionality, which enables automatic cluster discovery and management of ClickHouse nodes. The swarm cluster architecture consists of two main components:

1. An `initiator cluster` that accepts and plans queries. The queries are load-balanced using a classic network load-balancer.
2. A `swarm cluster` that is used to parallelize query execution. 

Each initiator node receives a query and plans query execution by breaking up execution of the query across all the nodes in the `swarm cluster` and aggregating partial query results from the swarm nodes.
The system is designed to optimize query performance through efficient resource utilization,
cache management, and parallel processing while maintaining fault tolerance and scalability.

## Requirements

### Node Registration and Deregistration

#### RQ.SRS-044.Swarm.NodeRegistration
version: 1.0  

[ClickHouse] SHALL support node registration through adding `<clickhouse><remote_servers><swarm><discovery>` section in the configuration file.

Example:
```xml
<clickhouse>
    <allow_experimental_cluster_discovery>1</allow_experimental_cluster_discovery>
    <remote_servers>
        <swarm>
            <discovery>
                <path>/clickhouse/discovery/swarm</path>
                <secret>secret_key</secret>
            </discovery>
        </swarm>
    </remote_servers>
</clickhouse>
```


#### RQ.SRS-044.Swarm.NodeRegistration.MultipleDiscoverySections
version: 1.0  

[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm>` 
contains multiple discovery sections.

#### RQ.SRS-044.Swarm.NodeDeregistration
version: 1.0  

[ClickHouse] SHALL support node deregistration through removal of `<clickhouse><remote_servers><swarm><discovery>` section in swarm node configuration files. Removing node from the swarm cluster does not require initiator node restart.

Example:
```xml
<!-- To deregister a node, remove this section from the configuration -->
<clickhouse>
    <allow_experimental_cluster_discovery>1</allow_experimental_cluster_discovery>
    <remote_servers>
        <swarm>
            <discovery>
                <path>/clickhouse/discovery/swarm</path>
                <secret>secret_key</secret>
            </discovery>
        </swarm>
    </remote_servers>
</clickhouse>
```


### Cluster Discovery

#### RQ.SRS-044.Swarm.ClusterDiscovery.Path
version: 1.0

[ClickHouse] SHALL support automatic cluster discovery through a configured discovery path which SHALL uniquely identify a specific swarm cluster.

Example:
```xml
<clickhouse>
    <remote_servers>
        <swarm>
            <discovery>
               <...>
               <path>/clickhouse/discovery/swarm</path>
               <...>
            </discovery>
        </swarm>
    </remote_servers>
</clickhouse>
```

#### RQ.SRS-044.Swarm.ClusterDiscovery.WrongPath
version: 1.0

[ClickHouse] SHALL not add node to the swarm cluster if path provided in `<clickhouse><remote_servers><swarm><discovery>` is different from the path provided in the initiator node configuration.

#### RQ.SRS-044.Swarm.ClusterDiscovery.MultiplePaths
version: 1.0

[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm><discovery>` 
contains multiple discovery paths.

### Authentication Using Secret

#### RQ.SRS-044.Swarm.ClusterDiscovery.Authentication
version: 1.0

[ClickHouse] SHALL use the configured secret key for swarm cluster node authentication.

Example:
```xml
<clickhouse>
    <remote_servers>
        <swarm>
            <discovery>
               <...>
               <secret>secret_key</secret>
               <...>
            </discovery>
        </swarm>
    </remote_servers>
</clickhouse>
```

#### RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.WrongKey
version: 1.0

[ClickHouse] SHALL not add node to the swarm cluster if secret key provided in `<clickhouse><remote_servers><swarm><discovery>` is different from the secret key provided in the initiator node configuration.

#### RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.MultipleKeys
version: 1.0

[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm><discovery>` contains multiple secret keys.

### Query Processing

#### RQ.SRS-044.Swarm.QueryProcessing.Planning
version: 1.0  

Initiator node SHALL plan query execution by breaking up execution of the query across all the nodes in the swarm cluster.

#### RQ.SRS-044.Swarm.QueryProcessing.PartialQueriesExecution
version: 1.0  

Initiator node SHALL send partial queries to swarm nodes. Swarm nodes SHALL execute partial queries and return partial results to the initiator node. Then initiator node SHALL aggregate results. 

### Retry Mechanism

#### RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeFailure
version: 1.0  

[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node failure during any point of query execution.

#### RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.ScaleDown
version: 1.0  

[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node disappearance due to scale-down.

#### RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeLatency
version: 1.0  

[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node latency or unresponsiveness.

#### RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NetworkFailure
version: 1.0  

[ClickHouse] SHALL support a retry mechanism for swarm queries in case of network failure.

### Caching

#### Local Disk Cache

##### RQ.SRS-044.Swarm.Caching.LocalDiskCache
version: 1.0  

Swarm nodes SHALL support local disk cache.
Swarm nodes SHALL not download data from storage data files if it is cached.

##### RQ.SRS-044.Swarm.Caching.LocalDiskCacheConsistency
version: 1.0  

Swarm nodes SHALL return the same result for queries when local disk cache is enabled and disabled.

##### RQ.SRS-044.Swarm.Caching.LocalDiskCachePerformance
version: 1.0  

Swarm nodes SHALL not run query much slower if data for the query is not cached in comparison with disabled local disk cache.
Swarm nodes SHALL run query faster if data for the query is cached in comparison with disabled local disk cache.

##### RQ.SRS-044.Swarm.Caching.DiskCacheUpdates
version: 1.0  

Swarm nodes SHALL run query and update disk cache if data for query is changed.

##### RQ.SRS-044.Swarm.Caching.DiskCacheNoDiskSpace
version: 1.0  

Swarm nodes SHALL not cache the data if node has no enough space to cache it.

#### Query Cache

##### RQ.SRS-044.Swarm.Caching.QueryCache
version: 1.0  

Swarm nodes SHALL support query cache. 
Swarm nodes SHALL not run query if it is cached on the node.

##### RQ.SRS-044.Swarm.Caching.QueryCacheConsistency
version: 1.0  

Swarm nodes SHALL return the same result for queries when query cache is enabled and disabled.

##### RQ.SRS-044.Swarm.Caching.QueryCachePerformance
version: 1.0  

Swarm nodes SHALL not perform query much slower if query is not cached in comparison with disabled query cache.
Swarm nodes SHALL perform query faster if query is cached in comparison with disabled query cache.

##### RQ.SRS-044.Swarm.Caching.QueryCacheUpdates
version: 1.0  

Swarm nodes SHALL run query and update query cache if data for query is changed.

##### RQ.SRS-044.Swarm.Caching.QueryCacheNoDiskSpace
version: 1.0  

Swarm nodes SHALL not cache the query if node has no enough space to cache it.

#### Parquet Metadata Cache

##### RQ.SRS-044.Swarm.Caching.ParquetMetadataCache
version: 1.0  

Swarm nodes SHALL support parquet metadata cache. 
Swarm nodes SHALL not download parquet metadata from storage if parquet metadata is cached.

##### RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheConsistency
version: 1.0  

Swarm nodes SHALL return the same result for queries with enabled and disabled parquet metadata cache.

##### RQ.SRS-044.Swarm.Caching.ParquetMetadataCachePerformance
version: 1.0  

Swarm nodes SHALL not perform query much slower if parquet metadata is not cached in comparison with parquet metadata cache.
Swarm nodes SHALL perform query faster if parquet metadata is cached in comparison with disabled parquet metadata cache.

##### RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheUpdates
version: 1.0  

Swarm nodes SHALL run query and update parquet metadata cache if data for query is changed.

##### RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheNoDiskSpace
version: 1.0  

Swarm nodes SHALL not cache the parquet metadata if node has no enough space to cache it.

### Settings

This section describes swarm-specific settings that control swarm cluster behavior.

#### RQ.SRS-044.Swarm.Settings.object_storage_max_nodes
version: 1.0  

[ClickHouse] SHALL support the `object_storage_max_nodes` setting to limit the number of nodes used in swarm cluster for a particular query

### Observer

#### RQ.SRS-044.Swarm.ObserverNodes
version: 1.0  

[ClickHouse] SHALL support specifying a swarm node as an observer.
This means that this node can use this cluster but doesn't get partial queries to execute.
[Clickhouse] SHALL support multiple observers.

Example:
```xml
<clickhouse>
    <remote_servers>
        <swarm>
            <discovery>
                ...
                <observer>true</observer>
                ...
            </discovery>
        </swarm>
    </remote_servers>
</clickhouse>
```

### RBAC

#### RQ.SRS-044.Swarm.RBAC.RowPolicy
version: 1.0  

[ClickHouse] SHALL support row-level access control for swarm queries on the initiator.  
Swarm queries SHALL be anonymized, and the authority model is enforced only on the initiator. 

#### RQ.SRS-044.Swarm.RBAC.ColumnPolicy
version: 1.0

[ClickHouse] SHALL support column-level access control for swarm queries on the initiator. 

### Performance

#### RQ.SRS-044.Swarm.Performance
version: 1.0  

Query performance using swarm cluster SHALL be not worse than the performance of a single ClickHouse node
for queries that accesses data from multiple files in average.

### Joins

#### RQ.SRS-044.Swarm.Joins
version: 1.0  

[ClickHouse] SHALL support joins for swarm queries. This includes both standard SQL join types and ClickHouse-specific join types.

#### Standard Join Types

##### RQ.SRS-044.Swarm.Joins.Inner
version: 1.0  

[ClickHouse] SHALL support inner joins for swarm queries. Inner joins SHALL return only matching rows from both tables.

##### RQ.SRS-044.Swarm.Joins.LeftOuter
version: 1.0  

[ClickHouse] SHALL support left outer joins for swarm queries. Left outer joins SHALL return non-matching rows from the left table in addition to matching rows. 

##### RQ.SRS-044.Swarm.Joins.RightOuter
version: 1.0  

[ClickHouse] SHALL support right outer joins for swarm queries. Right outer joins SHALL return non-matching rows from the right table in addition to matching rows. 

##### RQ.SRS-044.Swarm.Joins.FullOuter
version: 1.0  

[ClickHouse] SHALL support full outer joins for swarm queries. Full outer joins SHALL return non-matching rows from both tables in addition to matching rows. 

##### RQ.SRS-044.Swarm.Joins.Cross
version: 1.0  

[ClickHouse] SHALL support cross joins for swarm queries. Cross joins SHALL produce a cartesian product of whole tables without requiring join keys. An alternative syntax for CROSS JOIN is specifying multiple tables in the FROM clause separated by commas.

#### ClickHouse-Specific Join Types

##### RQ.SRS-044.Swarm.Joins.Semi
version: 1.0  

[ClickHouse] SHALL support left semi joins and right semi joins for swarm queries. Semi joins SHALL act as an allowlist on "join keys" without producing a cartesian product.

##### RQ.SRS-044.Swarm.Joins.Anti
version: 1.0  

[ClickHouse] SHALL support left anti joins and right anti joins for swarm queries. Anti joins SHALL act as a denylist on "join keys" without producing a cartesian product.

##### RQ.SRS-044.Swarm.Joins.Any
version: 1.0  

[ClickHouse] SHALL support left any joins, right any joins, and inner any joins for swarm queries. Any joins SHALL partially (for opposite side of LEFT and RIGHT) or completely (for INNER and FULL) disable the cartesian product for standard JOIN types.

##### RQ.SRS-044.Swarm.Joins.Asof
version: 1.0  

[ClickHouse] SHALL support ASOF joins and left ASOF joins for swarm queries. ASOF joins SHALL enable joining sequences with a non-exact match.

##### RQ.SRS-044.Swarm.Joins.Paste
version: 1.0  

[ClickHouse] SHALL support paste joins for swarm queries. Paste joins SHALL perform a horizontal concatenation of two tables.

#### Swarm Join Settings

This section describes swarm-specific settings that control JOIN behavior when using object storage cluster functions. 

##### RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode
version: 1.0  

[ClickHouse] SHALL support the `object_storage_cluster_join_mode` setting that controls the behavior of JOIN operations when using object storage cluster functions (such as `s3Cluster`) or iceberg tables.

The setting SHALL ONLY apply when:
- The query contains a JOIN operation
- The FROM clause uses an object storage cluster function or table on the left side of the JOIN


##### RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode.Allow
version: 1.0  

[ClickHouse] SHALL support `object_storage_cluster_join_mode='allow'` as the default mode.

When this mode is enabled:
- The entire query SHALL be sent to swarm nodes as-is
- JOIN operations SHALL be executed on the remote swarm nodes
- This SHALL preserve the behavior prior to the introduction of this setting


##### RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode.Local
version: 1.0  

[ClickHouse] SHALL support `object_storage_cluster_join_mode='local'` mode.

When this mode is enabled:
- Only the left part of the JOIN SHALL be sent to swarm nodes
- Swarm nodes SHALL execute the left part and return results to the initiator
- The initiator node SHALL collect responses from swarm nodes
- The initiator node SHALL execute the JOIN operation locally with the right table


##### RQ.SRS-044.Swarm.Joins.SwarmSettings.object_storage_cluster_join_mode.Global
version: 1.0  

[ClickHouse] SHALL support `object_storage_cluster_join_mode='global'` mode.

When this mode is implemented, it SHALL:
- Execute the right part of the JOIN on the initiator node
- Send the result of the right part along with the query to swarm nodes
- Execute the JOIN operation with the left part on swarm nodes

Note: This mode is NOT currently implemented and SHALL return an appropriate error or warning if used.

#### General Join Settings

This section describes general ClickHouse join settings that SHALL also work with swarm queries. 
These are standard ClickHouse settings, not swarm-specific settings.

##### RQ.SRS-044.Swarm.Joins.Settings.DefaultStrictness
version: 1.0  

[ClickHouse] SHALL support the `join_default_strictness` setting to override the default join type for swarm queries.

##### RQ.SRS-044.Swarm.Joins.Settings.AnyJoinDistinct
version: 1.0  

[ClickHouse] SHALL support the `any_join_distinct_right_table_keys` setting to control the behavior of ANY JOIN operations for swarm queries.

##### RQ.SRS-044.Swarm.Joins.Settings.CrossToInnerRewrite
version: 1.0  

[ClickHouse] SHALL support the `cross_to_inner_join_rewrite` setting to define behavior when CROSS JOIN cannot be rewritten as INNER JOIN for swarm queries. The setting SHALL support values 0 (throw error), 1 (allow slower join), and 2 (force rewrite or error).

##### RQ.SRS-044.Swarm.Joins.Settings.Algorithm
version: 1.0  

[ClickHouse] SHALL support the `join_algorithm` setting to control the join algorithm used for swarm queries.

##### RQ.SRS-044.Swarm.Joins.Settings.AnyTakeLastRow
version: 1.0  

[ClickHouse] SHALL support the `join_any_take_last_row` setting to control behavior when multiple matching rows are found in ANY JOIN operations for swarm queries.

##### RQ.SRS-044.Swarm.Joins.Settings.UseNulls
version: 1.0  

[ClickHouse] SHALL support the `join_use_nulls` setting to control whether NULL values are used for non-matching rows in outer joins for swarm queries.

##### RQ.SRS-044.Swarm.Joins.Settings.PartialMergeRows
version: 1.0  

[ClickHouse] SHALL support the `partial_merge_join_rows_in_right_blocks` setting to control the number of rows in right blocks for partial merge joins in swarm queries.

##### RQ.SRS-044.Swarm.Joins.Settings.OnDiskMaxFiles
version: 1.0  

[ClickHouse] SHALL support the `join_on_disk_max_files_to_merge` setting to control the maximum number of files to merge when using disk-based join algorithms for swarm queries. 


[ClickHouse]: https://clickhouse.com
[Ability Antalya]: https://altinity.com/blog/getting-started-with-altinitys-project-antalya
