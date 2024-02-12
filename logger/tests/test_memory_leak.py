from helpers.common import *
from helpers.cluster import *

from collections import namedtuple


@TestStep(Given)
def create_and_drop_tables(self, number_of_tables=1000):
    """Create and drop tables."""
    node = self.context.node
    for _ in range(number_of_tables):
        uid = getuid()
        table_name = f"test_table_{uid}"
        node.query(f"DROP TABLE IF EXISTS {table_name}")
        node.query(
            f"CREATE TABLE {table_name} (x UInt8) ENGINE = MergeTree ORDER BY ();"
        )
        node.query(f"DROP TABLE {table_name} SYNC;")


@TestStep(Given)
def create_and_drop_tables_parallel(self, number_of_workers=3, number_of_tables=1000):
    """Create and drop tables in parallel using the specified number of workers and tables."""
    with Pool(number_of_workers) as executor:
        for _ in range(number_of_workers):
            Step(test=create_and_drop_tables, parallel=True, executor=executor)(
                number_of_tables=number_of_tables
            )
        join()


@TestStep(When)
def get_process_memory_usage(self, pid):
    """
    Get process memory usage by reading contents of
    /proc/{pid}/statm.

    Provides information about memory usage, measured in
    pages.  The columns are:

        size       (1) total program size
                    (same as VmSize in /proc/pid/status)
        resident   (2) resident set size
                    (inaccurate; same as VmRSS in /proc/pid/status)
        shared     (3) number of resident shared pages
                    (i.e., backed by a file)
                    (inaccurate; same as RssFile+RssShmem in
                    /proc/pid/status)
        text       (4) text (code)
        lib        (5) library (unused since Linux 2.6; always 0)
        data       (6) data + stack
        dt         (7) dirty pages (unused since Linux 2.6; always 0)

    Some of these values are inaccurate because of a kernel-
    internal scalability optimization.  If accurate values are
    required, use /proc/pid/smaps or /proc/pid/smaps_rollup
    instead, which are much slower but provide accurate,
    detailed information.
    """
    ProcessMemory = namedtuple(
        "ProcessMemory", ["size", "resident", "sharded", "trs", "lrs", "drs", "dt"]
    )
    cmd = self.context.node.command(f"cat /proc/{pid}/statm", exitcode=0)
    return ProcessMemory(*[int(i.strip()) for i in cmd.output.split(" ")])


@TestScenario
def check_create_and_drop_tables(
    self,
    number_of_workers=10,
    number_of_tables=3000,
    node=None,
    max_memory_increase=1.3,
    timeout=300,
):
    """Test memory leak when we create and drop many tables."""
    if node is None:
        node = self.context.node

    pid = self.context.node.clickhouse_pid()

    with Given("I collect initial memory usage of clickhouse server process"):
        start_memory = get_process_memory_usage(pid=pid)
        note(f"start resident memory: {start_memory.resident}")

    with When(
        "I create and drop large amount of tables in parallel",
        description=f"number of workers = {number_of_workers}, number of tables = {number_of_tables}",
    ):
        create_and_drop_tables_parallel(
            number_of_workers=number_of_workers, number_of_tables=number_of_tables
        )

    with And("I collect memory usage after I create and drop large amount of tables"):
        end_memory = get_process_memory_usage(pid=pid)
        note(f"end resident memory: {end_memory.resident}")

    with Then("I check for memory leaks"):
        max_memory = start_memory.resident * max_memory_increase
        for attempt in retries(timeout=timeout, delay=10):
            with attempt:
                current_memory = get_process_memory_usage(pid=pid)
                note(f"start resident memory: {start_memory.resident}")
                note(f"current resident memory: {current_memory.resident}")
                assert (
                    current_memory.resident <= max_memory
                ), f"Memory usage {current_memory.resident} larger than expected {max_memory}"

    with Then("I calculate released memory"):
        counter = 0
        while counter < 5:
            if get_process_memory_usage(pid=pid).resident == current_memory.resident:
                counter += 1
            else:
                counter = 0
            current_memory = get_process_memory_usage(pid=pid)
            time.sleep(10)

        released_memory = end_memory.resident - current_memory.resident
        note(f"released memory: {released_memory}")


@TestFeature
@Name("memory leak")
def feature(self, node="clickhouse1"):
    """Test for checking memory leaks."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
