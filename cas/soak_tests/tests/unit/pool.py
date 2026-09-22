from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.pool import classify_pool_path, parse_pool_find


@TestScenario
@Name("classify blobs relative and prefixed")
def classify_blobs_relative_and_prefixed(self):
    assert classify_pool_path("blobs/ce/ce6dfecc05b818feadd26bcab4a4b4b7") == "blobs", error()
    assert classify_pool_path("soak_pool/blobs/ce/ce6dfecc05b818feadd26bcab4a4b4b7") == "blobs", error()
    assert classify_pool_path("./blobs/ce/xhash") == "blobs", error()


@TestScenario
@Name("classify manifests under cas tree")
def classify_manifests_under_cas_tree(self):
    key = (
        "cas/manifests/ca_soak_ch2/store/aff/aff823b3-cd6a-4444-9999-000000000001/"
        "3/3653/000001.proto"
    )
    assert classify_pool_path(key) == "_manifests", error()
    assert classify_pool_path("soak_pool/" + key) == "_manifests", error()


@TestScenario
@Name("classify refs under cas tree")
def classify_refs_under_cas_tree(self):
    assert classify_pool_path("cas/refs/ca_soak_ch1/7") == "refs", error()
    assert classify_pool_path("soak_pool/cas/refs/ca_soak_ch1/12") == "refs", error()


@TestScenario
@Name("classify gc not confused with roots")
def classify_gc_not_confused_with_roots(self):
    assert classify_pool_path("soak_pool/gc/server-roots/ca_soak_ch1/mount") == "gc", error()
    assert classify_pool_path("gc/state") == "gc", error()


@TestScenario
@Name("classify roots files pool_meta other")
def classify_roots_files_pool_meta_other(self):
    assert classify_pool_path("roots/ca_soak_ch1/store/uuid@cas@/3") == "roots", error()
    assert classify_pool_path("soak_pool/roots/ca_soak_ch1/_watermark") == "roots", error()
    assert classify_pool_path("roots/ns/store/uuid@cas@/_files/data.bin") == "_files", error()
    assert classify_pool_path("_pool_meta") == "_pool_meta", error()
    assert classify_pool_path("soak_pool/_pool_meta") == "_pool_meta", error()
    assert classify_pool_path("something/unknown") == "other", error()
    assert classify_pool_path("cas/unknown/zzz") == "other", error()


@TestScenario
@Name("parse pool find buckets sizes")
def parse_pool_find_buckets_sizes(self):
    text = "\n".join(
        [
            "100\t./blobs/ab/abcdef",
            "20\t./cas/manifests/ch1/x.proto",
            "5\t./cas/refs/ch1/7",
            "not-a-stat-line",
            "9\t./gc/state",
        ]
    )
    shape = parse_pool_find(text)
    assert shape["_ok"] is True, error()
    assert shape["blobs"] == {"objects": 1, "bytes": 100}, error()
    assert shape["_manifests"] == {"objects": 1, "bytes": 20}, error()
    assert shape["refs"] == {"objects": 1, "bytes": 5}, error()
    assert shape["gc"] == {"objects": 1, "bytes": 9}, error()
    assert shape["_total"] == {"objects": 4, "bytes": 134}, error()


@TestFeature
@Name("pool")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
