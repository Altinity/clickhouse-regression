import os
from testflows.core import *


def discover_test_features(current_dir=None, subdirectory=None):
    """Discover all test feature modules in the hybrid_alias directory.

    Args:
        current_dir: Directory to scan. Defaults to the directory containing this file.
        subdirectory: Optional subdirectory name (e.g., 'arithmetic', 'constants') for module path construction.
    """
    if current_dir is None:
        current_dir = os.path.dirname(__file__)
    test_features = []

    # Files to exclude
    exclude_files = {"feature.py", "outline.py"}

    for filename in os.listdir(current_dir):
        if filename.endswith(".py") and filename not in exclude_files:
            module_name = filename[:-3]  # Remove .py
            # Construct module path based on subdirectory
            if subdirectory:
                module_path = f"ice.tests.hybrid.hybrid_alias.{subdirectory}.{module_name}"
            else:
                module_path = f"ice.tests.hybrid.hybrid_alias.{module_name}"
            test_features.append(module_path)

    return test_features


def run_tests(test_features, minio_root_user=None, minio_root_password=None):
    for module_path in test_features:
        try:
            test = load(module_path, "feature")
        except Exception as e:
            note(f"Failed to load feature from {module_path}: {e}")
            assert False, f"Failed to load feature from {module_path}: {e}"

        Scenario(test=test)(minio_root_user=minio_root_user, minio_root_password=minio_root_password)


@TestFeature
@Name("hybrid_alias")
def feature(self, minio_root_user, minio_root_password):
    """Test hybrid alias support."""
    test_features = discover_test_features()

    run_tests(test_features=test_features)

    base_dir = os.path.dirname(__file__)

    with Feature("arithmetic"):
        arithmetic_dir = os.path.join(base_dir, "arithmetic")
        test_features = discover_test_features(current_dir=arithmetic_dir, subdirectory="arithmetic")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("constants"):
        constants_dir = os.path.join(base_dir, "constants")
        test_features = discover_test_features(current_dir=constants_dir, subdirectory="constants")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)
