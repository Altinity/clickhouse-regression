from testflows.core import *

from helpers.config import config_d, users_d

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_AnalyzerRequired,
)


@TestStep(Given)
def force_analyzer_for_hybrid(self):
    """Force enable_analyzer=1 for the Hybrid suite.

    The iceberg suite defaults to with_analyzer=False, which may inject
    allow_experimental_analyzer=0 into context.default_query_settings. That
    per-query override wins over the users.d profile; Hybrid coverage is
    written and run with enable_analyzer=1 (see RQ.ClickHouse.Hybrid.AnalyzerRequired).
    """
    default_query_settings = getsattr(self.context, "default_query_settings", [])
    for setting in (
        ("allow_experimental_analyzer", 0),
        ("allow_experimental_analyzer", 1),
        ("enable_analyzer", 0),
        ("enable_analyzer", 1),
    ):
        while setting in default_query_settings:
            default_query_settings.remove(setting)
    default_query_settings.append(("enable_analyzer", 1))


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_AnalyzerRequired("1.0"),
)
@Name("hybrid")
def feature(self, minio_root_user, minio_root_password):
    """Hybrid table engine suite (Antalya).

    ALIAS coverage runs as its own Feature for independent runtime control.
    """
    with Given(
        "enable Hybrid, analyzer, and Iceberg insert gates in the default profile"
    ):
        for node in self.context.nodes:
            users_d.create_and_add(
                entries={
                    "profiles": {
                        "default": {
                            "allow_experimental_hybrid_table": "1",
                            "enable_analyzer": "1",
                            "allow_experimental_insert_into_iceberg": "1",
                        }
                    }
                },
                config_file="allow_experimental_hybrid_table.xml",
                node=node,
                modify=True,
            )

    with Given(
        "allow serialized query-plan packets "
        "(required for serialize_query_plan=1 on remotes)"
    ):
        for node in self.context.nodes:
            config_d.create_and_add(
                entries={"process_query_plan_packet": "true"},
                config_file="process_query_plan_packet.xml",
                node=node,
                modify=True,
            )

    force_analyzer_for_hybrid()

    Feature(test=load("iceberg.tests.hybrid.smoke", "feature"))()

    Feature(test=load("iceberg.tests.hybrid.core.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    Feature(test=load("iceberg.tests.hybrid.storage.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    Feature(test=load("iceberg.tests.hybrid.lifecycle.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    Feature(test=load("iceberg.tests.hybrid.fuzzing.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    Feature(test=load("iceberg.tests.hybrid.schema.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    Feature(test=load("iceberg.tests.hybrid.hybrid_alias.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    # Disabled: https://github.com/Altinity/ClickHouse/issues/1347
    # Feature(test=load("iceberg.tests.hybrid.hybrid_dropped_segment_repro", "feature"))()
