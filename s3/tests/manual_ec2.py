from testflows.core import *
from testflows.asserts import error

from s3.tests.common import getuid

from s3.requirements import *


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_EC2_EnvironmentCredentials("1.0"))
def disk(self):
    """Check that S3 storage works correctly on an Amazon EC2 instance when using
    server-level environment credentials by manually setting the necessary
    configuration and then importing from and exporting to a disk configured
    for S3.
    """
    name = "table_" + getuid()

    with Given(
        """I have a server configured with endpoint and credentials set by adding
            the following to the s3.xml file inside the config.d directory""",
        description="""
            <yandex>
                <s3>
                    <my_endpoint>
                    <endpoint>https://my-endpoint-url</endpoint>
                    <access_key_id>ACCESS_KEY_ID</access_key_id>
                    <secret_access_key>SECRET_ACCESS_KEY</secret_access_key>
                    </my_endpoint>
                </s3>
            </yandex>""",
    ):
        note(input("Please enter specific endpoint configuration", multiline=True))
        pass

    with And(
        """I have a server configured to accept incoming connections by adding
            the following line to config.xml inside the <yandex> element""",
        description="<listen_host>0.0.0.0</listen_host>",
    ):
        pass

    with And(
        """I have a storage disk and policy configured to use S3 storage with
            the server-level credentials by adding this storage.xml file
            in the config.d directory""",
        description="""
            <yandex>
            <storage_configuration>
                <disks>
                    <default>
                        <keep_free_space_bytes>1024</keep_free_space_bytes>
                    </default>
                    <aws>
                        <type>s3</type>
                        <use_environment_credentials>1</use_environment_credentials>
                        <endpoint>https://my-endpoint-url</endpoint>
                    </aws>
                </disks>
                <policies>
                    <default>
                        <volumes>
                            <default>
                                <disk>default</disk>
                            </default>
                        </volumes>
                    </default>
                    <aws_external>
                        <volumes>
                            <external>
                                <disk>aws</disk>
                            </external>
                        </volumes>
                    </aws_external>
                </policies>
            </storage_configuration>
            </yandex>""",
    ):
        note(input("Please enter endpoint URL used for aws disk"))
        pass

    with When(
        """I connect to the clickhouse-server on the EC2 instance using the
            server ip address and the default port""",
        description="clickhouse-client --host [my_ec2_ip]",
    ):
        note(input("Please enter specific command used to connect", multiline=True))
        pass

    with And(
        "I create a table using storage policy aws_external",
        description=f"""
            CREATE TABLE {name} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d
            SETTINGS storage_policy='aws_external'""",
    ):
        pass

    with And(
        "I store simple data in the table",
        description=f"""
            INSERT INTO {name} VALUES (427)""",
    ):
        pass

    with Then(
        "I check that a simple SELECT * query returns 427 as expected",
        description=f"""
            SELECT * FROM {name} FORMAT CSV""",
    ):
        pass

    with Finally("I drop the table", description=f"DROP TABLE IF EXISTS {name} SYNC"):
        pass


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_EC2("1.0"))
def table_function(self):
    """Check that S3 storage works correctly on an Amazon EC2 instance by
    manually setting the necessary configuration and then importing from and
    exporting to S3 storage using the s3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()

    with Given(
        """I have a server configured to accept incoming connections by adding
            the following line to config.xml inside the <yandex> element""",
        description="<listen_host>0.0.0.0</listen_host>",
    ):
        pass

    with When(
        """I connect to the clickhouse-server on the EC2 instance using the
            server ip address and the default port""",
        description="clickhouse-client --host my_ec2_ip",
    ):
        note(
            input(
                "Please enter specific command used to connect to the server",
                multiline=True,
            )
        )
        pass

    with And(
        "I create a table",
        description=f"""
            CREATE TABLE {name_table1} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d""",
    ):
        pass

    with And(
        "I create a second table for comparison",
        description=f"""
            CREATE TABLE {name_table2} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d""",
    ):
        pass

    with And(
        "I store simple data in the table",
        description=f"""
            INSERT INTO {name_table1} VALUES (427)""",
    ):
        pass

    with And(
        "I store the data in S3 using a table function",
        description=f"""
            INSERT INTO FUNCTION s3('https://my-endpoint-url/data/', 'ACCESS_KEY_ID', 'SECRET_ACCESS_KEY', 'CSV', 'd UInt64')
            SELECT * FROM {name_table1}""",
    ):
        note(input("Please enter specific command used to export data", multiline=True))
        pass

    with And(
        "I import the data from S3 into the other table",
        description=f"""
            INSERT INTO {name_table2}
            SELECT * FROM s3('https://my-endpoint-url/data/', 'ACCESS_KEY_ID', 'SECRET_ACCESS_KEY', 'CSV', 'd UInt64')""",
    ):
        note(input("Please enter specific command used to import data", multiline=True))
        pass

    with Then(
        "I check that a simple SELECT * query on the second table returns 427 as expected",
        description=f"""
            SELECT * FROM {name_table2} FORMAT CSV""",
    ):
        pass

    with Finally("I overwrite the S3 data with empty data"):
        with By(
            "I drop the first table",
            description=f"DROP TABLE IF EXISTS {name_table1} SYNC",
        ):
            pass

        with And(
            "I create the table again (empty table)",
            description=f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d""",
        ):
            pass

        with And(
            "I insert the empty table into S3 where I want to overwrite data",
            description=f"""
                INSERT INTO FUNCTION s3('https://my-endpoint-url/data/', 'ACCESS_KEY_ID', 'SECRET_ACCESS_KEY', 'CSV', 'd UInt64')
                SELECT * FROM {name_table1}""",
        ):
            note(
                input(
                    "Please enter specific command used to overwrite data",
                    multiline=True,
                )
            )
            pass

    with Finally(
        "I drop the first table", description=f"DROP TABLE IF EXISTS {name_table1} SYNC"
    ):
        pass

    with And(
        "I drop the second table",
        description=f"DROP TABLE IF EXISTS {name_table2} SYNC",
    ):
        pass


@TestFeature
@Name("manual s3 ec2")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE | MANUAL)
