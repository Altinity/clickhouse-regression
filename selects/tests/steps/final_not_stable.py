from testflows.core import *
from testflows.connect import Shell
from testflows.asserts import error


@TestModule
@Repeat(20, until='fail')
def check_select(self):
    try:
        with Given("I create table with ReplacingMergeTree engine"):
            with Shell() as bash:
                cmd1 = bash(
                    f'clickhouse-client -q "CREATE TABLE tmp_table (number UInt64) ENGINE = ReplacingMergeTree ORDER BY number"'
                )
                assert cmd1.exitcode == 0, cmd1.output

        with When("I insert some duplicate data in it"):
            for i in range(20):
                with Shell() as bash:
                    cmd2 = bash(
                        f'clickhouse-client -q "INSERT INTO tmp_table VALUES ({i});"'
                    )
                    cmd3 = bash(
                        f'clickhouse-client -q "INSERT INTO tmp_table VALUES ({i});"'
                    )
                    cmd4 = bash(
                        f'clickhouse-client -q "INSERT INTO tmp_table VALUES ({i});"'
                    )
                    assert (
                        cmd2.exitcode == 0 and cmd3.exitcode == 0 and cmd4.exitcode == 0
                    )
        with Then("select result check without and with --final"):
            with Shell() as bash:
                cmd1 = bash(
                    'clickhouse-client -q "SELECT time, round(exp_smooth,10), bar(exp_smooth, -9223372036854775807, 1048575, 50) AS bar FROM (SELECT 2 OR (number = 0) OR (number >= 1) AS value, number AS time, exponentialTimeDecayedSum(2147483646)(value, time) OVER (order by number desc RANGE BETWEEN CURRENT ROW AND CURRENT ROW) AS exp_smooth FROM tmp_table ORDER BY number) ORDER BY time SETTINGS final = 1; "'
                )
                cmd2 = bash(
                    'clickhouse-client -q "SELECT time, round(exp_smooth,10), bar(exp_smooth, -9223372036854775807, 1048575, 50) AS bar FROM (SELECT 2 OR (number = 0) OR (number >= 1) AS value, number AS time, exponentialTimeDecayedSum(2147483646)(value, time) OVER (order by number desc RANGE BETWEEN CURRENT ROW AND CURRENT ROW) AS exp_smooth FROM tmp_table FINAL ORDER BY number) ORDER BY time; "'
                )
                assert cmd1.output == cmd2.output
    finally:
        with Finally("I drop the table"):
            with Shell() as bash:
                cmd = bash('clickhouse-client -q "DROP TABLE IF EXISTS tmp_table"')


if main():
    Module(run=check_select)