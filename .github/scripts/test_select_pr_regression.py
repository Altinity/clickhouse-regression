import importlib.util
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("selector", Path(__file__).with_name("select_pr_regression.py"))
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


class TieredStorageSelectionTest(unittest.TestCase):
    def test_normal_suite_is_not_dropped_when_minio_is_also_selected(self):
        suites = [{"path": "tiered_storage"}]
        jobs = [{
            "suite_name": "tiered_storage",
            "regression_args": '--only "/tiered storage/normal/*" "/tiered storage/with minio/*"',
        }]
        selected = selector.validate_jobs(suites, jobs)
        self.assertEqual(len(selected), 2)
        self.assertTrue(any('--only "/tiered storage/normal/*"' in job["regression_args"] for job in selected))
        self.assertTrue(any('--with-minio' in job["regression_args"] for job in selected))

    def test_minio_only_does_not_add_normal_job(self):
        suites = [{"path": "tiered_storage"}]
        jobs = [{"suite_name": "tiered_storage", "regression_args": '--only "/tiered storage/with minio/*"'}]
        selected = selector.validate_jobs(suites, jobs)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["regression_args"], "--with-minio")

    def test_normal_only_is_unchanged(self):
        suites = [{"path": "tiered_storage"}]
        args = '--only "/tiered storage/normal/*"'
        selected = selector.validate_jobs(suites, [{"suite_name": "tiered_storage", "regression_args": args}])
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["regression_args"], args)


if __name__ == "__main__":
    unittest.main()
