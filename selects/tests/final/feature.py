from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
import sys

append_path(sys.path, "..")


@TestModule
@Name("final")
def module(self):
    """Check FINAL modifier."""
    self.context.tables = []

    # with Given("I create and populate all tables from Log, Mergetree families"):
    #     create_and_populate_core_tables()
    #     create_and_populate_core_tables(duplicate=True)
    #
    # with And("I add system tables"):
    #     add_system_tables()
    #
    # with And("I create and populate distributed tables"):
    #     create_and_populate_distributed_tables()
    #
    # with And("I create normal, materialized, live and window views"):
    #     create_all_views()
    #     create_normal_view_with_join()
    #
    # with And("I create and populate replicated tables"):
    #     create_replicated_table_2shards3replicas()
    #
    # with And("I create and populate table for subquery tests"):
    #     create_expression_subquery_table()
    #
    # with And("I create table with alias column"):
    #     create_alias_table()

    Feature(run=load("final.modifier", "feature"))
    Feature(run=load("final.force.modifier", "feature"))
    Feature(run=load("final.force.concurrent", "feature"))
    Feature(run=load("final.force.user_rights", "feature"))
