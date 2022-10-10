import uuid
import pyarrow.parquet as pq

from testflows._core.testtype import TestSubType
from testflows.core.name import basename, parentname
from testflows.core import current
from helpers.common import *
from s3.tests.common import *
from testflows.asserts import values, error, snapshot


@TestStep(Given)
def instrument_cluster_nodes(self, test, cluster_nodes, always_dump=True):
    """Instrument logs on cluster nodes."""
    for name in cluster_nodes:
        instrument_clickhouse_server_log(
            node=self.context.cluster.node(name), test=test, always_dump=always_dump
        )


@TestStep(When)
def create_simple_table(
    self,
    node=None,
    table_name="test",
    cluster_name="'Cluster_3shards_with_3replicas'",
    values="Id Int32, partition Int32",
    manual_cleanup=False,
):
    """Create simple table with timeout option.

    :param node: node for table
    :param table_name: table name
    :param cluster_name: name of cluster for replicated table
    :param manual_cleanup: manual cleanup
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")
    try:
        retry(node.query, timeout=100, delay=1)(
            f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
            f" ({values}) "
            "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
            f"/{table_name}'"
            ", '{replica}') "
            "ORDER BY Id PARTITION BY Id",
            steps=False,
        )
        yield table_name
    finally:
        with Finally("I clean up"):
            if manual_cleanup is False:
                with By("dropping table if exists"):
                    node.query(
                        f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
                    )


@TestStep(When)
def insert_const(self, name, node=None):
    """Insert some data into table."""
    if node is None:
        node = self.context.node

    with By("Inserting 0's"):
        node.query(
            f"""
            INSERT INTO {name} VALUES 
                (0,0,0,0,0,0,0,0,0,0,0,'2022-01-01','2022-01-01 00:00:00','A','B',[0,0,0],(0,0,0,0,0,0,0,0,0,0,0,'2022-01-01','2022-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}), {{'a':0, 'b':0}}), (1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1), {{'a':1, 'b':1}}), {{'a':1, 'b':1}}), (0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.79769e+308,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.79769e+308,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}) , {{'a':0, 'b':0}}), (255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.79769e+308,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.79769e+308,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}), {{'a':0, 'b':0}})""",
            #     (1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1), {{'a':1, 'b':1}}), {{'a':1, 'b':1}}),
            #     (0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.797e+327,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.797e+327,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}) , {{'a':0, 'b':0}}),
            #     (255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.797e+327,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.797e+327,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}), {{'a':0, 'b':0}})
            #     (Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,[Null,Null,Null],(Null), {{Null:Null}})
            # """,
        )

    return


@TestStep(When)
def insert_null(self, name, node=None):
    """Insert some null data into table."""
    if node is None:
        node = self.context.node

    with By("Inserting Nulls"):
        node.query(
            f"INSERT INTO {name} VALUES (Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,[Null,Null,Null],(Null), {{Null:Null}}) FORMAT Parquet"
        )

    return


@TestStep(When)
def insert_array_const(self, name, node=None):
    """Insert some array data into table."""
    if node is None:
        node = self.context.node

    with By("Inserting 0's"):
        node.query(
            f"""
            INSERT INTO {name} VALUES
                ([0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['2022-01-01'],['2022-01-01 00:00:00'],['A'],['B'],[[0,0,0]],[(0,0,0,0,0,0,0,0,0,0,0,'2022-01-01','2022-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}})], [{{'a':0, 'b':0}}]) FORMAT Parquet"
            """
        )

    with And("Inserting 1's"):
        node.query(
            f"INSERT INTO {name} VALUES ([1],[1],[1],[1],[1],[1],[1],[1],[1],[1],[0.5],['2022-01-01'],['2022-01-01 00:00:00'],['A'],['B'],[[1,1,1]],[(1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1), {{'a':1, 'b':1}})], [{{'a':1, 'b':1}})] FORMAT Parquet"
        )

    with And("Inserting mins"):
        node.query(
            f"INSERT INTO {name} VALUES ([0],[-128],[0],[-32768],[0],[-2147483648],[0],[-9223372036854775808],[-3.40282347e+38],[-1.79769e+308],[-0.9999999999999999999999999999999999999],['1970-01-01'],['1970-01-01 00:00:00'],['A'],['B'],[[0,0,0]],[(0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.79769e+308,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}})] , [{{'a':0, 'b':0}}]) FORMAT Parquet"
        )

    with And("Inserting maxes"):
        node.query(
            f"INSERT INTO {name} VALUES ([255],[127],[65535],[32767],[4294967295],[2147483647],[18446744073709551615],[9223372036854775807],[3.40282347e+38],[1.79769e+308],[0.9999999999999999999999999999999999999],['2149-06-06'],['2106-02-07 06:28:15'],['A'],['B'],[[0,0,0]],[(255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.79769e+308,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}})], [{{'a':0, 'b':0}}]) FORMAT Parquet"
        )

    return


@TestStep(Given)
def allow_experimental_map_type(self):
    """Set allow_experimental_map_type = 1"""
    setting = ("allow_experimental_map_type", 1)
    default_query_settings = None

    try:
        with By("adding allow_experimental_map_type to the default query settings"):
            default_query_settings = getsattr(
                current().context, "default_query_settings", []
            )
            default_query_settings.append(setting)
        yield
    finally:
        with Finally(
            "I remove allow_experimental_map_type from the default query settings"
        ):
            if default_query_settings:
                try:
                    default_query_settings.pop(default_query_settings.index(setting))
                except ValueError:
                    pass


@TestStep(Given)
def table(self, engine, name="table0", create="CREATE"):
    """Create a table."""
    node = current().context.node

    try:
        with By("creating table"):
            node.query(
                f"""
                {create} TABLE {name} (
                    a UInt8,
                    b Int8,
                    c UInt16,
                    d Int16,
                    e UInt32,
                    f Int32,
                    g UInt64,
                    h Int64,
                    i Float32,
                    j Float64,
                    k Decimal128(38),
                    l Date,
                    m DateTime,
                    n String,
                    o FixedString(16),
                    p Array(UInt8),
                    q Tuple(
                        UInt8,
                        Int8,
                        UInt16, 
                        Int16, 
                        UInt32, 
                        Int32, 
                        UInt64, 
                        Int64, 
                        Float32, 
                        Float64, 
                        Decimal128(38), 
                        Date, 
                        DateTime, 
                        String, 
                        FixedString(8), 
                        Array(UInt8), 
                        Tuple(
                            UInt8,
                            UInt8,
                            UInt8
                        ), 
                        Map(String, UInt64)),
                    r Map(String, UInt64),

                    aa Array(UInt8),
                    ab Array(Int8),
                    ac Array(UInt16),
                    ad Array(Int16),
                    ae Array(UInt32),
                    af Array(Int32),
                    ag Array(UInt64),
                    ah Array(Int64),
                    ai Array(Float32),
                    aj Array(Float64),
                    ak Array(Decimal128(38)),
                    al Array(Date),
                    am Array(DateTime),
                    an Array(String),
                    ao Array(FixedString(16)),
                    ap Array(Array(UInt8)),
                    aq Tuple(
                        UInt8,
                        Int8,
                        UInt16, 
                        Int16, 
                        UInt32, 
                        Int32, 
                        UInt64, 
                        Int64, 
                        Float32, 
                        Float64, 
                        Decimal128(38), 
                        Date, 
                        DateTime, 
                        String, 
                        FixedString(8), 
                        Array(UInt8), 
                        Tuple(
                            UInt8,
                            UInt8,
                            UInt8
                            ), 
                        Map(String, UInt64)),
                    ar Array(Map(String, UInt64)),

                    na Nullable(UInt8),
                    nb Nullable(Int8),
                    nc Nullable(UInt16), 
                    nd Nullable(Int16), 
                    ne Nullable(UInt32), 
                    nf Nullable(Int32), 
                    ng Nullable(UInt64), 
                    nh Nullable(Int64), 
                    ni Nullable(Float32), 
                    nj Nullable(Float64), 
                    nk Nullable(Decimal128(38)), 
                    nl Nullable(Date), 
                    nm Nullable(DateTime), 
                    nn Nullable(String), 
                    no Nullable(FixedString(8)), 
                    np Array(Nullable(UInt8)), 
                    nq Tuple(
                        Nullable(UInt8),
                        Nullable(Int8),
                        Nullable(UInt16), 
                        Nullable(Int16), 
                        Nullable(UInt32), 
                        Nullable(Int32), 
                        Nullable(UInt64), 
                        Nullable(Int64), 
                        Nullable(Float32), 
                        Nullable(Float64), 
                        Nullable(Decimal128(38)), 
                        Nullable(Date), 
                        Nullable(DateTime), 
                        Nullable(String), 
                        Nullable(FixedString(8)), 
                        Array(Nullable(UInt8)), 
                        Tuple(
                            Nullable(UInt8),
                            Nullable(UInt8),
                            Nullable(UInt8)
                            ),
                    nr Map(Nullable(String), Nullable(UInt64)))

                    ana Array(Nullable(UInt8))),
                    anb Array(Nullable(Int8)),
                    anc Array(Nullable(UInt16)),
                    and Array(Nullable(Int16)),
                    ane Array(Nullable(UInt32)),
                    anf Array(Nullable(Int32)),
                    ang Array(Nullable(UInt64)),
                    anh Array(Nullable(Int64)),
                    ani Array(Nullable(Float32)),
                    anj Array(Nullable(Float64)),
                    ank Array(Nullable(Decimal128(38))),
                    anl Array(Nullable(Date)),
                    anm Array(Nullable(DateTime)),
                    ann Array(Nullable(String)),
                    ano Array(Nullable(FixedString(16))),
                    anp Array(Nullable(Array(UInt8))),
                    anq Tuple(
                        Nullable(UInt8),
                        Nullable(Int8),
                        Nullable(UInt16), 
                        Nullable(Int16), 
                        Nullable(UInt32), 
                        Nullable(Int32), 
                        Nullable(UInt64), 
                        Nullable(Int64), 
                        Nullable(Float32), 
                        Nullable(Float64), 
                        Nullable(Decimal128(38)), 
                        Nullable(Date), 
                        Nullable(DateTime), 
                        Nullable(String), 
                        Nullable(FixedString(8)), 
                        Array(Nullable(UInt8)), 
                        Tuple(
                            Nullable(UInt8),
                            Nullable(UInt8),
                            Nullable(UInt8)
                            ), 
                        Map(Nullable(String), Nullable(UInt64))),
                    anr Array(Map(Nullable(String), Nullable(UInt64)))
                )
                Engine = {engine}
            """
            )
        yield

    finally:
        with Finally("drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep(When)
def insert(
    self,
    table_name,
    values=None,
    partitions=1,
    parts_per_partition=1,
    block_size=1000,
    no_checks=False,
    settings=[],
    node=None,
    table_engine=None,
):
    """Insert data having specified number of partitions and parts."""
    if node is None:
        node = self.context.node

    if table_engine is None:
        table_engine = self.context.table_engine

    if values is None:
        if table_engine in (
            "MergeTree",
            "ReplacingMergeTree",
            "SummingMergeTree",
            "AggregatingMergeTree",
        ):
            values = ",".join(
                f"({x},{y})"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

        if table_engine in ("CollapsingMergeTree", "VersionedCollapsingMergeTree"):
            values = ",".join(
                f"({x},{y},1)"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

        if table_engine == "GraphiteMergeTree":
            values = ",".join(
                f"({x},{y}, '1', toDateTime(10), 10, 10)"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

    return node.query(
        f"INSERT INTO {table_name} VALUES {values}",
        settings=[("max_block_size", block_size)] + settings,
        no_checks=no_checks,
    )


@TestStep(Given)
def create_view(self, view_type, view_name, condition, node=None):
    """Create view."""
    if node is None:
        node = self.context.node

    try:
        with Given("I create view"):
            if view_type == "LIVE":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_live_view", 1)],
                )
            elif view_type == "WINDOW":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_window_view", 1)],
                )
            else:
                node.query(f"CREATE {view_type} VIEW {view_name} as {condition}")

        yield
    finally:
        with Finally("I delete view"):
            node.query(f"DROP VIEW {view_name} SYNC")


def getuid():
    if current().subtype == TestSubType.Example:
        testname = (
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',','')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',','')}"
    return testname + "_" + str(uuid.uuid1()).replace("-", "_")


@TestStep(Given)
def upload_s3_parquet(self, s3_client):
    """Upload Parquet data file to s3."""

    with By("Uploading a file"):
        s3_client.upload_file(
            "/var/lib/clickhouse/user_files/data.Parquet",
            self.context.uri,
            "/s3_Table/data.Parquet",
        )


@TestStep(Then)
def check_query(self, query, expected=None):
    node = current().context.node
    name = basename(current().name)

    with By(f"executing query", description=query):
        r = node.query(query).output.strip()

    if expected:
        with Then(f"result should match the expected", description=expected):
            assert r == expected, error()

    else:
        with Then("I check output against snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        '\n' + r + '\n',
                        'parquet_file',
                        name=name,
                        encoder=str,
                    )
                ), error()


@TestStep(Then)
def check_file(self, path, expected=None):
    node = current().context.node
    name = basename(current().name)

    with By(f"Reading file"):
        r = node.command(f"python3 -c \"import pyarrow.parquet as pq;[print(i.columns) for i in pq.ParquetFile('{path}').iter_batches()];\"").output.strip()

    if expected:
        with Then(f"result should match the expected", description=expected):
            assert r == expected, error()

    else:
        with Then("I check output against snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        '\n' + r + '\n',
                        'parquet_file',
                        name=name,
                        encoder=str,
                    )
                ), error()

    return

@TestStep(Then)
def check_s3_file(self, s3_client, file, expected):
    """Download file from s3 and read it."""

    with By("Downloading the file"):
        s3_client.download_file(self.context.uri, file, file)

    with Then("I check the file"):
        check_file(file=file, expected=expected)


@TestStep(Then)
def check_mysql(self, name, mysql_node, expected):
    """Check MYSQL table."""

    with By("I selecting from table using mysql"):
        msql_out = mysql_node.command(
            f"mysql -D default -u default -e 'SELECT * FROM {name} FORMAT Parquet'"
        ).output
        assert msql_out == expected, error()

