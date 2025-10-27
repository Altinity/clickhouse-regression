from testflows.core import *


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Run Ice tests."""
    self.context.catalog = "rest"
    Feature(
        test=load("ice.tests.ice_export_sanity", "test_basic_datatypes_export"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load(
            "ice.tests.ice_export_sanity",
            "test_comprehensive_datetime_datatypes_export",
        ),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("ice.tests.ice_export_sanity", "test_nullable_datatypes_export"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("ice.tests.ice_export_sanity", "test_enum_datatypes_export"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("ice.tests.big_partitions", "test_enum_datatypes_export"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("ice.tests.big_partitions", "test_tuple_datatypes_export"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
