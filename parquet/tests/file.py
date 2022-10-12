from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *

@TestSuite
@Requirements()
def engine(self, node=None):
    """Check that ClickHouse reads Parquet format correctly from tables using the File engine."""

    if node is None:
        node = self.context.node

    with Scenario("Write Parquet into File engine"):
        table_name = "table_" + getuid()

        with Given("I have a table."):
            table(name=table_name, engine='File(Parquet)')

        with When("I insert some data."):
            insert_const(name=table_name)

        with Then("I check the file in the table engine."):
            check_file(path=f'/var/lib/clickhouse/data/default/{table_name}/data.Parquet')

    with Scenario("Read Parquet from File engine"):
        table_name = "table_" + getuid()

        with Given("I attach a table."):
            table(name=table_name, engine='File(Parquet)', create="ATTACH")

        with Then("I check the data from the table engine"):
            check_query(query=f"SELECT * FROM {table_name}")

@TestSuite
@Requirements()
def function(self, node=None):
    """Check that ClickHouse reads Parquet format correctly using the File table function."""

    if node is None:
        node = self.context.node

    table_name = "table_" + getuid()
    file_name = "file_" + getuid()

    with Scenario("Write Parquet into File function."):

        with Given("I have a table."):
            table(name=table_name, engine='File(Parquet)')

        with When("I insert some data."):
            insert_const(name=f"""
                FUNCTION file('{file_name}.Parquet', 'Parquet', 
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
                """)

        with Then("I check the file in the table function."):
            check_file(path=f'/var/lib/clickhouse/user_files/{file_name}.Parquet')

    with Scenario("Read Parquet from table function, default type cast"):

        with Then("I check the data from the table function"):
            check_query(query=f"SELECT *, toTypeName(*) FROM file('{file_name}.Parquet', 'Parquet')")

    with Scenario("Read Parquet from table function, manual type cast"):

        with Then("I check the data from the table function"):
            check_query(query=f"""
                SELECT * FROM file('{file_name}.Parquet', 'Parquet',
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
                """)


@TestFeature
@Name("file")
def feature(self, node="clickhouse1"):
    """Run checks for clickhouse using Parquet format."""

    self.context.node = self.context.cluster.node(node)

    Suite(run=engine)
    Suite(run=function)
