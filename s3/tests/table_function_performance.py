import random

from testflows.core import *

from s3.tests.common import *
from s3.requirements import *

many_files_uri = (
    "https://s3.us-west-2.amazonaws.com/altinity-qa-test/data/many_files_benchmark/"
)


@TestStep(Given)
def s3_create_many_files(self):
    """Create a folder with many folders and files in S3"""

    assert self.context.storage == "aws_s3", error(
        "Must be in s3 mode to insert new data"
    )

    num_folders = 50_000
    start_offset = 0
    folder_size_mb = 4
    num_files_per_folder = 5

    node = current().context.node
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    table_name = "table_" + getuid()
    random.seed("many_files")

    @TestStep(When)
    def insert_files(self, folder_id, iteration):
        node.query(
            f"""INSERT INTO TABLE FUNCTION 
            s3('{many_files_uri}id={folder_id}/file_{{_partition_id}}.csv','{access_key_id}','{secret_access_key}','CSV','d UInt64') 
            PARTITION BY (d % {num_files_per_folder}) SELECT * FROM {table_name} 
            -- {iteration}/{num_folders}"""
        )

    with Given("I have a table with data"):
        simple_table(node=node, name=table_name, policy="default")
        insert_data(node=node, number_of_mb=folder_size_mb, name=table_name)

    with Given("I have many folders with files in S3"):
        executor = Pool(50, thread_name_prefix="s3_insert")
        for j in range(num_folders):
            i = random.randint(100_000, 999_999)

            # skip ahead through random number generation
            if j < start_offset:
                continue

            By(test=insert_files, parallel=True, executor=executor)(
                folder_id=i, iteration=j
            )

        join()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path_Wildcard("1.0"))
def wildcard_performance(self):
    """Check the performance of using wildcards in s3 paths."""

    node = current().context.node
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key

    examples = [
        ("522029", "one_file"),
        ("{249278..283359}", "range"),
        ("{759040,547776,167687,283359}", "nums"),
        ("{759040,547776,167687,283359,abc}", "nums_one_missing"),
        # ("*", "star"),
        # ("%3F", "question"),
    ]

    for wildcard, name in examples:
        with Example(name):
            with Then(f"""I query the data using the wildcard '{wildcard}'"""):
                t_start = time.time()
                r = node.query(
                    f"""SELECT median(d) FROM s3('{many_files_uri}id={wildcard}/*', '{access_key_id}','{secret_access_key}', 'CSV', 'd UInt64')"""
                )
                metric(f"wildcard {name} ({wildcard})", time.time() - t_start, "s")
                assert r.output.strip() != "", error()


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_TableFunction("1.0"))
def outline(self):
    """Test S3 and S3 compatible storage through storage disks."""

    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("table function performance")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    # with Given("I create many S3 files"):
    #     s3_create_many_files()
    #     return

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("table function performance")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("table function performance")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    outline()
