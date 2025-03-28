# SRS-044 Swarm Cluster Query Execution
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
    * 2.1 [Node Registration and Deregistration](#node-registration-and-deregistration)
        * 2.1.1 [RQ.SRS-044.Swarm.NodeRegistration](#rqsrs-044swarmnoderegistration)
        * 2.1.2 [RQ.SRS-044.Swarm.NodeRegistration.MultipleDiscoverySections](#rqsrs-044swarmnoderegistrationmultiplediscoverysections)
        * 2.1.3 [RQ.SRS-044.Swarm.NodeDeregistration ](#rqsrs-044swarmnodederegistration-)
    * 2.2 [Cluster Discovery](#cluster-discovery)
        * 2.2.1 [RQ.SRS-044.Swarm.ClusterDiscovery.Path](#rqsrs-044swarmclusterdiscoverypath)
        * 2.2.2 [RQ.SRS-044.Swarm.ClusterDiscovery.WrongPath](#rqsrs-044swarmclusterdiscoverywrongpath)
        * 2.2.3 [RQ.SRS-044.Swarm.ClusterDiscovery.MultiplePath](#rqsrs-044swarmclusterdiscoverymultiplepath)
    * 2.3 [Authentification Using Secret](#authentification-using-secret)
        * 2.3.1 [RQ.SRS-001.Swarm.ClusterDiscovery.Authentication](#rqsrs-001swarmclusterdiscoveryauthentication)
        * 2.3.2 [RQ.SRS-001.Swarm.ClusterDiscovery.Authentication.WrongKey](#rqsrs-001swarmclusterdiscoveryauthenticationwrongkey)
        * 2.3.3 [RQ.SRS-001.Swarm.ClusterDiscovery.Authentication.MultipleKey](#rqsrs-001swarmclusterdiscoveryauthenticationmultiplekey)
    * 2.4 [Query Processing](#query-processing)
        * 2.4.1 [RQ.SRS-044.Swarm.QueryProcessing.Planning](#rqsrs-044swarmqueryprocessingplanning)
        * 2.4.2 [RQ.SRS-044.Swarm.QueryProcessing.PartialQueriesExecution](#rqsrs-044swarmqueryprocessingpartialqueriesexecution)
    * 2.5 [Retry Mechanism](#retry-mechanism)
        * 2.5.1 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeFailure](#rqsrs-044swarmqueryprocessingretrymechanismnodefailure)
        * 2.5.2 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.ScaleDown](#rqsrs-044swarmqueryprocessingretrymechanismscaledown)
        * 2.5.3 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeLatency](#rqsrs-044swarmqueryprocessingretrymechanismnodelatency)
        * 2.5.4 [RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NetworkFailure](#rqsrs-044swarmqueryprocessingretrymechanismnetworkfailure)
    * 2.6 [Caching](#caching)
        * 2.6.1 [Disk Cache](#disk-cache)
            * 2.6.1.1 [RQ.SRS-044.Swarm.Caching.SwarmLocalDiskCache](#rqsrs-044swarmcachingswarmlocaldiskcache)
        * 2.6.2 [Query Cache (???)](#query-cache-)
        * 2.6.3 [Parquet Metadata Cache](#parquet-metadata-cache)
        * 2.6.4 [System Cache (???)](#system-cache-)
    * 2.7 [Settings](#settings)
        * 2.7.1 [RQ.SRS-044.Swarm.Settings.object_storage_max_nodes](#rqsrs-044swarmsettingsobject_storage_max_nodes)
    * 2.8 [Observer](#observer)
        * 2.8.1 [RQ.SRS-044.Swarm.ObserverNodes](#rqsrs-044swarmobservernodes)
    * 2.9 [RBAC](#rbac)
        * 2.9.1 [RQ.SRS-044.Swarm.RBAC.RowPolicy](#rqsrs-044swarmrbacrowpolicy)
        * 2.9.2 [RQ.SRS-044.Swarm.RBAC.ColumnPolicy](#rqsrs-044swarmrbaccolumnpolicy)
    * 2.10 [Performance](#performance)
        * 2.10.1 [RQ.SRS-044.Swarm.Performance](#rqsrs-044swarmperformance)




## Introduction

This document describes the requirements for the [ClickHouse] Swarm Cluster functionality, which enables automatic cluster discovery and management of [ClickHouse] nodes. The swarm cluster architecture consists of two main components:

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

[ClickHouse] SHALL support node deregistration through removal of `<clickhouse><remote_servers><swarm>` section in configuration files. Removing node from the swarm cluster does not require node restart.

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

[ClickHouse] SHALL return an error if path provided in `<clickhouse><remote_servers><swarm><discovery>` 
is wrong.

#### RQ.SRS-044.Swarm.ClusterDiscovery.MultiplePath

version: 1.0

[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm><discovery>` 
contains multiple discovery sections.

### Authentification Using Secret

#### RQ.SRS-001.Swarm.ClusterDiscovery.Authentication

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

#### RQ.SRS-001.Swarm.ClusterDiscovery.Authentication.WrongKey

version: 1.0

[ClickHouse] SHALL return an error if secret key provided in `<clickhouse><remote_servers><swarm><discovery>` is wrong.


#### RQ.SRS-001.Swarm.ClusterDiscovery.Authentication.MultipleKey

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

#### Disk Cache

##### RQ.SRS-044.Swarm.Caching.SwarmLocalDiskCache
version: 1.0  

Swarm nodes SHALL have local disk cache.

#### Query Cache (???)

To be defined

#### Parquet Metadata Cache

To be defined

#### System Cache (???)

To be defined

### Settings

#### RQ.SRS-044.Swarm.Settings.object_storage_max_nodes
version: 1.0  

[ClickHouse] SHALL support the `object_storage_max_nodes` setting to limit the number of nodes used in swarm for a particular query

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


[ClickHouse]: https://clickhouse.com
