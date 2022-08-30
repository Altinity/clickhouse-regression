from testflows.core import *
from testflows.asserts import error

from s3.tests.common import *

from s3.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_015_S3_AWS_EC2_Disk("1.0"),
    RQ_SRS_015_S3_AWS_EC2_EnvironmentCredentials("1.0"),
)
def disk(self, ch_client, uri):
    """Check that S3 storage works correctly on an Amazon EC2 instance when using
    server-level environment credentials by connecting to the remote server with
    correct configuration and then importing from and exporting to a disk configured
    for S3.
    """
    name = "table_" + getuid()

    with When("I create a table using the storage policy"):
        ch_client.send(
            f"""
            CREATE TABLE {name} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d
            SETTINGS storage_policy='aws_external'""",
            delay=0.5,
        )
        ch_client.expect("Ok.")

    with And("I store simple data in the table"):
        ch_client.send(f"INSERT INTO {name} VALUES (427)", delay=0.25)
        ch_client.expect("Ok.")

    with Then("I check that a simple SELECT * query returns matching data"):
        ch_client.send(f"SELECT * FROM {name} FORMAT CSV", delay=0.25)
        ch_client.expect("427")

    with Finally("I drop the table"):
        ch_client.send(f"DROP TABLE IF EXISTS {name} SYNC", delay=0.25)
        ch_client.expect("Ok.")


@TestScenario
@Requirements(RQ_SRS_015_S3_AWS_EC2_TableFunction("1.0"))
def table_function(self, ch_client, uri):
    """Check that S3 storage works correctly on an Amazon EC2 instance by
    connecting to the remote server with correct configuration and then importing
    from and exporting to S3 storage using the s3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()

    with When("I create a table"):
        ch_client.send(
            f"""
            CREATE TABLE {name_table1} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d""",
            delay=0.5,
        )
        ch_client.expect("Ok.")

    with And("I create a second table for comparison"):
        ch_client.send(
            f"""
            CREATE TABLE {name_table2} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d""",
            delay=0.25,
        )
        ch_client.expect("Ok.")

    with And(f"I store simple data in the first table {name_table1}"):
        ch_client.send(f"INSERT INTO {name_table1} VALUES (427)", delay=0.25)
        ch_client.expect("Ok.")

    with And("I export the data to S3 using the table function"):
        ch_client.send(
            f"""
                INSERT INTO FUNCTION
                s3('{uri}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}""",
            delay=0.5,
        )
        ch_client.expect("Ok.")

    with And(f"I import the data from S3 into the second table {name_table2}"):
        ch_client.send(
            f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}', 'CSVWithNames', 'd UInt64')""",
            delay=0.5,
        )
        ch_client.expect("Ok.")

    with Then(
        f"""I check that a simple SELECT * query on the second table
            {name_table2} returns matching data"""
    ):
        ch_client.send(f"SELECT * FROM {name_table2} FORMAT CSV", delay=0.25)
        ch_client.expect("427")

    with Finally("I overwrite the S3 data with empty data"):
        with By(f"I drop the first table {name_table1}"):
            ch_client.send(f"DROP TABLE IF EXISTS {name_table1} SYNC", delay=0.25)
            ch_client.expect("Ok.")

        with And(f"I create the table again {name_table1}"):
            ch_client.send(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d""",
                delay=0.5,
            )
            ch_client.expect("Ok.")

        with And(
            f"""I export the empty table {name_table1} to S3 at the
                location where I want to overwrite data"""
        ):
            ch_client.send(
                f"""
                    INSERT INTO FUNCTION
                    s3('{uri}', 'CSVWithNames', 'd UInt64')
                    SELECT * FROM {name_table1}""",
                delay=0.5,
            )
            ch_client.expect("Ok.")

    with Finally(f"I drop the first table {name_table1}"):
        ch_client.send(f"DROP TABLE IF EXISTS {name_table1} SYNC", delay=0.25)
        ch_client.expect("Ok.")

    with And(f"I drop the second table {name_table2}"):
        ch_client.send(f"DROP TABLE IF EXISTS {name_table2} SYNC", delay=0.25)
        ch_client.expect("Ok.")


@TestFeature
@Name("ec2")
def feature(
    self,
    uri="https://s3.us-west-2.amazonaws.com/altinity-qa-test/data",
    host="i-0190112ed3c6dddeb",
    username="ssm-user",
    password="testec2",
    options=["-i ~/.ssh/id_rsa"],
):
    """Test ClickHouse access to S3 environment credentials when running on EC2."""
    ch_client = None
    terminal = None
    self.context.node = self.context.cluster.node("aws")

    with Given(
        """I create an SSH connection to the EC2 instance for the
               ClickHouse client"""
    ):
        ch_client = ssh_terminal(
            host=host, username=username, options=options, rsa_password=password
        )

    with And("I connect to the ClickHouse client on the EC2 instance"):
        ch_client.send(f"clickhouse-client --password {password}", delay=0.25)
        ch_client.expect("ClickHouse client version 20.13.1.5356")

    with And("I create another SSH connection to the EC2 instance for bash"):
        terminal = ssh_terminal(
            host=host, username=username, options=options, rsa_password=password
        )
        self.context.terminal = terminal

    for scenario in loads(current_module(), Scenario):
        Scenario(test=scenario, setup=instrument_clickhouse_server_log)(
            ch_client=ch_client, uri=uri
        )
