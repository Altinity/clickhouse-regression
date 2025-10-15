# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_044_Swarm_NodeRegistration = Requirement(
    name="RQ.SRS-044.Swarm.NodeRegistration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support node registration through adding `<clickhouse><remote_servers><swarm><discovery>` section in the configuration file.\n"
        "\n"
        "Example:\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <allow_experimental_cluster_discovery>1</allow_experimental_cluster_discovery>\n"
        "    <remote_servers>\n"
        "        <swarm>\n"
        "            <discovery>\n"
        "                <path>/clickhouse/discovery/swarm</path>\n"
        "                <secret>secret_key</secret>\n"
        "            </discovery>\n"
        "        </swarm>\n"
        "    </remote_servers>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.1.1",
)

RQ_SRS_044_Swarm_NodeRegistration_MultipleDiscoverySections = Requirement(
    name="RQ.SRS-044.Swarm.NodeRegistration.MultipleDiscoverySections",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm>` \n"
        "contains multiple discovery sections.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.1.2",
)

RQ_SRS_044_Swarm_NodeDeregistration = Requirement(
    name="RQ.SRS-044.Swarm.NodeDeregistration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support node deregistration through removal of `<clickhouse><remote_servers><swarm><discovery>` section in swarm node configuration files. Removing node from the swarm cluster does not require initiator node restart.\n"
        "\n"
        "Example:\n"
        "```xml\n"
        "<!-- To deregister a node, remove this section from the configuration -->\n"
        "<clickhouse>\n"
        "    <allow_experimental_cluster_discovery>1</allow_experimental_cluster_discovery>\n"
        "    <remote_servers>\n"
        "        <swarm>\n"
        "            <discovery>\n"
        "                <path>/clickhouse/discovery/swarm</path>\n"
        "                <secret>secret_key</secret>\n"
        "            </discovery>\n"
        "        </swarm>\n"
        "    </remote_servers>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.1.3",
)

RQ_SRS_044_Swarm_ClusterDiscovery_Path = Requirement(
    name="RQ.SRS-044.Swarm.ClusterDiscovery.Path",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatic cluster discovery through a configured discovery path which SHALL uniquely identify a specific swarm cluster.\n"
        "\n"
        "Example:\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <remote_servers>\n"
        "        <swarm>\n"
        "            <discovery>\n"
        "               <...>\n"
        "               <path>/clickhouse/discovery/swarm</path>\n"
        "               <...>\n"
        "            </discovery>\n"
        "        </swarm>\n"
        "    </remote_servers>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.2.1",
)

RQ_SRS_044_Swarm_ClusterDiscovery_WrongPath = Requirement(
    name="RQ.SRS-044.Swarm.ClusterDiscovery.WrongPath",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not add node to the swarm cluster if path provided in `<clickhouse><remote_servers><swarm><discovery>` is different from the path provided in the initiator node configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.2.2",
)

RQ_SRS_044_Swarm_ClusterDiscovery_MultiplePaths = Requirement(
    name="RQ.SRS-044.Swarm.ClusterDiscovery.MultiplePaths",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm><discovery>` \n"
        "contains multiple discovery paths.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.2.3",
)

RQ_SRS_044_Swarm_ClusterDiscovery_Authentication = Requirement(
    name="RQ.SRS-044.Swarm.ClusterDiscovery.Authentication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use the configured secret key for swarm cluster node authentication.\n"
        "\n"
        "Example:\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <remote_servers>\n"
        "        <swarm>\n"
        "            <discovery>\n"
        "               <...>\n"
        "               <secret>secret_key</secret>\n"
        "               <...>\n"
        "            </discovery>\n"
        "        </swarm>\n"
        "    </remote_servers>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.3.1",
)

RQ_SRS_044_Swarm_ClusterDiscovery_Authentication_WrongKey = Requirement(
    name="RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.WrongKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not add node to the swarm cluster if secret key provided in `<clickhouse><remote_servers><swarm><discovery>` is different from the secret key provided in the initiator node configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.3.2",
)

RQ_SRS_044_Swarm_ClusterDiscovery_Authentication_MultipleKeys = Requirement(
    name="RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.MultipleKeys",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if `<clickhouse><remote_servers><swarm><discovery>` contains multiple secret keys.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.3.3",
)

RQ_SRS_044_Swarm_QueryProcessing_Planning = Requirement(
    name="RQ.SRS-044.Swarm.QueryProcessing.Planning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Initiator node SHALL plan query execution by breaking up execution of the query across all the nodes in the swarm cluster.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.4.1",
)

RQ_SRS_044_Swarm_QueryProcessing_PartialQueriesExecution = Requirement(
    name="RQ.SRS-044.Swarm.QueryProcessing.PartialQueriesExecution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Initiator node SHALL send partial queries to swarm nodes. Swarm nodes SHALL execute partial queries and return partial results to the initiator node. Then initiator node SHALL aggregate results. \n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.4.2",
)

RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_NodeFailure = Requirement(
    name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeFailure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node failure during any point of query execution.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.5.1",
)

RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_ScaleDown = Requirement(
    name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.ScaleDown",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node disappearance due to scale-down.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.5.2",
)

RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_NodeLatency = Requirement(
    name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeLatency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support a retry mechanism for swarm queries in case of node latency or unresponsiveness.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.5.3",
)

RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_NetworkFailure = Requirement(
    name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NetworkFailure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support a retry mechanism for swarm queries in case of network failure.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.5.4",
)

RQ_SRS_044_Swarm_Caching_LocalDiskCache = Requirement(
    name="RQ.SRS-044.Swarm.Caching.LocalDiskCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL support local disk cache.\n"
        "Swarm nodes SHALL not download data from storage data files if it is cached.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.1.1",
)

RQ_SRS_044_Swarm_Caching_LocalDiskCacheConsistency = Requirement(
    name="RQ.SRS-044.Swarm.Caching.LocalDiskCacheConsistency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL return the same result for queries when local disk cache is enabled and disabled.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.1.2",
)

RQ_SRS_044_Swarm_Caching_LocalDiskCachePerformance = Requirement(
    name="RQ.SRS-044.Swarm.Caching.LocalDiskCachePerformance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL not run query much slower if data for the query is not cached in comparison with disabled local disk cache.\n"
        "Swarm nodes SHALL run query faster if data for the query is cached in comparison with disabled local disk cache.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.1.3",
)

RQ_SRS_044_Swarm_Caching_DiskCacheUpdates = Requirement(
    name="RQ.SRS-044.Swarm.Caching.DiskCacheUpdates",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL run query and update disk cache if data for query is changed.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.1.4",
)

RQ_SRS_044_Swarm_Caching_DiskCacheNoDiskSpace = Requirement(
    name="RQ.SRS-044.Swarm.Caching.DiskCacheNoDiskSpace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL not cache the data if node has no enough space to cache it.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.1.5",
)

RQ_SRS_044_Swarm_Caching_QueryCache = Requirement(
    name="RQ.SRS-044.Swarm.Caching.QueryCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL support query cache. \n"
        "Swarm nodes SHALL not run query if it is cached on the node.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.2.1",
)

RQ_SRS_044_Swarm_Caching_QueryCacheConsistency = Requirement(
    name="RQ.SRS-044.Swarm.Caching.QueryCacheConsistency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL return the same result for queries when query cache is enabled and disabled.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.2.2",
)

RQ_SRS_044_Swarm_Caching_QueryCachePerformance = Requirement(
    name="RQ.SRS-044.Swarm.Caching.QueryCachePerformance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL not perform query much slower if query is not cached in comparison with disabled query cache.\n"
        "Swarm nodes SHALL perform query faster if query is cached in comparison with disabled query cache.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.2.3",
)

RQ_SRS_044_Swarm_Caching_QueryCacheUpdates = Requirement(
    name="RQ.SRS-044.Swarm.Caching.QueryCacheUpdates",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL run query and update query cache if data for query is changed.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.2.4",
)

RQ_SRS_044_Swarm_Caching_QueryCacheNoDiskSpace = Requirement(
    name="RQ.SRS-044.Swarm.Caching.QueryCacheNoDiskSpace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL not cache the query if node has no enough space to cache it.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.2.5",
)

RQ_SRS_044_Swarm_Caching_ParquetMetadataCache = Requirement(
    name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL support parquet metadata cache. \n"
        "Swarm nodes SHALL not download parquet metadata from storage if parquet metadata is cached.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.3.1",
)

RQ_SRS_044_Swarm_Caching_ParquetMetadataCacheConsistency = Requirement(
    name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheConsistency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL return the same result for queries with enabled and disabled parquet metadata cache.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.3.2",
)

RQ_SRS_044_Swarm_Caching_ParquetMetadataCachePerformance = Requirement(
    name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCachePerformance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL not perform query much slower if parquet metadata is not cached in comparison with parquet metadata cache.\n"
        "Swarm nodes SHALL perform query faster if parquet metadata is cached in comparison with disabled parquet metadata cache.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.3.3",
)

RQ_SRS_044_Swarm_Caching_ParquetMetadataCacheUpdates = Requirement(
    name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheUpdates",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL run query and update parquet metadata cache if data for query is changed.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.3.4",
)

RQ_SRS_044_Swarm_Caching_ParquetMetadataCacheNoDiskSpace = Requirement(
    name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheNoDiskSpace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Swarm nodes SHALL not cache the parquet metadata if node has no enough space to cache it.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.6.3.5",
)

RQ_SRS_044_Swarm_Settings_object_storage_max_nodes = Requirement(
    name="RQ.SRS-044.Swarm.Settings.object_storage_max_nodes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `object_storage_max_nodes` setting to limit the number of nodes used in swarm cluster for a particular query\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.7.1",
)

RQ_SRS_044_Swarm_ObserverNodes = Requirement(
    name="RQ.SRS-044.Swarm.ObserverNodes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support specifying a swarm node as an observer.\n"
        "This means that this node can use this cluster but doesn't get partial queries to execute.\n"
        "[Clickhouse] SHALL support multiple observers.\n"
        "\n"
        "Example:\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <remote_servers>\n"
        "        <swarm>\n"
        "            <discovery>\n"
        "                ...\n"
        "                <observer>true</observer>\n"
        "                ...\n"
        "            </discovery>\n"
        "        </swarm>\n"
        "    </remote_servers>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.8.1",
)

RQ_SRS_044_Swarm_RBAC_RowPolicy = Requirement(
    name="RQ.SRS-044.Swarm.RBAC.RowPolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support row-level access control for swarm queries on the initiator.  \n"
        "Swarm queries SHALL be anonymized, and the authority model is enforced only on the initiator. \n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.9.1",
)

RQ_SRS_044_Swarm_RBAC_ColumnPolicy = Requirement(
    name="RQ.SRS-044.Swarm.RBAC.ColumnPolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support column-level access control for swarm queries on the initiator. \n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.9.2",
)

RQ_SRS_044_Swarm_Performance = Requirement(
    name="RQ.SRS-044.Swarm.Performance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "Query performance using swarm cluster SHALL be not worse than the performance of a single ClickHouse node\n"
        "for queries that accesses data from multiple files in average.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.10.1",
)

RQ_SRS_044_Swarm_Joins = Requirement(
    name="RQ.SRS-044.Swarm.Joins",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support joins for swarm queries. This includes both standard SQL join types and ClickHouse-specific join types.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.11.1",
)

RQ_SRS_044_Swarm_Joins_Inner = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Inner",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support inner joins for swarm queries. Inner joins SHALL return only matching rows from both tables.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.2.1",
)

RQ_SRS_044_Swarm_Joins_LeftOuter = Requirement(
    name="RQ.SRS-044.Swarm.Joins.LeftOuter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support left outer joins for swarm queries. Left outer joins SHALL return non-matching rows from the left table in addition to matching rows. \n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.2.2",
)

RQ_SRS_044_Swarm_Joins_RightOuter = Requirement(
    name="RQ.SRS-044.Swarm.Joins.RightOuter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support right outer joins for swarm queries. Right outer joins SHALL return non-matching rows from the right table in addition to matching rows. \n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.2.3",
)

RQ_SRS_044_Swarm_Joins_FullOuter = Requirement(
    name="RQ.SRS-044.Swarm.Joins.FullOuter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support full outer joins for swarm queries. Full outer joins SHALL return non-matching rows from both tables in addition to matching rows. \n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.2.4",
)

RQ_SRS_044_Swarm_Joins_Cross = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Cross",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support cross joins for swarm queries. Cross joins SHALL produce a cartesian product of whole tables without requiring join keys. An alternative syntax for CROSS JOIN is specifying multiple tables in the FROM clause separated by commas.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.2.5",
)

RQ_SRS_044_Swarm_Joins_Semi = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Semi",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        '[ClickHouse] SHALL support left semi joins and right semi joins for swarm queries. Semi joins SHALL act as an allowlist on "join keys" without producing a cartesian product.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.3.1",
)

RQ_SRS_044_Swarm_Joins_Anti = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Anti",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        '[ClickHouse] SHALL support left anti joins and right anti joins for swarm queries. Anti joins SHALL act as a denylist on "join keys" without producing a cartesian product.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.3.2",
)

RQ_SRS_044_Swarm_Joins_Any = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Any",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support left any joins, right any joins, and inner any joins for swarm queries. Any joins SHALL partially (for opposite side of LEFT and RIGHT) or completely (for INNER and FULL) disable the cartesian product for standard JOIN types.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.3.3",
)

RQ_SRS_044_Swarm_Joins_Asof = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Asof",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support ASOF joins and left ASOF joins for swarm queries. ASOF joins SHALL enable joining sequences with a non-exact match.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.3.4",
)

RQ_SRS_044_Swarm_Joins_Paste = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Paste",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support paste joins for swarm queries. Paste joins SHALL perform a horizontal concatenation of two tables.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.3.5",
)

RQ_SRS_044_Swarm_Joins_Settings_DefaultStrictness = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.DefaultStrictness",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `join_default_strictness` setting to override the default join type for swarm queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.1",
)

RQ_SRS_044_Swarm_Joins_Settings_AnyJoinDistinct = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.AnyJoinDistinct",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `any_join_distinct_right_table_keys` setting to control the behavior of ANY JOIN operations for swarm queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.2",
)

RQ_SRS_044_Swarm_Joins_Settings_CrossToInnerRewrite = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.CrossToInnerRewrite",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `cross_to_inner_join_rewrite` setting to define behavior when CROSS JOIN cannot be rewritten as INNER JOIN for swarm queries. The setting SHALL support values 0 (throw error), 1 (allow slower join), and 2 (force rewrite or error).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.3",
)

RQ_SRS_044_Swarm_Joins_Settings_Algorithm = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.Algorithm",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `join_algorithm` setting to control the join algorithm used for swarm queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.4",
)

RQ_SRS_044_Swarm_Joins_Settings_AnyTakeLastRow = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.AnyTakeLastRow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `join_any_take_last_row` setting to control behavior when multiple matching rows are found in ANY JOIN operations for swarm queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.5",
)

RQ_SRS_044_Swarm_Joins_Settings_UseNulls = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.UseNulls",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `join_use_nulls` setting to control whether NULL values are used for non-matching rows in outer joins for swarm queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.6",
)

RQ_SRS_044_Swarm_Joins_Settings_PartialMergeRows = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.PartialMergeRows",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `partial_merge_join_rows_in_right_blocks` setting to control the number of rows in right blocks for partial merge joins in swarm queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.11.4.7",
)

RQ_SRS_044_Swarm_Joins_Settings_OnDiskMaxFiles = Requirement(
    name="RQ.SRS-044.Swarm.Joins.Settings.OnDiskMaxFiles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the `join_on_disk_max_files_to_merge` setting to control the maximum number of files to merge when using disk-based join algorithms for swarm queries. \n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[Ability Antalya]: https://altinity.com/blog/getting-started-with-altinitys-project-antalya\n"
    ),
    link=None,
    level=4,
    num="2.11.4.8",
)

SRS_044_Swarm_Cluster_Query_Execution = Specification(
    name="SRS-044 Swarm Cluster Query Execution",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Requirements", level=1, num="2"),
        Heading(name="Node Registration and Deregistration", level=2, num="2.1"),
        Heading(name="RQ.SRS-044.Swarm.NodeRegistration", level=3, num="2.1.1"),
        Heading(
            name="RQ.SRS-044.Swarm.NodeRegistration.MultipleDiscoverySections",
            level=3,
            num="2.1.2",
        ),
        Heading(name="RQ.SRS-044.Swarm.NodeDeregistration", level=3, num="2.1.3"),
        Heading(name="Cluster Discovery", level=2, num="2.2"),
        Heading(name="RQ.SRS-044.Swarm.ClusterDiscovery.Path", level=3, num="2.2.1"),
        Heading(
            name="RQ.SRS-044.Swarm.ClusterDiscovery.WrongPath", level=3, num="2.2.2"
        ),
        Heading(
            name="RQ.SRS-044.Swarm.ClusterDiscovery.MultiplePaths", level=3, num="2.2.3"
        ),
        Heading(name="Authentication Using Secret", level=2, num="2.3"),
        Heading(
            name="RQ.SRS-044.Swarm.ClusterDiscovery.Authentication",
            level=3,
            num="2.3.1",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.WrongKey",
            level=3,
            num="2.3.2",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.ClusterDiscovery.Authentication.MultipleKeys",
            level=3,
            num="2.3.3",
        ),
        Heading(name="Query Processing", level=2, num="2.4"),
        Heading(name="RQ.SRS-044.Swarm.QueryProcessing.Planning", level=3, num="2.4.1"),
        Heading(
            name="RQ.SRS-044.Swarm.QueryProcessing.PartialQueriesExecution",
            level=3,
            num="2.4.2",
        ),
        Heading(name="Retry Mechanism", level=2, num="2.5"),
        Heading(
            name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeFailure",
            level=3,
            num="2.5.1",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.ScaleDown",
            level=3,
            num="2.5.2",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NodeLatency",
            level=3,
            num="2.5.3",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.QueryProcessing.RetryMechanism.NetworkFailure",
            level=3,
            num="2.5.4",
        ),
        Heading(name="Caching", level=2, num="2.6"),
        Heading(name="Local Disk Cache", level=3, num="2.6.1"),
        Heading(name="RQ.SRS-044.Swarm.Caching.LocalDiskCache", level=4, num="2.6.1.1"),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.LocalDiskCacheConsistency",
            level=4,
            num="2.6.1.2",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.LocalDiskCachePerformance",
            level=4,
            num="2.6.1.3",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.DiskCacheUpdates", level=4, num="2.6.1.4"
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.DiskCacheNoDiskSpace", level=4, num="2.6.1.5"
        ),
        Heading(name="Query Cache", level=3, num="2.6.2"),
        Heading(name="RQ.SRS-044.Swarm.Caching.QueryCache", level=4, num="2.6.2.1"),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.QueryCacheConsistency",
            level=4,
            num="2.6.2.2",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.QueryCachePerformance",
            level=4,
            num="2.6.2.3",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.QueryCacheUpdates", level=4, num="2.6.2.4"
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.QueryCacheNoDiskSpace",
            level=4,
            num="2.6.2.5",
        ),
        Heading(name="Parquet Metadata Cache", level=3, num="2.6.3"),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCache", level=4, num="2.6.3.1"
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheConsistency",
            level=4,
            num="2.6.3.2",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCachePerformance",
            level=4,
            num="2.6.3.3",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheUpdates",
            level=4,
            num="2.6.3.4",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Caching.ParquetMetadataCacheNoDiskSpace",
            level=4,
            num="2.6.3.5",
        ),
        Heading(name="Settings", level=2, num="2.7"),
        Heading(
            name="RQ.SRS-044.Swarm.Settings.object_storage_max_nodes",
            level=3,
            num="2.7.1",
        ),
        Heading(name="Observer", level=2, num="2.8"),
        Heading(name="RQ.SRS-044.Swarm.ObserverNodes", level=3, num="2.8.1"),
        Heading(name="RBAC", level=2, num="2.9"),
        Heading(name="RQ.SRS-044.Swarm.RBAC.RowPolicy", level=3, num="2.9.1"),
        Heading(name="RQ.SRS-044.Swarm.RBAC.ColumnPolicy", level=3, num="2.9.2"),
        Heading(name="Performance", level=2, num="2.10"),
        Heading(name="RQ.SRS-044.Swarm.Performance", level=3, num="2.10.1"),
        Heading(name="Joins", level=2, num="2.11"),
        Heading(name="RQ.SRS-044.Swarm.Joins", level=3, num="2.11.1"),
        Heading(name="Standard Join Types", level=3, num="2.11.2"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Inner", level=4, num="2.11.2.1"),
        Heading(name="RQ.SRS-044.Swarm.Joins.LeftOuter", level=4, num="2.11.2.2"),
        Heading(name="RQ.SRS-044.Swarm.Joins.RightOuter", level=4, num="2.11.2.3"),
        Heading(name="RQ.SRS-044.Swarm.Joins.FullOuter", level=4, num="2.11.2.4"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Cross", level=4, num="2.11.2.5"),
        Heading(name="ClickHouse-Specific Join Types", level=3, num="2.11.3"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Semi", level=4, num="2.11.3.1"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Anti", level=4, num="2.11.3.2"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Any", level=4, num="2.11.3.3"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Asof", level=4, num="2.11.3.4"),
        Heading(name="RQ.SRS-044.Swarm.Joins.Paste", level=4, num="2.11.3.5"),
        Heading(name="Join Settings", level=3, num="2.11.4"),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.DefaultStrictness",
            level=4,
            num="2.11.4.1",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.AnyJoinDistinct",
            level=4,
            num="2.11.4.2",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.CrossToInnerRewrite",
            level=4,
            num="2.11.4.3",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.Algorithm", level=4, num="2.11.4.4"
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.AnyTakeLastRow",
            level=4,
            num="2.11.4.5",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.UseNulls", level=4, num="2.11.4.6"
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.PartialMergeRows",
            level=4,
            num="2.11.4.7",
        ),
        Heading(
            name="RQ.SRS-044.Swarm.Joins.Settings.OnDiskMaxFiles",
            level=4,
            num="2.11.4.8",
        ),
    ),
    requirements=(
        RQ_SRS_044_Swarm_NodeRegistration,
        RQ_SRS_044_Swarm_NodeRegistration_MultipleDiscoverySections,
        RQ_SRS_044_Swarm_NodeDeregistration,
        RQ_SRS_044_Swarm_ClusterDiscovery_Path,
        RQ_SRS_044_Swarm_ClusterDiscovery_WrongPath,
        RQ_SRS_044_Swarm_ClusterDiscovery_MultiplePaths,
        RQ_SRS_044_Swarm_ClusterDiscovery_Authentication,
        RQ_SRS_044_Swarm_ClusterDiscovery_Authentication_WrongKey,
        RQ_SRS_044_Swarm_ClusterDiscovery_Authentication_MultipleKeys,
        RQ_SRS_044_Swarm_QueryProcessing_Planning,
        RQ_SRS_044_Swarm_QueryProcessing_PartialQueriesExecution,
        RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_NodeFailure,
        RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_ScaleDown,
        RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_NodeLatency,
        RQ_SRS_044_Swarm_QueryProcessing_RetryMechanism_NetworkFailure,
        RQ_SRS_044_Swarm_Caching_LocalDiskCache,
        RQ_SRS_044_Swarm_Caching_LocalDiskCacheConsistency,
        RQ_SRS_044_Swarm_Caching_LocalDiskCachePerformance,
        RQ_SRS_044_Swarm_Caching_DiskCacheUpdates,
        RQ_SRS_044_Swarm_Caching_DiskCacheNoDiskSpace,
        RQ_SRS_044_Swarm_Caching_QueryCache,
        RQ_SRS_044_Swarm_Caching_QueryCacheConsistency,
        RQ_SRS_044_Swarm_Caching_QueryCachePerformance,
        RQ_SRS_044_Swarm_Caching_QueryCacheUpdates,
        RQ_SRS_044_Swarm_Caching_QueryCacheNoDiskSpace,
        RQ_SRS_044_Swarm_Caching_ParquetMetadataCache,
        RQ_SRS_044_Swarm_Caching_ParquetMetadataCacheConsistency,
        RQ_SRS_044_Swarm_Caching_ParquetMetadataCachePerformance,
        RQ_SRS_044_Swarm_Caching_ParquetMetadataCacheUpdates,
        RQ_SRS_044_Swarm_Caching_ParquetMetadataCacheNoDiskSpace,
        RQ_SRS_044_Swarm_Settings_object_storage_max_nodes,
        RQ_SRS_044_Swarm_ObserverNodes,
        RQ_SRS_044_Swarm_RBAC_RowPolicy,
        RQ_SRS_044_Swarm_RBAC_ColumnPolicy,
        RQ_SRS_044_Swarm_Performance,
        RQ_SRS_044_Swarm_Joins,
        RQ_SRS_044_Swarm_Joins_Inner,
        RQ_SRS_044_Swarm_Joins_LeftOuter,
        RQ_SRS_044_Swarm_Joins_RightOuter,
        RQ_SRS_044_Swarm_Joins_FullOuter,
        RQ_SRS_044_Swarm_Joins_Cross,
        RQ_SRS_044_Swarm_Joins_Semi,
        RQ_SRS_044_Swarm_Joins_Anti,
        RQ_SRS_044_Swarm_Joins_Any,
        RQ_SRS_044_Swarm_Joins_Asof,
        RQ_SRS_044_Swarm_Joins_Paste,
        RQ_SRS_044_Swarm_Joins_Settings_DefaultStrictness,
        RQ_SRS_044_Swarm_Joins_Settings_AnyJoinDistinct,
        RQ_SRS_044_Swarm_Joins_Settings_CrossToInnerRewrite,
        RQ_SRS_044_Swarm_Joins_Settings_Algorithm,
        RQ_SRS_044_Swarm_Joins_Settings_AnyTakeLastRow,
        RQ_SRS_044_Swarm_Joins_Settings_UseNulls,
        RQ_SRS_044_Swarm_Joins_Settings_PartialMergeRows,
        RQ_SRS_044_Swarm_Joins_Settings_OnDiskMaxFiles,
    ),
    content=r"""
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
        * 2.11.4 [Join Settings](#join-settings)
            * 2.11.4.1 [RQ.SRS-044.Swarm.Joins.Settings.DefaultStrictness](#rqsrs-044swarmjoinssettingsdefaultstrictness)
            * 2.11.4.2 [RQ.SRS-044.Swarm.Joins.Settings.AnyJoinDistinct](#rqsrs-044swarmjoinssettingsanyjoindistinct)
            * 2.11.4.3 [RQ.SRS-044.Swarm.Joins.Settings.CrossToInnerRewrite](#rqsrs-044swarmjoinssettingscrosstoinnerrewrite)
            * 2.11.4.4 [RQ.SRS-044.Swarm.Joins.Settings.Algorithm](#rqsrs-044swarmjoinssettingsalgorithm)
            * 2.11.4.5 [RQ.SRS-044.Swarm.Joins.Settings.AnyTakeLastRow](#rqsrs-044swarmjoinssettingsanytakelastrow)
            * 2.11.4.6 [RQ.SRS-044.Swarm.Joins.Settings.UseNulls](#rqsrs-044swarmjoinssettingsusenulls)
            * 2.11.4.7 [RQ.SRS-044.Swarm.Joins.Settings.PartialMergeRows](#rqsrs-044swarmjoinssettingspartialmergerows)
            * 2.11.4.8 [RQ.SRS-044.Swarm.Joins.Settings.OnDiskMaxFiles](#rqsrs-044swarmjoinssettingsondiskmaxfiles)


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

#### Join Settings

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
""",
)
