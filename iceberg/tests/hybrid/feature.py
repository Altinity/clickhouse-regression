from testflows.core import *

from helpers.config import users_d


@TestStep(Given)
def force_analyzer_for_hybrid(self):
    """Hybrid requires enable_analyzer=1.

    The iceberg suite defaults to with_analyzer=False, which may inject
    allow_experimental_analyzer=0 into context.default_query_settings. That
    per-query override wins over the users.d profile and breaks ALIAS selects
    (THERE_IS_NO_COLUMN with expression names like multiply(value, 2)).
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
@Name("hybrid")
def feature(self, minio_root_user, minio_root_password):
    """Hybrid table engine suite (Antalya).

    ALIAS coverage runs as its own Feature for independent runtime control.
    Query fuzzing is present but not enabled by default.
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

    force_analyzer_for_hybrid()

    Feature(test=load("iceberg.tests.hybrid.smoke", "feature"))()

    Feature(test=load("iceberg.tests.hybrid.core.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    Feature(test=load("iceberg.tests.hybrid.hybrid_alias.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    # Disabled: https://github.com/Altinity/ClickHouse/issues/1347
    # Feature(test=load("iceberg.tests.hybrid.hybrid_dropped_segment_repro", "feature"))()

    # Query fuzzing (existing Hybrid SQL + upstream-derived) — enable when ready.
    # Feature(test=load("iceberg.tests.hybrid.hybrid_query_fuzzing", "feature"))(
    #     minio_root_user=minio_root_user,
    #     minio_root_password=minio_root_password,
    # )
