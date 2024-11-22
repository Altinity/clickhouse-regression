from helpers.common import *
from helpers.cluster import *

from collections import namedtuple


@TestStep(Given)
def create_and_drop_tables_old(self, number_of_tables=1000):
    """Create and drop tables."""
    node = self.context.node
    for _ in range(number_of_tables):
        uid = getuid()
        table_name = f"test_table_{uid}"
        node.query(f"DROP TABLE IF EXISTS {table_name}")
        node.query(
            f"CREATE TABLE {table_name} (x UInt8) ENGINE = MergeTree ORDER BY tuple()"
        )
        node.query(f"DROP TABLE {table_name} SYNC")


@TestStep(Given)
def create_and_drop_tables(self, number_of_tables=1000):
    """Create and drop tables."""
    command = ""
    node = self.context.node

    for _ in range(number_of_tables):
        table_name = f"test_table_{getuid()}"
        command += (
            f"DROP TABLE IF EXISTS {table_name}; "
            + f"CREATE TABLE {table_name} (x UInt8) ENGINE = MergeTree ORDER BY tuple(); "
            + f"DROP TABLE {table_name} SYNC; "
            + "SELECT 1 FORMAT TabSeparated; "
        )

    node.query(command)


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

    https://man7.org/linux/man-pages/man5/proc.5.html
    """
    ProcessMemory = namedtuple(
        "ProcessMemory", ["size", "resident", "sharded", "trs", "lrs", "drs", "dt"]
    )
    cmd = self.context.node.command(f"cat /proc/{pid}/statm", exitcode=0)
    return ProcessMemory(*[int(i.strip()) for i in cmd.output.split(" ")])


@TestStep(When)
def get_process_memory_usage_in_kilobytes(self, pid):
    """
    Get process memory usage by reading contents of
    /proc/{pid}/status.

    Provides information about memory usage, measured in
    pages. The example of columns are:

    VmPeak Peak virtual memory size.

    VmSize Virtual memory size.

    VmLck  Locked memory size (see mlock(2)).

    VmPin  Pinned memory size (since Linux 3.2).  These are
            pages that can't be moved because something needs
            to directly access physical memory.

    VmHWM  Peak resident set size ("high water mark").  This
            value is inaccurate; see /proc/pid/statm above.

    VmRSS  Resident set size.  Note that the value here is the
            sum of RssAnon, RssFile, and RssShmem.  This value
            is inaccurate; see /proc/pid/statm above.

    RssAnon
            Size of resident anonymous memory.  (since Linux
            4.5).  This value is inaccurate; see
            /proc/pid/statm above.

    RssFile
            Size of resident file mappings.  (since Linux 4.5).
            This value is inaccurate; see /proc/pid/statm
            above.

    RssShmem
            Size of resident shared memory (includes System V
            shared memory, mappings from tmpfs(5), and shared
            anonymous mappings).  (since Linux 4.5).

    https://man7.org/linux/man-pages/man5/proc.5.html
    """
    ProcessMemory = namedtuple(
        "ProcessMemory",
        [
            "VmPeak",
            "VmSize",
            "VmLck",
            "VmPin",
            "VmHWM",
            "VmRSS",
            "VmData",
            "VmStk",
            "VmExe",
            "VmLib",
            "VmPTE",
            "VmSwap",
        ],
    )
    cmd = self.context.node.command(f"grep Vm /proc/{pid}/status", exitcode=0).output
    """
    VmPeak:	 3420468 kB
    VmSize:	 3420468 kB
    VmLck:	       0 kB
    VmPin:	       0 kB
    VmHWM:	  440460 kB
    VmRSS:	  435520 kB  ----> ['3420468', '3420468', '0', '0', '440460', '435520', '2515044', '132', '291976', '2520', '2212', '0']
    VmData:	 2515044 kB
    VmStk:	     132 kB
    VmExe:	  291976 kB
    VmLib:	    2520 kB
    VmPTE:	    2212 kB
    VmSwap:	       0 kB
    """
    output = [line.split("\t")[1].strip().split(" ")[0] for line in cmd.split("\n")]
    return ProcessMemory(*[int(i.strip()) for i in output])


@TestScenario
def check_create_and_drop_tables(
    self,
    number_of_workers=20,
    number_of_tables=15000,
    node=None,
    timeout=3600,
):
    """Test memory leak when we create and drop many tables."""
    if node is None:
        node = self.context.node

    pid = self.context.node.clickhouse_pid()

    with Given("I collect initial memory usage of clickhouse server process"):
        start_memory = get_process_memory_usage(pid=pid)
        note(f"start resident memory: {start_memory.resident}")

    with When(
        "I create and drop large number of tables in parallel",
        description=f"number of workers = {number_of_workers}, number of tables = {number_of_tables}",
    ):
        create_and_drop_tables_parallel(
            number_of_workers=number_of_workers, number_of_tables=number_of_tables
        )

    with And("I collect memory usage after I create and drop large number of tables"):
        end_memory = get_process_memory_usage(pid=pid)
        note(f"end resident memory: {end_memory.resident}")

    with Then("I check for memory leaks and calculate released memory"):
        max_memory = 200000
        for attempt in retries(timeout=timeout, delay=10):
            with attempt:
                current_memory = get_process_memory_usage(pid=pid)
                released_memory = end_memory.resident - current_memory.resident
                note(f"start resident memory: {start_memory.resident}")
                note(f"current resident memory: {current_memory.resident}")
                note(f"released memory: {released_memory}")
                assert (
                    current_memory.resident - start_memory.resident <= max_memory
                ), f"Memory usage {current_memory.resident - start_memory.resident} larger than expected {max_memory}"


@TestFeature
@Name("memory leak")
def feature(self, node="clickhouse1"):
    """Test for checking memory leaks."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
