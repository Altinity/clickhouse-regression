import os
from testflows.core import *


def discover_test_features(current_dir=None, subdirectory=None):
    """Discover all test feature modules in the hybrid_alias/tests directory.

    Args:
        current_dir: Directory to scan. Defaults to tests/ directory.
        subdirectory: Optional subdirectory name (e.g., 'arithmetic', 'constants') for module path construction.
    """
    if current_dir is None:
        base_dir = os.path.dirname(__file__)
        current_dir = os.path.join(base_dir, "tests")
    test_features = []

    # Files to exclude
    exclude_files = {"feature.py", "outline.py", "__init__.py"}

    for filename in os.listdir(current_dir):
        if filename.endswith(".py") and filename not in exclude_files:
            module_name = filename[:-3]  # Remove .py
            # Construct module path based on subdirectory
            if subdirectory:
                module_path = f"ice.tests.hybrid.hybrid_alias.tests.{subdirectory}.{module_name}"
            else:
                module_path = f"ice.tests.hybrid.hybrid_alias.tests.{module_name}"
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
    tests_dir = os.path.join(base_dir, "tests")

    with Feature("arithmetic"):
        arithmetic_dir = os.path.join(tests_dir, "arithmetic")
        test_features = discover_test_features(current_dir=arithmetic_dir, subdirectory="arithmetic")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("constants"):
        constants_dir = os.path.join(tests_dir, "constants")
        test_features = discover_test_features(current_dir=constants_dir, subdirectory="constants")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("math functions"):
        math_functions_dir = os.path.join(tests_dir, "math_functions")
        test_features = discover_test_features(current_dir=math_functions_dir, subdirectory="math_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("rounding functions"):
        rounding_functions_dir = os.path.join(tests_dir, "rounding_functions")
        test_features = discover_test_features(current_dir=rounding_functions_dir, subdirectory="rounding_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("boolean logical"):
        boolean_logical_dir = os.path.join(tests_dir, "boolean_logical")
        test_features = discover_test_features(current_dir=boolean_logical_dir, subdirectory="boolean_logical")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("datetime functions"):
        datetime_functions_dir = os.path.join(tests_dir, "datetime_functions")
        test_features = discover_test_features(current_dir=datetime_functions_dir, subdirectory="datetime_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("string functions"):
        string_functions_dir = os.path.join(tests_dir, "string_functions")
        test_features = discover_test_features(current_dir=string_functions_dir, subdirectory="string_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("type conversions"):
        type_conversions_dir = os.path.join(tests_dir, "type_conversions")
        test_features = discover_test_features(current_dir=type_conversions_dir, subdirectory="type_conversions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("conditional functions"):
        conditional_functions_dir = os.path.join(tests_dir, "conditional_functions")
        test_features = discover_test_features(
            current_dir=conditional_functions_dir, subdirectory="conditional_functions"
        )
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("nested dependent"):
        nested_dependent_dir = os.path.join(tests_dir, "nested_dependent")
        test_features = discover_test_features(current_dir=nested_dependent_dir, subdirectory="nested_dependent")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("utility functions"):
        utility_functions_dir = os.path.join(tests_dir, "utility_functions")
        test_features = discover_test_features(current_dir=utility_functions_dir, subdirectory="utility_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("complex expressions"):
        complex_expressions_dir = os.path.join(tests_dir, "complex_expressions")
        test_features = discover_test_features(current_dir=complex_expressions_dir, subdirectory="complex_expressions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("array functions"):
        array_functions_dir = os.path.join(tests_dir, "array_functions")
        test_features = discover_test_features(current_dir=array_functions_dir, subdirectory="array_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("tuple functions"):
        tuple_functions_dir = os.path.join(tests_dir, "tuple_functions")
        test_features = discover_test_features(current_dir=tuple_functions_dir, subdirectory="tuple_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("map functions"):
        map_functions_dir = os.path.join(tests_dir, "map_functions")
        test_features = discover_test_features(current_dir=map_functions_dir, subdirectory="map_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("json functions"):
        json_functions_dir = os.path.join(tests_dir, "json_functions")
        test_features = discover_test_features(current_dir=json_functions_dir, subdirectory="json_functions")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("hash encoding functions"):
        hash_encoding_functions_dir = os.path.join(tests_dir, "hash_encoding_functions")
        test_features = discover_test_features(
            current_dir=hash_encoding_functions_dir, subdirectory="hash_encoding_functions"
        )
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("query context"):
        query_context_dir = os.path.join(tests_dir, "query_context")
        test_features = discover_test_features(current_dir=query_context_dir, subdirectory="query_context")
        run_tests(test_features, minio_root_user=minio_root_user, minio_root_password=minio_root_password)
