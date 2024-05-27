from contextlib import contextmanager

from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.helper.common import *
import rbac.helper.errors as errors


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_Table_PublicTables("1.0"),
)
def public_tables(self, node=None):
    """Check that a user with no privilege is able to select from public tables."""
    user_name = f"user_{getuid()}"
    if node is None:
        node = self.context.node

    with user(node, f"{user_name}"):
        with When("I check the user is able to select on system.one"):
            node.query(
                "SELECT count(*) FROM system.one FORMAT TabSeparated",
                settings=[("user", user_name)],
            )

        with And("I check the user is able to select on system.numbers"):
            exitcode, message = None, None
            if check_clickhouse_version(">=24.4")(self):
                exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                "SELECT * FROM system.numbers LIMIT 1 FORMAT TabSeparated",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )

        with And("I check the user is able to select on system.contributors"):
            node.query(
                "SELECT count(*) FROM system.contributors FORMAT TabSeparated",
                settings=[("user", user_name)],
            )

        with And("I check the user is able to select on system.functions"):
            node.query(
                "SELECT count(*) FROM system.functions FORMAT TabSeparated",
                settings=[("user", user_name)],
            )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_Table_SensitiveTables("1.0"),
)
def sensitive_tables(self, node=None):
    """Check that a user with no privilege is not able to see from these tables."""
    user_name = f"user_{getuid()}"
    exitcode, message = errors.not_enough_privileges(name=user_name)
    if node is None:
        node = self.context.node

    with user(node, f"{user_name}"):
        with Given("I create a query"):
            node.query("SELECT 1 FORMAT TabSeparated")

        with When("I select from processes"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.processes FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.processes FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from query_log"):
            node.query("SYSTEM FLUSH LOGS")
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.query_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.query_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from query_thread_log"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.query_thread_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.query_thread_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from query_views_log"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.query_views_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.query_views_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from clusters"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.clusters FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.clusters FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from events"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.events FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.events FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from graphite_retentions"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.graphite_retentions FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.graphite_retentions FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from stack_trace"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.stack_trace FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.stack_trace FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from trace_log"):
            if check_clickhouse_version(">=24.4")(self):
                output = node.query(
                    "SELECT count(*) FROM system.trace_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.trace_log FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from user_directories"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.user_directories FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.user_directories FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from zookeeper"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.zookeeper WHERE path = '/clickhouse' FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.zookeeper WHERE path = '/clickhouse' FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()

        with And("I select from macros"):
            if check_clickhouse_version(">=24.4")(self):
                node.query(
                    "SELECT count(*) FROM system.macros FORMAT TabSeparated",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )
            else:
                output = node.query(
                    "SELECT count(*) FROM system.macros FORMAT TabSeparated",
                    settings=[("user", user_name)],
                ).output
                assert output == 0, error()


@TestFeature
@Name("public tables")
def feature(self, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    Scenario(run=public_tables, setup=instrument_clickhouse_server_log)
    Scenario(run=sensitive_tables, setup=instrument_clickhouse_server_log)
