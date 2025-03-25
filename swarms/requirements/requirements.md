# SRS-044 Swarm Cluster Query Execution
# Software Requirements Specification

## Table of Contents


## Introduction

This document describes the requirements for the ClickHouse Swarm Cluster functionality, which enables automatic cluster discovery and management of ClickHouse nodes. The swarm cluster architecture consists of two main components:

1. An `initiator cluster` that accepts and plans queries. The queries are load-balanced using a classic network load-balancer.
2. A `swarm cluster` that are used to parallelize query execution. 

Each initiator node receives a query and plans query execution by breaking up execution of the query across all the nodes in the `swarm cluster` and aggregating partial query results from the swarm nodes.
The system is designed to optimize query performance through efficient resource utilization,
cache management, and parallel processing while maintaining fault tolerance and scalability.

## Requirements

### Cluster Discovery

#### RQ.SRS-044.Swarm.ClusterDiscovery.Path

version: 1.0

[ClickHouse] SHALL support automatic cluster discovery through a configured discovery path.


Example:
```xml
<clickhouse>
    <allow_experimental_cluster_discovery>1</allow_experimental_cluster_discovery>
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


### RQ.SRS-001.Swarm.ClusterDiscovery.Authentication

version: 1.0

[ClickHouse] SHALL use the configured secret key for swarm cluster authentication.

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

### Node Registration and Deregistration


### Initiator Nodes



### Swarm Nodes


### Query Processing

#### RQ.SRS-044.Swarm.QueryProcessing.Planning
version: 1.0  

Initiator node SHALL plan query execution by breaking up execution of the query across all the nodes in the swarm cluster.

#### RQ.SRS-044.Swarm.QueryProcessing.PartialQueries
version: 1.0  

Initiator node SHALL send partial queries for specific data ranges to each swarm node.

#### RQ.SRS-044.Swarm.QueryProcessing.SwarmQueryExecution
version: 1.0  

Swarm nodes SHALL execute partial queries and return partial results to the initiator node.

#### RQ.SRS-044.Swarm.QueryProcessing.Aggregation
version: 1.0  

Initiator node SHALL wait for all partial results from the swarm nodes and aggregate them to produce the final result which is returned to the client.

#### Retry Mechanism

#### RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeFailure
version: 1.0  

[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node failure.

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

#### Disk Cache

##### RQ.SRS-044.Swarm.Caching.SwarmLocalDiskCache
version: 1.0  

Swarm nodes SHALL have local disk cache.

#### Query Cache (???)

#### Parquet Metadata Cache

#### System Cache (???)

### Settings

#### object_storage_max_nodes

#### RQ.SRS-044.Swarm.Settings.object_storage_max_nodes
version: 1.0  

[ClickHouse] SHALL support the `object_storage_max_nodes` setting to limit the number of nodes used in swarm for a particular query

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

Query performance using swarm cluster SHALL be not worse than the performance of a single ClickHouse node.


## References

[ClickHouse]: https://clickhouse.com