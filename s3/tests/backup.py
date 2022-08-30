from s3.tests.common import *
from s3.requirements import *


@TestOutline
@Requirements(RQ_SRS_015_S3_Backup_AlterFreeze("1.0"))
def alter_freeze(self, policy_name):
    """Check tables work with ALTER TABLE FREEZE."""
    node = self.context.node
    table_name = f"table_{getuid()}"
    backup_name = f"backup_{getuid()}"

    with Given(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with Then("I freeze the table"):
        node.query(f"ALTER TABLE {table_name} FREEZE WITH NAME '{backup_name}'")

    with Finally("I unfreeze the table"):
        node.query(f"ALTER TABLE {table_name} UNFREEZE WITH NAME '{backup_name}'")


@TestOutline
@Requirements(RQ_SRS_015_S3_Backup_AlterFreeze("1.0"))
def alter_freeze_partition(self, policy_name):
    """Check tables work with ALTER TABLE FREEZE on specific partitions."""
    node = self.context.node
    table_name = f"table_{getuid()}"
    backup_name = f"backup_{getuid()}"

    with Given(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with Then("I freeze the table"):
        node.query(
            f"ALTER TABLE {table_name} FREEZE PARTITION 1 WITH NAME '{backup_name}'"
        )

    with Finally("I unfreeze the table"):
        node.query(
            f"ALTER TABLE {table_name} UNFREEZE PARTITION 1 WITH NAME '{backup_name}'"
        )


@TestOutline
@Requirements(RQ_SRS_015_S3_Backup_AlterDetach("1.0"))
def detach_partition(self, policy_name):
    """Check tables work with ALTER TABLE DETACH PARTITION."""
    node = self.context.node
    table_name = f"table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with Then("I detach the partition"):
        node.query(f"ALTER TABLE {table_name} DETACH PARTITION 1")

    with Finally("I check the data is gone from the table"):
        output = node.query(f"SELECT * FROM {table_name}").output
        assert output == "", error()


@TestOutline
@Requirements(RQ_SRS_015_S3_Backup_AlterAttach("1.0"))
def attach_partition(self, policy_name):
    """Check tables work with ALTER TABLE ATTACH PARTITION."""
    node = self.context.node
    table_name = f"s3.table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with And("I detach the partition"):
        node.query(f"ALTER TABLE {table_name} DETACH PARTITION 1")

    with And("I check the data is gone from the table"):
        output = node.query(f"SELECT * FROM {table_name}").output
        assert output == "", error()

    with And("I restart the node"):
        node.restart_clickhouse()

    with Then("I attach the partition"):
        node.query(f"ALTER TABLE {table_name} ATTACH PARTITION 1")

    with Finally("I check the data is restored"):
        output = node.query(
            f"SELECT * FROM {table_name} ORDER BY id, x FORMAT JSONEachRow"
        ).output
        assert output == '{"id":"1","x":"2"}', error()


@TestOutline
@Requirements(
    RQ_SRS_015_S3_MetadataRestore_NoLocalMetadata("1.0"),
)
def metadata_full_restore(self, policy_name, disk="external"):
    """Check that a full recovery is possible after purging the content of the s3 disk directory."""
    node = self.context.node
    table_name = f"s3.table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with And("I check the data"):
        assert node.query(f"SELECT count(*) FROM {table_name}").output == "1", error()

    with And("I detach the table"):
        node.query(f"DETACH TABLE {table_name}")

    with And("I drop metadata"):
        drop_s3_metadata(disk=disk)

    with Then("I create a restore file"):
        create_restore_file(disk=disk)

    with And("I restart the disk"):
        node.query(f"SYSTEM RESTART DISK {disk}")

    with And("I attach the table"):
        node.query(f"ATTACH TABLE {table_name}")

    with And("I check the data is restored"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                if node.query(f"SELECT count(*) FROM {table_name}").output != "1":
                    fail("data not restored")


@TestOutline
@Requirements(RQ_SRS_015_S3_MetadataRestore_BucketPath("1.0"))
def metadata_restore_another_bucket_path(self, policy_name, disk="external"):
    """Check that a recovery is possible using metadata on different nodes using different source buckets and paths."""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")
    node3 = self.context.cluster.node("clickhouse3")

    table_name = f"s3.table_{getuid()}"

    try:
        with Given("I have different storage.xml on another nodes"):
            node2.command(
                f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node2.restart_clickhouse()
            node3.command(
                f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node3.restart_clickhouse()

        with And(f"I have a table {table_name}"):
            s3_table(table_name=table_name, policy=policy_name)

        with When("I insert some data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

        with And("I check the data"):
            assert (
                node.query(f"SELECT count(*) FROM {table_name}").output == "1"
            ), error()

        with Then("I create a restore file on clickhouse2"):
            create_restore_file(node=node2, bucket=self.context.bucket, disk=disk)

        with And("I restart the disk"):
            node2.query(f"SYSTEM RESTART DISK {disk}")

        with And("I attach the table on a different node than where it was created"):
            attach_table(table_name=table_name, policy=policy_name, node=node2)

        with And("I check that the data on the table is correct"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    expected = ("1",)
                    if policy_name == "local_and_s3_disk":
                        expected = ("0", "1")
                    assert (
                        node2.query(f"SELECT count(*) FROM {table_name}").output
                        in expected
                    ), error()

        with And("I create a restore file on clickhouse3"):
            create_restore_file(
                node=node3, bucket=self.context.bucket2, path="data", disk=disk
            )

        with And("I restart the disk"):
            node3.query(f"SYSTEM RESTART DISK {disk}")

        with And("I attach the table on clickhouse3"):
            attach_table(table_name=table_name, policy=policy_name, node=node3)

        with And("I check that the data on the table is correct"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    expected = ("1",)
                    if policy_name == "local_and_s3_disk":
                        expected = ("0", "1")
                    assert (
                        node3.query(f"SELECT count(*) FROM {table_name}").output
                        in expected
                    ), error()

    finally:
        with Finally("I change the storage.xml back", flags=TE):
            node2.command(
                f"sed -i -e 's/{self.context.bucket2}\//{self.context.bucket}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node2.restart_clickhouse()
            node3.command(
                f"sed -i -e 's/{self.context.bucket2}\//{self.context.bucket}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node3.restart_clickhouse()


@TestOutline
@Requirements(RQ_SRS_015_S3_MetadataRestore_RevisionRestore("1.0"))
def metadata_restore_different_revisions(self, policy_name, disk="external"):
    """Check that a recovery is possible using metadata of different revision versions."""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")

    table_name = f"table_{getuid()}"

    with Given("I have different storage.xml on another node"):
        node2.command(
            f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
        )
        node2.restart_clickhouse()

    with And(f"I have a table {table_name}"):
        s3_table(table_name=f"s3.{table_name}", policy=policy_name)

    with And("I change database"):
        node.query("USE s3")

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO s3.{table_name} VALUES (1, 2)")
        node.query(f"INSERT INTO s3.{table_name} VALUES (2, 2)")

    with And("I save the revision counter"):
        revision1 = get_revision_counter(
            table_name=f"s3.{table_name}", backup_number=1, disk=disk
        )

    with And("I insert some more data into the table"):
        node.query(f"INSERT INTO s3.{table_name} VALUES (3, 4)")
        node.query(f"INSERT INTO s3.{table_name} VALUES (4, 4)")

    with And("I save the revision counter again"):
        revision2 = get_revision_counter(
            table_name=f"s3.{table_name}", backup_number=2, disk=disk
        )

    with And("I insert some more data into the table"):
        node.query(f"INSERT INTO s3.{table_name} VALUES (5, 6)")
        node.query(f"INSERT INTO s3.{table_name} VALUES (6, 6)")

    with And("I make sure the parts are merged"):
        node.query(f"OPTIMIZE TABLE s3.{table_name}")

    with And("I save the revision counter for the third time"):
        revision3 = get_revision_counter(
            table_name=f"s3.{table_name}", backup_number=3, disk=disk
        )

    with And("I check the data"):
        assert (
            node.query(f"SELECT count(*) FROM s3.{table_name}").output == "6"
        ), error()
        assert (
            node.query(
                f"SELECT count(*) FROM system.parts WHERE table = '{table_name}'"
            ).output
            == "6"
        ), error()

    with Then("I attempt to restore an old revision to the original bucket and path"):
        create_restore_file(
            node=node, revision=revision1, bucket=self.context.bucket, disk=disk
        )

    with And("I restart the disk"):
        node.query(
            f"SYSTEM RESTART DISK {disk}",
            exitcode=36,
            message="DB::Exception: Restoring to the same bucket and path is allowed if revision is latest (0).",
        )

    with And("I restore revision1"):
        create_restore_file(
            node=node2, revision=revision1, bucket=self.context.bucket, disk=disk
        )

    with And("I restart the disk"):
        node2.query(f"SYSTEM RESTART DISK {disk}")

    with And("I attach the table on a different node than where it was created"):
        attach_table(table_name=f"s3.{table_name}", policy=policy_name, node=node2)
        node2.query("USE s3")

    with And("I check the data"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                expected = ("2",)
                if policy_name == "local_and_s3_disk":
                    expected = ("1", "2")
                if (
                    node2.query(f"SELECT count(*) FROM s3.{table_name}").output
                    not in expected
                    or node2.query(
                        f"SELECT count(*) FROM system.parts WHERE table = '{table_name}'"
                    ).output
                    not in expected
                ):
                    fail("data not restored")

    with When("I restore revision 2"):
        node2.query(f"DETACH TABLE s3.{table_name}")
        create_restore_file(
            node=node2, revision=revision2, bucket=self.context.bucket, disk=disk
        )
        node2.query(f"SYSTEM RESTART DISK {disk}")
        node2.query(f"ATTACH TABLE s3.{table_name}")

    with Then("I check the data"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                expected = ("4",)
                if policy_name == "local_and_s3_disk":
                    expected = ("1", "2")
                if (
                    node2.query(f"SELECT count(*) FROM s3.{table_name}").output
                    not in expected
                    or node2.query(
                        f"SELECT count(*) FROM system.parts WHERE table = '{table_name}'"
                    ).output
                    not in expected
                ):
                    fail("data not restored")

    with When("I restore revision 3"):
        node2.query(f"DETACH TABLE s3.{table_name}")
        create_restore_file(
            node=node2, revision=revision3, bucket=self.context.bucket, disk=disk
        )
        node2.query(f"SYSTEM RESTART DISK {disk}")
        node2.query(f"ATTACH TABLE s3.{table_name}")

    with Then("I check the data"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                expected = ("6",)
                if policy_name == "local_and_s3_disk":
                    expected = ("3", "6")
                assert (
                    node2.query(f"SELECT count(*) FROM s3.{table_name}").output
                    in expected
                ), error()
                assert (
                    node2.query(
                        f"SELECT count(*) FROM system.parts WHERE table = '{table_name}'"
                    ).output
                    in expected
                ), error()


@TestOutline
@Requirements(RQ_SRS_015_S3_MetadataRestore_Mutations("1.0"))
def metadata_mutations(self, policy_name, disk="external"):
    """Check that a recovery is possible using metadata before, during and after mutations."""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")

    table_name = f"s3.table_{getuid()}"

    with Given("I have different storage.xml on another node"):
        node2.command(
            f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
        )
        node2.restart_clickhouse()

    with And(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with And("I save the revision counter"):
        revision_before_mutation = get_revision_counter(
            table_name=table_name, backup_number=1, disk=disk
        )

    with And("I generate a mutation"):
        node.query(
            f"ALTER TABLE {table_name} UPDATE x = 1 WHERE 1",
            settings=[("mutations_sync", 2)],
        )

    with And("I save the revision counter after mutation"):
        revision_after_mutation = get_revision_counter(
            table_name=table_name, backup_number=2, disk=disk
        )

    with Then("I restore revision before mutation"):
        create_restore_file(
            node=node2,
            revision=revision_before_mutation,
            bucket=self.context.bucket,
            disk=disk,
        )

    with And("I restart the disk"):
        node2.query(f"SYSTEM RESTART DISK {disk}")

    with And("I attach the table on a different node than where it was created"):
        attach_table(table_name=table_name, policy=policy_name, node=node2)

    with And("I check the data"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                expected = ("2",)
                if policy_name == "local_and_s3_disk":
                    expected = "2"
                assert (
                    node2.query(f"SELECT sum(x) FROM {table_name}").output in expected
                ), error()

    with And("I restore revision after mutation"):
        node2.query(f"DETACH TABLE {table_name}")
        create_restore_file(
            node=node2,
            revision=revision_after_mutation,
            bucket=self.context.bucket,
            disk=disk,
        )
        node2.query(f"SYSTEM RESTART DISK {disk}")
        node2.query(f"ATTACH TABLE {table_name}")

    with And("I check the data"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                expected = ("1",)
                if policy_name == "local_and_s3_disk":
                    expected = ("1", "2")
                assert (
                    node2.query(f"SELECT sum(x) FROM {table_name}").output in expected
                ), error()

    with And("I restore revision during mutation"):
        node2.query(f"DETACH TABLE {table_name}")
        create_restore_file(
            node=node2,
            revision=(revision_after_mutation + revision_before_mutation) // 2,
            bucket=self.context.bucket,
            disk=disk,
        )
        node2.query(f"SYSTEM RESTART DISK {disk}")
        node2.query(f"ATTACH TABLE {table_name}")

    with And("I wait for the mutation to finish"):
        time.sleep(3)

    with And("I check the data"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                expected = ("1",)
                if policy_name == "local_and_s3_disk":
                    expected = ("1", "2")
                assert (
                    node2.query(f"SELECT sum(x) FROM {table_name}").output in expected
                ), error()


@TestOutline
@Requirements(RQ_SRS_015_S3_MetadataRestore_Detached("1.0"))
def metadata_detached(self, policy_name, disk="external"):
    """Check that a recovery is possible using metadata on a detached partition."""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")
    table_name = f"s3.table_{getuid()}"

    with Given("I have different storage.xml on another node"):
        node2.command(
            f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
        )
        node2.restart_clickhouse()

    with And(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")
        node.query(f"INSERT INTO {table_name} VALUES (2, 3)")
        node.query(f"INSERT INTO {table_name} VALUES (3, 4)")

    with And("I generate a mutation"):
        node.query(
            f"ALTER TABLE {table_name} UPDATE x = 1 WHERE 1",
            settings=[("mutations_sync", 2)],
        )

    with And("I detach a partition"):
        node.query(f"ALTER TABLE {table_name} DETACH PARTITION '1'")

    with And("I save the revision counter"):
        revision = get_revision_counter(
            table_name=table_name, backup_number=1, disk=disk
        )

    with Then("I restore revision before mutation"):
        create_restore_file(
            node=node2,
            revision=revision,
            bucket=self.context.bucket,
            path="data",
            detached=True,
            disk=disk,
        )

    with And("I restart the disk"):
        node2.query(f"SYSTEM RESTART DISK {disk}")

    with And(f"I recreate the table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name, node=node2)

    with And("I attach some partitions to it"):
        node2.query(f"ALTER TABLE {table_name} ATTACH PARTITION '2'")
        node2.query(f"ALTER TABLE {table_name} ATTACH PARTITION '3'")

    with And("I check the data"):
        expected = "2"
        if policy_name == "local_and_s3_disk":
            expected = "1"
        assert (
            node2.query(f"SELECT count(*) FROM {table_name}").output == expected
        ), error()

    with And("I attach the partition that was detached before the backup"):
        node2.query(f"ALTER TABLE {table_name} ATTACH PARTITION '1'")

    with And("I check the data"):
        expected = "3"
        if policy_name == "local_and_s3_disk":
            expected = "1"
        assert (
            node2.query(f"SELECT count(*) FROM {table_name}").output == expected
        ), error()


@TestOutline
@Requirements(RQ_SRS_015_S3_Metadata("1.0"))
def metadata_non_restorable_schema(self, policy_name, disk="external"):
    """Fail to restore using metadata when send_metadata is set to false."""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")
    table_name = f"s3.table_{getuid()}"

    try:
        with Given("I have different storage.xml on another node"):
            node.command(
                "sed -i -e 's/<send_metadata>true<\/send_metadata>/<send_metadata>false<\/send_metadata>/' /etc/clickhouse-server/config.d/storage.xml"
            )
            node.restart_clickhouse()

        with And(f"I have a table {table_name}"):
            s3_table(table_name=table_name, policy=policy_name)

        with When("I insert some data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

        with And("I detach the table"):
            node.query(f"DETACH TABLE {table_name}")

        with And("I drop metadata"):
            drop_s3_metadata(disk=disk)

        with And("I create a restore file"):
            create_restore_file(node=node, disk=disk)

        with Then("I try to restart the disk"):
            node.query(f"SYSTEM RESTART DISK {disk}")

        with And("I attach the table on a different node than where it was created"):
            attach_table(table_name=table_name, policy=policy_name, node=node2)

        with And("I check the data"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    assert (
                        node2.query(f"SELECT count(*) FROM {table_name}").output == "0"
                    ), error()

    finally:
        with Finally("I change the storage configs back"):
            node.command(
                "sed -i -e 's/<send_metadata>false<\/send_metadata>/<send_metadata>true<\/send_metadata>/' /etc/clickhouse-server/config.d/storage.xml"
            )
            node.restart_clickhouse()


@TestOutline
@Requirements(RQ_SRS_0_5_S3_MetadataRestore_BadRestoreFile("1.0"))
def metadata_garbage_restore_file(self, policy_name, disk="external"):
    """Bad restore file(s)"""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")
    table_name = f"s3.table_{getuid()}"

    try:
        with Given("I have different storage.xml on another node"):
            node2.command(
                f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node2.restart_clickhouse()

        with And(f"I have a table {table_name}"):
            s3_table(table_name=table_name, policy=policy_name)

        with When("I insert some data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

        with And("I save the revision counter"):
            revision = get_revision_counter(
                table_name=table_name, backup_number=1, disk=disk
            )

        with And("I insert some more data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (2, 4)")

        with And("I create a restore file with a bucket that doesn't exist"):
            create_restore_file(disk=disk, node=node2, bucket="aaa")

        with Then("I try to restart the disk"):
            node2.query(
                f"SYSTEM RESTART DISK {disk}",
                exitcode=243,
                message="DB::Exception: 132: The specified bucket does not exist.",
            )

        with When("I create a restore file with no bucket and a path"):
            node2.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/restore")
            create_restore_file(disk=disk, node=node2, path="aaa")

        with Then("I try to restart the disk"):
            node2.query(
                f"SYSTEM RESTART DISK {disk}",
                exitcode=36,
                message="DB::Exception: Source bucket doesn't have restorable schema..",
            )

        with When(
            "I create a restore file with no path, and a negative revision version"
        ):
            node2.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/restore")
            create_restore_file(
                disk=disk, node=node2, bucket=self.context.bucket, revision=-1
            )

        with Then("I try to restart the disk"):
            node2.query(
                f"SYSTEM RESTART DISK {disk}",
                exitcode=72,
                message="DB::Exception: Unsigned type must not contain '-' symbol.",
            )

        with When("I create a restore file with no path, and a revision version"):
            node2.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/restore")
            create_restore_file(
                disk=disk,
                node=node2,
                bucket=self.context.bucket,
                revision=revision + 99999999,
            )

        with Then("I try to restart the disk"):
            node2.query(f"SYSTEM RESTART DISK {disk}")

        with And("I attach the table on a different node than where it was created"):
            attach_table(table_name=table_name, policy=policy_name, node=node2)

        with And("I check the data"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    expected = "2"
                    if policy_name == "local_and_s3_disk":
                        expected = "1"
                    assert (
                        node2.query(f"SELECT count(*) FROM {table_name}").output
                        == expected
                    ), error()

    finally:
        with Finally("I change the storage configs back"):
            node.command(
                f"sed -i -e 's/{self.context.bucket2}\//{self.context.bucket}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node.restart_clickhouse()


@TestOutline
@Requirements(
    RQ_SRS_0_5_S3_MetadataRestore_HugeRestoreFile("1.0"),
)
def metadata_huge_restore_file(self, policy_name, disk="external"):
    """/dev/urandom > restore file"""
    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")
    table_name = f"s3.table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with And("I create a restore file by adding a megabyte from /dev/urandom"):
        node.command(f"mkdir -p /var/lib/clickhouse/disks/{disk}/")
        node.command(f"touch /var/lib/clickhouse/disks/{disk}/restore")
        node.command(f"echo 'a=' > /var/lib/clickhouse/disks/{disk}/restore")
        node.command(
            f"cat /dev/urandom | tr -dc 'A-Za-z0-9#$&()*+,-./:;<=>?@[]^_~' | head -c 1000000 /dev/urandom > /var/lib/clickhouse/disks/{disk}/restore"
        )

    with Then("I try to restart the disk"):
        r = node.query(f"SYSTEM RESTART DISK {disk}", no_checks=1)
        assert r.exitcode in (27, 73), error(r.output)
        assert "DB::Exception:" in r.output, error(r.output)


@TestOutline
def metadata_change_configs(self, policy_name, disk="external"):
    """Change the storage.xml file before running tests."""

    node = self.context.node

    table_name = f"s3.table_{getuid()}"

    try:
        with Given("I have a different config on clickhouse1"):
            node.command(
                f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node.restart_clickhouse()

        with And(f"I have a table {table_name}"):
            s3_table(table_name=table_name, policy=policy_name)

        with When("I insert some data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (1, 2)")
            node.query(f"INSERT INTO {table_name} VALUES (2, 2)")
            node.query(f"INSERT INTO {table_name} VALUES (3, 2)")

        with And("I save the revision counter"):
            revision_before_mutation = get_revision_counter(
                table_name=table_name, backup_number=1, disk=disk
            )

        with And("I generate a mutation"):
            node.query(
                f"ALTER TABLE {table_name} UPDATE x = 1 WHERE 1",
                settings=[("mutations_sync", 2)],
            )

        with And("I detach the table"):
            node.query(f"DETACH TABLE {table_name}")

        with And("I drop metadata"):
            drop_s3_metadata(disk=disk)

        with Then("I restore revision before mutation"):
            create_restore_file(
                node=node,
                revision=revision_before_mutation,
                bucket=self.context.bucket2,
                disk=disk,
            )

        with And("I restart the disk"):
            node.query(
                f"SYSTEM RESTART DISK {disk}",
                exitcode=36,
                message="DB::Exception: Restoring to the same bucket and path is allowed if revision is latest",
            )

        with And("I attach the table on a different node than where it was created"):
            attach_table(table_name=table_name, policy=policy_name, node=node)

        with And("I check the data"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    assert (
                        int(
                            node.query(
                                f"SELECT count(*) FROM {table_name}"
                            ).output.strip()
                        )
                        < 3
                    ), error()

        node.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/restore")

    finally:
        with Finally("I change the storage.xml back"):
            node.command(
                f"sed -i -e 's/{self.context.bucket2}\//{self.context.bucket}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node.restart_clickhouse()


@TestOutline
def metadata_restore_two_tables(self, policy_name, disk="external"):
    """Restoring a table with a mutation and then restoring a regular table."""

    node = self.context.node
    node2 = self.context.cluster.node("clickhouse2")

    table_name = f"s3.table_{getuid()}"

    try:
        with Given("I have a different config on clickhouse2"):
            node2.command(
                f"sed -i -e 's/{self.context.bucket}\//{self.context.bucket2}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node2.restart_clickhouse()

        with Given(f"I have a table {table_name}"):
            s3_table(table_name=table_name, policy=policy_name)

        with When("I insert some data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

        with And("I save the revision counter"):
            revision_before_mutation = get_revision_counter(
                table_name=table_name, backup_number=1, disk=disk
            )

        with And("I generate a mutation"):
            node.query(
                f"ALTER TABLE {table_name} UPDATE x = 1 WHERE 1",
                settings=[("mutations_sync", 2)],
            )

        with Then("I restore revision before mutation"):
            create_restore_file(
                node=node2,
                revision=revision_before_mutation,
                bucket=self.context.bucket,
                disk=disk,
            )

        with And("I restart the disk"):
            node2.query(f"SYSTEM RESTART DISK {disk}")

        with And("I attach the table on a different node than where it was created"):
            attach_table(table_name=table_name, policy=policy_name, node=node2)

        with And("I check the data"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    if node2.query(f"SELECT sum(x) FROM {table_name}").output != "2":
                        fail("data has not been restored yet")

        node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
        node2.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

        table_name = f"s3.table_{getuid()}"

        cleanup(storage=self.context.storage)

        with Given(f"I have a table {table_name}"):
            s3_table(table_name=table_name, policy=policy_name)

        with When("I insert some data into the table"):
            node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

        with And("I check the data"):
            assert (
                node.query(f"SELECT count(*) FROM {table_name}").output == "1"
            ), error()

        with And("I detach the table"):
            node.query(f"DETACH TABLE {table_name}")

        with And("I drop metadata"):
            drop_s3_metadata(disk=disk)

        with Then("I create a restore file on clickhouse"):
            create_restore_file(node=node, disk=disk)

        with And("I restart the disk"):
            node.query(f"SYSTEM RESTART DISK {disk}")

        with And("I attach the table"):
            attach_table(table_name=table_name, policy=policy_name, node=node)

        with And("I check that the data on the table is correct"):
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    if node.query(f"SELECT count(*) FROM {table_name}").output != "1":
                        fail("data has not been restored yet")

    finally:
        with Finally("I change the storage.xml back"):
            node2.command(
                f"sed -i -e 's/{self.context.bucket2}\//{self.context.bucket}\//' /etc/clickhouse-server/config.d/storage.xml"
            )
            node2.restart_clickhouse()


@TestScenario
@Requirements(RQ_SRS_015_S3_Backup_StoragePolicies("1.0"))
def local_and_s3_disk(self):
    """Test back up using s3 and local disk combination."""
    node = current().context.node
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
                "send_metadata": "true",
                "list_object_keys_size": "1",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "local_and_s3_disk": {
                "volumes": [
                    {
                        "default_and_external": [
                            {"disk": "default"},
                            {"disk": "external"},
                        ]
                    }
                ]
            },
        }

    with s3_storage(disks, policies, restart=True):
        for outline in loads(current_module(), Outline):

            with Given("I run the clean up"):
                cleanup(storage=self.context.storage)

            Scenario(test=outline)(policy_name="local_and_s3_disk")


@TestScenario
@Requirements(RQ_SRS_015_S3_Backup_StoragePolicies("1.0"))
def local_and_s3_volumes(self):
    """Test backup with a storage policy that has both local and s3 volume."""
    node = current().context.node
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
                "send_metadata": "true",
                "list_object_keys_size": "1",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default_and_external": {
                "volumes": {
                    "external": {"disk": "external"},
                    "default": {"disk": "default"},
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        for outline in loads(current_module(), Outline):

            with Given("I run the clean up"):
                cleanup(storage=self.context.storage)

            Scenario(test=outline)(policy_name="default_and_external")


@TestScenario
@Requirements(RQ_SRS_015_S3_Backup_StoragePolicies("1.0"))
def s3_disk(self):
    """Test backup with s3 disk."""
    node = current().context.node
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        disks = {
            "external": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
                "send_metadata": "true",
                "list_object_keys_size": "1",
            }
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {"external": {"volumes": {"external": {"disk": "external"}}}}

    with s3_storage(disks, policies, restart=True):
        for outline in loads(current_module(), Outline):

            with Given("I run the clean up"):
                cleanup(storage=self.context.storage)

            Scenario(test=outline)(policy_name="external")


@TestFeature
@Requirements(RQ_SRS_015_S3_Backup_AWSS3Backup("1.0"))
@Name("aws s3 backup")
def aws_s3(self, uri, access_key, key_id, bucket, region, node="clickhouse1"):
    """Test manual backup and metadata back up with aws s3 storage."""
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket = bucket
    self.context.bucket2 = bucket + "2"
    self.context.region = region

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)


@TestFeature
@Requirements(RQ_SRS_015_S3_Backup_GCSBackup("1.0"))
@Name("gcs backup")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    """Test manual backup and metadata back up with gcs storage."""
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.bucket = "data"
    self.context.bucket2 = "data2"
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)


@TestFeature
@Requirements(RQ_SRS_015_S3_Backup_MinIOBackup("1.0"))
@Name("minio backup")
def minio(self, uri, key, secret, node="clickhouse1"):
    """Test manual backup and metadata back up with minio storage."""
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret
    self.context.bucket = self.context.cluster.minio_bucket
    self.context.bucket2 = self.context.cluster.minio_bucket_2

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
