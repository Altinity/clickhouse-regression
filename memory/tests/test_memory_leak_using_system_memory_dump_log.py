from helpers.common import *


@TestStep(Given)
def create_and_drop_table(self, number_of_tables=100):
    node = self.context.node
    uid = getuid()
    table_name = f"test_table{uid}"
    for _ in range(number_of_tables):
        node.query(f"DROP TABLE IF EXISTS {table_name}")
        node.query(
            f"CREATE TABLE {table_name} (x UInt8) ENGINE = MergeTree ORDER BY ();"
        )
        node.query(f"DROP TABLE {table_name} SYNC;")


@TestScenario
def check_leak_with_system_memory_dump_log(self, node=None):
    if check_clickhouse_version("<24.4")(self):
        skip("system.memory_dump_log is available from 24.4")

    if node is None:
        node = self.context.node

    with Given("I create 1000 tables in parallel"):
        with Pool(10) as executor:
            for _ in range(10):
                Step(test=create_and_drop_table, parallel=True, executor=executor)(
                    number_of_tables=100
                )
            join()

    with Then("I check total memory leaked by Poco::Logger::unsafeGet"):
        event_time = node.query(f"SELECT now() FORMAT TabSeparated").output.strip()
        node.query(
            f"SELECT formatReadableSize(sum(size)) AS total_size, count() AS count FROM system.memory_dump_log WHERE event_time='{event_time}' FORMAT PrettyCompact"
        )
        query = f"""
            SELECT
                formatReadableSize(sum(total_size)),
                sum(total_count) AS total_count
            FROM
            (
                SELECT
                    substring(leak_function, 1, 50),
                    sum(total_size) AS total_size,
                    sum(count) AS total_count
                FROM
                (
                    SELECT
                        traces[index + 1] AS leak_function,
                        total_size,
                        count
                    FROM
                    (
                        SELECT
                            trace,
                            arrayMap(x -> demangle(addressToSymbol(x)), trace) AS traces,
                            indexOf(traces, 'Poco::Logger::get(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char>> const&)') AS index,
                            arrayStringConcat(traces, '\n') AS trace_string,
                            sum(size) AS total_size,
                            count() AS count
                        FROM system.memory_dump_log
                        WHERE (event_time = '{event_time}') AND (trace_string LIKE '%Poco::Logger::unsafeGet%')
                        GROUP BY trace
                        HAVING count > 1000
                        ORDER BY count DESC
                    )
                )
                GROUP BY leak_function
                SETTINGS allow_introspection_functions=1
            ) FORMAT TabSeparated
        """

        result = node.query(query).output
        assert result.strip() == "0.00 B	0"


@TestFeature
@Name("memory")
def feature(self):
    """Check logger leak."""
    for scenario in loads(current_module(), Scenario):
        scenario()
