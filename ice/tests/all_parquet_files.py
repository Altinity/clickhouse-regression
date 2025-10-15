from parquet.tests.steps.generate_all_files import *
from testflows.core import *




@TestScenario
def run_all_parquet_files(self, pool=3):
    """Run all parquet files generation in parallel."""


    with Given("I generate all possible parquet files"):
        run_all_possible_files(pool=3, json_file_location=os.path.join(current_dir(), "..", "data", "json_files"))

@TestFeature
@Name("parquet files generation")
def feature(self, pool=3):
    """Generate all possible parquet files."""
    Scenario(test=run_all_parquet_files)(pool=pool)