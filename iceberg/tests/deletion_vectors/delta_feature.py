"""Entry point for the Delta ``.bin`` container pass of SRS-048.

Databricks stores Iceberg v3 deletion vectors in a Delta-style
``deletion_vector_*.bin`` container rather than a Puffin file: one format
version byte followed by the byte-identical ``deletion-vector-v1`` blob, with
the delete manifest still declaring ``file_format = PUFFIN``. ClickHouse
identifies the container from the object's bytes, so almost the entire read
path below that decision is shared with the Puffin case.

This feature therefore **reuses** the existing scenario modules rather than
duplicating them. It sets ``context.dv_container``, which the two crafting
chokepoints in ``steps/common.py`` and ``steps/manifest.py`` read:

* ``table_with_deletion_vectors`` rewrites every writer-produced Puffin as a
  ``.bin`` in place, keeping the blob bytes the writer serialized;
* ``replace_vector_with_positions`` and ``install_delta_bin`` wrap crafted
  payloads in a ``.bin`` instead of a Puffin file.

Both assert afterwards that the objects really are ``.bin`` containers. That
post-condition is the point: a conversion that silently did nothing would leave
a Puffin table behind and this whole feature would pass while proving nothing.

Why a separate feature instead of a container dimension on the existing one:

* Puffin-specific scenarios are **absent** here rather than skipped. TestFlows
  marks a requirement unsatisfied when a linked scenario is Skip, so guarding
  footer scenarios with ``skip()`` in a Delta pass would poison requirement
  coverage that the Puffin run satisfies perfectly (the mechanism behind A2/A3
  in ``docs/COVERAGE_ISSUES.md``).
* ``feature.py`` is untouched, so the Puffin run cannot regress while this
  lands. The container mode defaults to ``puffin`` everywhere.
* The curation is reviewable in one file instead of scattered conditionals.

What is deliberately **not** run, and why: ``datatypes``, ``parquet_variety``,
``reporting``, ``many_data_files``, ``time_travel``, ``partitioning`` and
``query_semantics`` are container-agnostic but vary dimensions orthogonal to
the container, so re-running them buys little for a suite that already takes
hours. That is a coverage trade-off, not an oversight.

Puffin-specific scenarios omitted from the curated modules below — their
subject is the footer, which a ``.bin`` does not have:
``sanity.puffin_metadata_structure``, ``sanity.crafted_writer_conformance``,
``error_handling.blob_metadata``, ``error_handling.compressed_footer``, and the
footer/trailer cases of ``file_corruption.puffin_defect``.
"""

import ast
import pathlib

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import (
    SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support,
)

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.manifest as manifest

MODULE = "iceberg.tests.deletion_vectors.{}"

# modules that are container-agnostic end to end, so their own feature() entry
# point is reused as is. Do not put Delta-only modules here — a later edit
# that copies this list into the Puffin feature would run them twice.
WHOLESALE_MODULES = (
    "access_forms",
    "vector_shapes",
    "coexistence",
    "count_paths",
    "distributed",
)

# Class C: the container seam itself. Only this feature runs them.
DELTA_ONLY_MODULES = ("container_formats",)

# modules mixing container-agnostic and Puffin-specific scenarios, so the
# applicable suites and scenarios are named one by one. Adding a scenario to
# one of these modules does not reach this feature until it is listed here —
# the cost of scenario-level curation, paid deliberately.
CURATED = {
    "sanity": (
        (Scenario, "read_deletion_vectors"),
        (Scenario, "read_only"),
        (Suite, "mutations_rejected"),
        (Suite, "writer_operations"),
    ),
    "error_handling": (
        (Suite, "malformed_blob"),
        (Suite, "blob_bounds"),
        (Suite, "manifest_consistency"),
        (Suite, "resource_limits"),
        (Suite, "non_parquet_data_files"),
    ),
    "file_corruption": (
        (Suite, "corrupt_delete_manifest"),
        (Suite, "corrupt_manifest_list"),
    ),
}

# Puffin-specific entry points of the curated modules, listed so that
# :func:`curation_is_complete` can tell a deliberate omission from a scenario
# somebody added later and nobody classified.
OMITTED = {
    "sanity": {
        "puffin_metadata_structure": "asserts Puffin footer blob structure directly",
        "crafted_writer_conformance": "pins the crafted Puffin writer against Spark",
    },
    "error_handling": {
        "blob_metadata": "every defect in it is a Puffin footer property",
        "compressed_footer": "LZ4 footer payload and footer flag bits",
    },
    "file_corruption": {
        "corrupt_puffin_file": "footer and trailer byte damage; a .bin has neither",
    },
}


def _feature_entry_points(module):
    """Names the module's own ``feature()`` runs, read from its source.

    Parsing beats importing and introspecting here: the entry points are the
    ``run=`` / ``test=`` arguments inside ``feature``, which is exactly the
    list this feature curates against, and no test has to execute to find
    them."""
    path = pathlib.Path(__file__).with_name(f"{module}.py")
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "feature":
            return {
                keyword.value.id
                for call in ast.walk(node)
                if isinstance(call, ast.Call)
                for keyword in call.keywords
                if keyword.arg in ("run", "test")
                and isinstance(keyword.value, ast.Name)
            }
    raise AssertionError(f"{module}.py has no feature() to read entry points from")


@TestScenario
def curation_is_complete(self):
    """Every entry point of a curated module is either run here or listed as
    a deliberate omission.

    Scenario-level curation has one failure mode: a scenario added to
    ``sanity`` or ``error_handling`` later never reaches the Delta run, and
    nothing says so. This turns that silence into a failure, naming the
    scenario and asking for a decision — run it under Delta, or record why
    it is Puffin-specific."""
    for module in CURATED:
        with Check(module):
            defined = _feature_entry_points(module)
            curated = {name for _, name in CURATED[module]}
            omitted = set(OMITTED.get(module, {}))

            unclassified = defined - curated - omitted
            assert not unclassified, error(
                f"{module}.py runs {sorted(unclassified)} but this feature "
                f"neither reuses them nor records them in OMITTED — decide "
                f"whether they apply to a Delta container"
            )

            stale = (curated | omitted) - defined
            assert not stale, error(
                f"{sorted(stale)} are listed for {module} but its feature() no "
                f"longer runs them — the curation is out of date"
            )


@TestFeature
@Specifications(SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support)
@Name("delta deletion vectors")
def feature(self, minio_root_user, minio_root_password):
    """Run the deletion-vector scenarios that apply to a Delta ``.bin``
    container, with every vector stored in one."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password
    self.context.spark_created_tables = []
    self.context.dv_container = manifest.DELTA_BIN_CONTAINER

    with Given("the Spark writer container is ready"):
        spark.wait_for_spark()

    try:
        # first, and deliberately: if the curation has drifted, the run that
        # follows is measuring something other than what this file claims
        Scenario(run=curation_is_complete)

        for module in WHOLESALE_MODULES + DELTA_ONLY_MODULES:
            Feature(test=load(MODULE.format(module), "feature"))(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )

        for module, entries in CURATED.items():
            with Feature(module.replace("_", " ")):
                for test_type, name in entries:
                    # suites and scenarios take no arguments, unlike a module
                    # feature(); they read the credentials off the feature
                    # context set above. The type has to match the loaded
                    # definition's own decorator.
                    test_type(test=load(MODULE.format(module), name))()
    finally:
        with Finally("clean up all Spark-created tables"):
            common.cleanup_created_tables()
