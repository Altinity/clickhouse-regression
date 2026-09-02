"""Shared CAS disk/policy config for the ``--cas`` / ``--cas-s3-cache`` harness toggles.

``cas_policy`` (and, when requested, ``default``) keep those names so existing
tests do not need a storage-policy change. ``--cas-s3-cache`` only swaps the
volume's disk to a ``type=cache`` wrapper in front of ``cas_disk``.
"""

CAS_S3_ENDPOINT = "http://minio:9001/cas/data/"
CAS_S3_ACCESS_KEY = "minio"
CAS_S3_SECRET_KEY = "minio123"

CAS_CACHE_DISK = "cas_cache"
CAS_DISK = "cas_disk"
CAS_POLICY = "cas_policy"
CAS_CACHE_PATH = "/var/lib/clickhouse/cas_cache/"
CAS_CACHE_MAX_SIZE = "10Gi"

CAS_S3_CACHE_FLAG_HELP = (
    "like --cas, but layer a type=cache disk in front of the CAS disk "
    "(production-shaped S3 cache; cas_policy name is unchanged)"
)


def add_cas_arguments(parser, *, cas_help, s3_cache_help=None):
    """Add ``--cas`` and ``--cas-s3-cache`` to a suite argparser."""
    parser.add_argument(
        "--cas",
        action="store_true",
        default=False,
        dest="use_cas",
        help=cas_help,
    )
    parser.add_argument(
        "--cas-s3-cache",
        action="store_true",
        default=False,
        dest="use_cas_s3_cache",
        help=s3_cache_help or CAS_S3_CACHE_FLAG_HELP,
    )


def apply_cas_context(test, *, s3_cache=False):
    """Mark this run as CAS (and optionally cache-in-front) on test context."""
    test.context.use_cas_storage = True
    test.context.use_cas_s3_cache = bool(s3_cache)
    test.context.cas_disk_name = CAS_CACHE_DISK if s3_cache else CAS_DISK
    test.context.default_storage_policy = CAS_POLICY


def cas_storage_config(
    server_root_id,
    *,
    with_s3_cache=False,
    override_default_policy=True,
    endpoint=CAS_S3_ENDPOINT,
    access_key_id=CAS_S3_ACCESS_KEY,
    secret_access_key=CAS_S3_SECRET_KEY,
    gc_interval_sec=None,
):
    """XML that defines ``cas_disk`` and ``cas_policy``.

    When ``with_s3_cache`` is set, also defines ``cas_cache`` wrapping
    ``cas_disk`` and points ``cas_policy`` (and ``default``, if requested) at
    the cache disk. ``gc_interval_sec`` is omitted unless a suite sets it;
    the server default is 60.
    """
    policy_disk = CAS_CACHE_DISK if with_s3_cache else CAS_DISK
    gc_interval_xml = (
        f"\n                <gc_interval_sec>{gc_interval_sec}</gc_interval_sec>"
        if gc_interval_sec is not None
        else ""
    )

    disks = [
        f"""            <{CAS_DISK}>
                <type>object_storage</type>
                <object_storage_type>s3</object_storage_type>
                <metadata_type>cas</metadata_type>
                <server_root_id>{server_root_id}</server_root_id>
                <endpoint>{endpoint}</endpoint>
                <access_key_id>{access_key_id}</access_key_id>
                <secret_access_key>{secret_access_key}</secret_access_key>{gc_interval_xml}
            </{CAS_DISK}>"""
    ]
    if with_s3_cache:
        disks.append(
            f"""            <{CAS_CACHE_DISK}>
                <type>cache</type>
                <disk>{CAS_DISK}</disk>
                <path>{CAS_CACHE_PATH}</path>
                <max_size>{CAS_CACHE_MAX_SIZE}</max_size>
            </{CAS_CACHE_DISK}>"""
        )

    policies = [
        f"""            <{CAS_POLICY}>
                <volumes>
                    <main>
                        <disk>{policy_disk}</disk>
                    </main>
                </volumes>
            </{CAS_POLICY}>"""
    ]
    if override_default_policy:
        policies.append(
            f"""            <default>
                <volumes>
                    <default>
                        <disk>{policy_disk}</disk>
                    </default>
                </volumes>
            </default>"""
        )

    disks_xml = "\n".join(disks)
    policies_xml = "\n".join(policies)
    return f"""\
<clickhouse>
    <storage_configuration>
        <disks>
{disks_xml}
        </disks>
        <policies>
{policies_xml}
        </policies>
    </storage_configuration>
</clickhouse>
"""
