import random

from testflows.core import *

from s3.tests.common import *
from s3.requirements import *


@TestStep(Given)
@Name("setup")
def s3_create_many_files(self):
    """Create a folder with many folders and files in S3."""

    num_folders = 30_000
    start_offset = 0
    folder_size_mb = 0.5 if self.context.storage == "minio" else 4
    num_files_per_folder = 5

    node = current().context.node
    table_name = "table_" + getuid()
    my_random = random.Random("many_files")

    with Given("I have a list of random folder ids"):
        folder_ids = [my_random.randint(100_000, 999_999) for _ in range(num_folders)]

    with Then("I check if the files already exist"):
        with By(f"checking if the last folder exists"):
            r = node.query(
                f"""SELECT _path FROM s3(s3_credentials, url='{self.context.many_files_uri}id={folder_ids[-1]}/*', format='One') FORMAT TabSeparated"""
            )

    if r.output:
        skip("Files already exist")
        return

    @TestStep(When)
    def insert_files(self, folder_id, iteration):
        for attempt in retries(timeout=100, delay=10):
            with attempt:
                node.query(
                    f"""INSERT INTO TABLE FUNCTION 
                    s3(s3_credentials, url='{self.context.many_files_uri}id={folder_id}/file_{{_partition_id}}.csv', format='CSV', structure='d UInt64') 
                    PARTITION BY (d % {num_files_per_folder}) SELECT * FROM {table_name} 
                    -- {iteration}/{num_folders}"""
                )

    with Given("I have a table with data"):
        simple_table(node=node, name=table_name, policy="default")
        insert_data(node=node, number_of_mb=folder_size_mb, name=table_name)

    with Given("I have many folders with files in S3"):
        executor = Pool(100, thread_name_prefix="s3_insert")
        for j, folder_id in enumerate(folder_ids):

            # skip ahead through random number generation
            if j < start_offset:
                continue

            By(test=insert_files, parallel=True, executor=executor)(
                folder_id=folder_id, iteration=j
            )

        join()


@TestOutline(Scenario)
@Examples(
    "wildcard expected_time expect_result",
    [
        ("522029", 20, True, Name("one folder")),
        ("{759040,547776,167687,283359}", 120, True, Name("nums")),
        ("{759040,547776,167687,abc,283359}", 120, True, Name("nums one invalid")),
        ("1500*", 20, True, Name("star")),
        ("2500%3F%3F", 20, True, Name("question encoded")),
        ("3500??", 20, True, Name("question")),
        ("{450000..450099}", 120, True, Name("range")),
        ("{abc,efg,hij}", 120, False, Name("nums no match")),
        ("abc*", 2, False, Name("star no match")),
        ("abc??", 2, False, Name("question no match")),
        ("{100..199}", 120, False, Name("range no match")),
    ],
)
@Requirements(RQ_SRS_015_S3_Performance_Glob("1.0"))
def wildcard(self, wildcard, expected_time, expect_result):
    """Check the performance of using wildcards in s3 paths."""

    node = current().context.node

    for i in range(1, 3):
        with Then(f"""I query S3 using the wildcard '{wildcard}'"""):
            t_start = time.time()
            r = node.query(
                f"""SELECT median(d) FROM s3(s3_credentials, url='{self.context.many_files_uri}id={wildcard}/*', format='CSV', structure='d UInt64') FORMAT TabSeparated""",
                timeout=expected_time,
            )
            t_elapsed = time.time() - t_start
            metric(f"wildcard pattern='{wildcard}', i={i}", t_elapsed, "s")
            is_number = r.output.strip().replace(".", "").isdigit()
            assert is_number == expect_result, error(
                f"Expected a number, got {r.output}"
            )
            assert t_elapsed < expected_time, error()


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_TableFunction_S3("1.0"))
def outline(self, uri):
    """Test S3 and S3 compatible storage through storage disks."""

    self.context.uri = uri
    self.context.many_files_uri = self.context.uri + "many_files_benchmark/"

    with Given("I add S3 credentials configuration"):
        named_s3_credentials(
            access_key_id=self.context.access_key_id,
            secret_access_key=self.context.secret_access_key,
            restart=True,
        )

    with allow_s3_truncate(self.context.node):
        Scenario(run=s3_create_many_files)

        for scenario in loads(current_module(), Scenario):
            scenario()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("table function performance")
def aws_s3(self, uri):

    outline(uri=uri)


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("table function performance")
def gcs(self, uri):

    outline(uri=uri)


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("table function performance")
def minio(self, uri):

    outline(uri=uri)
