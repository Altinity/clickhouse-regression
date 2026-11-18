import importlib.util
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "selector", Path(__file__).with_name("select_pr_regression.py")
)
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


def _split(args: str) -> list[dict]:
    return selector.split_tiered_storage(
        {"suite_name": "tiered_storage", "regression_args": args, "storage_path": ""}
    )


class TieredStorageSelectionTest(unittest.TestCase):
    def test_mapping_paths_keep_the_local_run_beside_minio(self):
        selected = _split(
            '--only "/tiered storage/*" "/tiered storage/with minio/*"'
        )
        self.assertEqual(
            [job["regression_args"] for job in selected],
            ["--with-minio", '--only "/tiered storage/*"'],
        )
        self.assertEqual(selected[1]["storage_path"], "/local")

    def test_colon_path_stays_on_the_local_job(self):
        selected = _split(
            '--only "/tiered storage/:/alter move/*" "/tiered storage/with minio/*"'
        )
        self.assertEqual(selected[0]["regression_args"], "--with-minio")
        self.assertEqual(
            selected[1]["regression_args"],
            '--only "/tiered storage/:/alter move/*"',
        )

    def test_minio_only_does_not_add_a_local_job(self):
        selected = _split('--only "/tiered storage/with minio/*"')
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["regression_args"], "--with-minio")

    def test_local_only_is_unchanged(self):
        args = '--only "/tiered storage/:/alter move/*"'
        selected = _split(args)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["regression_args"], args)

    def test_narrow_minio_path_keeps_only_with_the_flag(self):
        selected = _split('--only "/tiered storage/with minio/alter move/*"')
        self.assertEqual(len(selected), 1)
        self.assertEqual(
            selected[0]["regression_args"],
            '--with-minio --only "/tiered storage/with minio/alter move/*"',
        )


if __name__ == "__main__":
    unittest.main()
