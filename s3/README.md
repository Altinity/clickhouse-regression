# Running S3 tests
The S3 regression runs tests on 3 possible types of storage - minio [default], aws s3, and gcs.

## Minio
Running minio with default root user, root password, and local hosted minio container:
```bash
./regression.py --local
```

Running minio specifying the arguments:
```bash
./regression.py --local --storage "minio" --minio-uri " " --minio-root-user " " --minio-root-password " "
```

## AWS S3
Running aws requires region, bucket, key id, and secret access key:
```bash
./regression.py --local --storage "aws_s3" --aws-s3-bucket "" --aws-s3-region "" --aws-s3-key-id "" --aws-s3-access-key ""
```

## GCS
Running gcs requires uri, key id and secret access key:
```bash
./regression.py --local --storage "gcs" --gcs-uri "" --gcs-key-id "" --gcs-access-key ""
```

# How to S3 Metadata Restore

## config
The storage disk must be configured to send metadata before the restore process.
Example config file:
```xml
<yandex>
    <storage_configuration>
        <disks>
            <external>
                <type>s3</type>
                <endpoint>http://minio1:9001/root/data/</endpoint>
                <access_key_id>minio</access_key_id>
                <secret_access_key>minio123</secret_access_key>
                <send_metadata>true</send_metadata>
            </external>
        </disks>
        <policies>
            <s3>
                <volumes>
                    <main>
                        <disk>s3</disk>
                    </main>
                </volumes>
            </s3>
        </policies>
    </storage_configuration>
</yandex>
```

## Local data
In order to restore a dropped or detached table back to the node where it was originally created, the shadow and disk directory must be dropped.
When restoring to a node where the table doesn't exist yet, this is unnecessary.

```
rm -rf /var/lib/clickhouse/disks/{disk name}/*

rm -rf /var/lib/clickhouse/shadow/*
```

## Restore file
Then the restore file must be created in '/var/lib/clickhouse/disks/{disk name}/restore'.
The restore file takes the following keywords and arguments:
    * Indicate the s3 bucket to restore to using "source_bucket= "
    * Indicate the s3 path to restore to using "source_path= "
    Both must be defined in the config file with <send_metadata>true</send_metadata>

    * If a part or partition of the table has been detached after the last backup of the table, indicate "detached=True"
    * To restore a specific revision, indicate "revision= "
    Only the latest revision can be restored to the original source_bucket and source_path.

## Revision number
The revision number is stored in '/var/lib/clickhouse/disks/{disk name}/shadow/{backup number}/revision.txt',
where the 'backup number' is the number of the backup that is to be restored. Backup number starts at 0 and is incremented every time "ALTER TABLE FREEZE" is executed on that table.

## Attaching the table
The final step is in ClickHouse itself.
Run:
```sql
SYSTEM RESTART DISK {disk name}
```
Then attach the table the same way as the original was created.
