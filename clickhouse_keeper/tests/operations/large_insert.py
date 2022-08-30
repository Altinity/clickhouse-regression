import tempfile
from testflows.stash import stashed
from testflows.core.name import basename
from clickhouse_keeper.tests.steps import *


@TestStep(When)
def large_create_and_insert(
    self,
    table_name="test",
    node_name="clickhouse2",
    partitions_num=2,
    inserts_num=1000,
    random_string_length=1000,
):
    with Given("I create random string data"):
        hash1 = hash(partitions_num)
        hash2 = hash(inserts_num)
        hash3 = hash(random_string_length)
        with stashed(
            basename(self.name)
            + " random_string_of_data"
            + f"{hash1}{hash2}{hash3}"
            + node_name
        ) as stash:
            with By("creating random string data"):
                random_data = get_random_string(
                    length=partitions_num * inserts_num * random_string_length
                )
            stash(random_data)
        random_data = stash.value

    with And(f"I make hard insert ClickHouse {node_name} node"):
        multiple_values = []
        for j in range(1, inserts_num + 1):
            values = (
                "("
                + "), (".join(
                    [
                        str(i)
                        + f",'{random_data[((i - 1) * inserts_num + (j - 1)) * random_string_length: ((i - 1) * inserts_num + j) * random_string_length]}'"
                        for i in range(1, partitions_num + 1)
                    ]
                )
                + ") "
            )
            multiple_values.append(values)
        multiple_insert_into_table(
            node=self.context.cluster.node(node_name),
            table_name=table_name,
            values=multiple_values,
        )
        metric(name="map insert time", value=current_time(), units="sec")


@TestStep(When)
def multiple_insert_into_table(self, table_name, values, node=None):
    """Insert multiple data into a table."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")
    query = "; ".join([f"INSERT INTO {table_name} VALUES {data}" for data in values])
    return node.query(query)


@TestStep
def get_random_string(self, length, cluster=None, steps=True, *args, **kwargs):
    cluster = self.context.cluster if cluster is None else cluster
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as fd:
        cluster.command(
            None,
            f"cat /dev/urandom | tr -dc 'A-Za-z0-9#$&()*+,-./:;<=>?@[\]^_~' | head -c {length} > {fd.name}",
            steps=steps,
            *args,
            **kwargs,
        )
        fd.seek(0)
        return fd.read()


@TestStep
def multi_nodes_insert(
    self,
    nodes_list=["clickhouse1", "clickhouse4"],
    partitions_num=2,
    inserts_num=5,
    random_string_length=3,
    cluster_name="'Cluster_3shards_with_3replicas'",
):
    """Parallel insert from different nodes into table

    :param nodes_list: list of insert nodes names
    :param partitions_num: number of partitions
    :param inserts_num: number of inserts
    :param random_string_length: number of insert chars
    """
    with When("Receive UID"):
        uid = getuid()

    try:
        with And("I create simple table"):
            table_name = f"test{uid}"
            create_simple_table(
                table_name=table_name,
                values="Id Int32, Values String",
                cluster_name=cluster_name,
            )

    finally:
        with And("I make multiple insert"):
            for name in nodes_list:
                When(
                    "I insert some big data from first node",
                    test=large_create_and_insert,
                    parallel=True,
                )(
                    table_name=table_name,
                    node_name=name,
                    partitions_num=partitions_num,
                    inserts_num=inserts_num,
                    random_string_length=random_string_length,
                )
