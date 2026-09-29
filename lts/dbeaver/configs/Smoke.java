import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

/**
 * Replays what DBeaver does against ClickHouse through the driver DBeaver
 * bundles: connect, read the server version, browse the navigator, open a
 * table's properties and DDL, read and insert data. The SQL mirrors the
 * DBeaver ClickHouse plugin (org.jkiss.dbeaver.ext.clickhouse).
 *
 * The dataset, lts_dbeaver.events with 100 rows, is created through the driver
 * the way a user creates it from the DBeaver SQL editor, and then queried.
 * Each check is written as a JUnit testcase to the file given as the first
 * argument.
 */
public class Smoke {
    interface Check {
        void run(Connection connection) throws Exception;
    }

    static final String URL = "jdbc:clickhouse://localhost:8123/default";
    static final String DATABASE = "lts_dbeaver";
    static final String TABLE = "events";

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    static List<String> column(ResultSet resultSet, String name) throws Exception {
        List<String> values = new ArrayList<>();
        while (resultSet.next()) {
            values.add(resultSet.getString(name));
        }
        return values;
    }

    static void execute(Connection connection, String sql) throws Exception {
        try (Statement statement = connection.createStatement()) {
            statement.execute(sql);
        }
    }

    /** Run a query that returns one row and check its columns as strings. */
    static void expect(Connection connection, String sql, String... expected) throws Exception {
        try (Statement statement = connection.createStatement();
                ResultSet resultSet = statement.executeQuery(sql)) {
            require(resultSet.next(), "no rows from: " + sql);
            List<String> actual = new ArrayList<>();
            for (int i = 1; i <= expected.length; i++) {
                actual.add(resultSet.getString(i));
            }
            require(actual.equals(java.util.Arrays.asList(expected)),
                    "expected " + java.util.Arrays.toString(expected) + " but got " + actual + " from: " + sql);
            require(!resultSet.next(), "more than one row from: " + sql);
        }
    }

    static Connection connect() throws Exception {
        Properties properties = new Properties();
        properties.setProperty("user", "default");
        properties.setProperty("password", "");
        return DriverManager.getConnection(URL, properties);
    }

    static Map<String, Check> checks() {
        Map<String, Check> checks = new LinkedHashMap<>();

        checks.put("server version", connection -> {
            try (Statement statement = connection.createStatement();
                    ResultSet resultSet = statement.executeQuery("SELECT VERSION()")) {
                require(resultSet.next(), "SELECT VERSION() returned no rows");
                String version = resultSet.getString(1);
                require(version != null && version.matches("\\d+\\.\\d+.*"), "unexpected version: " + version);
                System.out.println("server version: " + version);
            }
            DatabaseMetaData metaData = connection.getMetaData();
            System.out.println("driver: " + metaData.getDriverName() + " " + metaData.getDriverVersion());
            System.out.println("product: " + metaData.getDatabaseProductName() + " "
                    + metaData.getDatabaseProductVersion());
        });

        checks.put("create dataset", connection -> {
            execute(connection, "DROP DATABASE IF EXISTS " + DATABASE);
            execute(connection, "CREATE DATABASE " + DATABASE);
            execute(connection, "CREATE TABLE " + DATABASE + "." + TABLE + "\n(\n"
                    + "    id UInt64,\n    name String,\n    created DateTime,\n"
                    + "    score Nullable(Float64),\n    tags Array(String)\n)\n"
                    + "ENGINE = MergeTree ORDER BY id COMMENT 'LTS DBeaver smoke table'");
            execute(connection, "INSERT INTO " + DATABASE + "." + TABLE
                    + " SELECT number, concat('name_', toString(number)), now() - number,"
                    + " if(number % 5 = 0, NULL, number / 3), [toString(number), 'tag'] FROM numbers(100)");
        });

        checks.put("navigator databases", connection -> {
            DatabaseMetaData metaData = connection.getMetaData();
            List<String> schemas = column(metaData.getSchemas(), "TABLE_SCHEM");
            List<String> catalogs = column(metaData.getCatalogs(), "TABLE_CAT");
            System.out.println("schemas: " + schemas + ", catalogs: " + catalogs);
            require(schemas.contains(DATABASE) || catalogs.contains(DATABASE),
                    DATABASE + " is not listed in getSchemas() or getCatalogs()");
            column(metaData.getTableTypes(), "TABLE_TYPE");
        });

        checks.put("navigator table engines", connection -> {
            try (Statement statement = connection.createStatement();
                    ResultSet resultSet = statement.executeQuery("SELECT name FROM system.table_engines")) {
                require(column(resultSet, "name").contains("MergeTree"), "MergeTree is not in system.table_engines");
            }
        });

        checks.put("navigator tables", connection -> {
            String sql = "SELECT name as TABLE_NAME, engine as TABLE_TYPE, database as TABLE_SCHEM,"
                    + "comment as REMARKS, * FROM system.tables\nWHERE database = ?";
            try (PreparedStatement statement = connection.prepareStatement(sql)) {
                statement.setString(1, DATABASE);
                try (ResultSet resultSet = statement.executeQuery()) {
                    require(column(resultSet, "TABLE_NAME").contains(TABLE), TABLE + " is not listed");
                }
            }
        });

        checks.put("navigator columns", connection -> {
            try (ResultSet resultSet = connection.getMetaData().getColumns(null, DATABASE, TABLE, "%")) {
                List<String> columns = column(resultSet, "COLUMN_NAME");
                System.out.println("columns: " + columns);
                for (String expected : new String[] { "id", "name", "created", "score", "tags" }) {
                    require(columns.contains(expected), "getColumns() is missing " + expected + ": " + columns);
                }
            }
        });

        checks.put("database statistics", connection -> {
            String sql = "select table,sum(bytes) as table_size, sum(rows) as table_rows, "
                    + "max(modification_time) as latest_modification,min(min_date) AS min_date,"
                    + "max(max_date) AS max_date FROM system.parts\nWHERE database=? AND active\nGROUP BY table";
            try (PreparedStatement statement = connection.prepareStatement(sql)) {
                statement.setString(1, DATABASE);
                try (ResultSet resultSet = statement.executeQuery()) {
                    require(resultSet.next(), "no parts statistics for " + DATABASE);
                    require(resultSet.getLong("table_rows") > 0, "table_rows is 0");
                }
            }
        });

        checks.put("table statistics", connection -> {
            String sql = "select sum(bytes) as table_size, sum(rows) as table_rows, "
                    + "max(modification_time) as latest_modification,min(min_date) AS min_date,"
                    + "max(max_date) AS max_date FROM system.parts\nWHERE active AND database=? AND table=?\n"
                    + "GROUP BY table";
            try (PreparedStatement statement = connection.prepareStatement(sql)) {
                statement.setString(1, DATABASE);
                statement.setString(2, TABLE);
                try (ResultSet resultSet = statement.executeQuery()) {
                    require(resultSet.next(), "no parts statistics for " + TABLE);
                    require(resultSet.getLong("table_rows") == 100, "table_rows is " + resultSet.getLong("table_rows"));
                }
            }
        });

        checks.put("table ddl", connection -> {
            try (Statement statement = connection.createStatement();
                    ResultSet resultSet = statement.executeQuery("SHOW CREATE TABLE " + DATABASE + "." + TABLE)) {
                require(resultSet.next(), "SHOW CREATE TABLE returned no rows");
                String ddl = resultSet.getString(1);
                require(ddl.contains("MergeTree"), "unexpected DDL: " + ddl);
            }
        });

        String from = " FROM " + DATABASE + "." + TABLE;

        checks.put("query count", connection -> {
            expect(connection, "SELECT count()" + from, "100");
            expect(connection, "SELECT count(score)" + from, "80");
        });

        checks.put("query aggregates", connection -> {
            expect(connection, "SELECT sum(id), min(id), max(id), avg(id)" + from, "4950", "0", "99", "49.5");
            expect(connection, "SELECT uniqExact(name)" + from, "100");
        });

        checks.put("query where", connection -> {
            expect(connection, "SELECT count()" + from + " WHERE id < 10 AND name LIKE 'name_%'", "10");
            expect(connection, "SELECT count()" + from + " WHERE score IS NULL", "20");
        });

        checks.put("query group by", connection -> {
            try (Statement statement = connection.createStatement();
                    ResultSet resultSet = statement.executeQuery(
                            "SELECT id % 5 AS bucket, count() AS rows" + from + " GROUP BY bucket ORDER BY bucket")) {
                int buckets = 0;
                while (resultSet.next()) {
                    require(resultSet.getLong("bucket") == buckets, "unexpected bucket " + resultSet.getLong("bucket"));
                    require(resultSet.getLong("rows") == 20, "bucket " + buckets + " has "
                            + resultSet.getLong("rows") + " rows, expected 20");
                    buckets++;
                }
                require(buckets == 5, buckets + " buckets, expected 5");
            }
        });

        checks.put("query order by limit", connection -> {
            try (Statement statement = connection.createStatement();
                    ResultSet resultSet = statement.executeQuery("SELECT id" + from + " ORDER BY id DESC LIMIT 3")) {
                List<String> ids = column(resultSet, "id");
                require(ids.equals(java.util.Arrays.asList("99", "98", "97")), "unexpected ids " + ids);
            }
        });

        checks.put("query array join", connection -> {
            expect(connection, "SELECT count()" + from + " ARRAY JOIN tags AS tag", "200");
            expect(connection, "SELECT countIf(tag = 'tag')" + from + " ARRAY JOIN tags AS tag", "100");
        });

        checks.put("data editor read", connection -> {
            try (Statement statement = connection.createStatement()) {
                statement.setMaxRows(200);
                try (ResultSet resultSet = statement.executeQuery(
                        "SELECT * FROM " + DATABASE + "." + TABLE + " ORDER BY id")) {
                    int rows = 0;
                    while (resultSet.next()) {
                        rows++;
                        long id = resultSet.getLong("id");
                        require(resultSet.getString("name").equals("name_" + id), "wrong name for id " + id);
                        require(resultSet.getTimestamp("created") != null, "created is NULL for id " + id);
                        resultSet.getObject("score");
                        resultSet.getArray("tags");
                    }
                    require(rows == 100, "read " + rows + " rows, expected 100");
                }
            }
        });

        checks.put("data editor insert", connection -> {
            String sql = "INSERT INTO " + DATABASE + "." + TABLE + " (id, name, created, score, tags) "
                    + "VALUES (?, ?, now(), ?, [])";
            try (PreparedStatement statement = connection.prepareStatement(sql)) {
                for (int id = 1000; id < 1003; id++) {
                    statement.setLong(1, id);
                    statement.setString(2, "name_" + id);
                    statement.setNull(3, java.sql.Types.DOUBLE);
                    statement.addBatch();
                }
                statement.executeBatch();
            }
            try (Statement statement = connection.createStatement();
                    ResultSet resultSet = statement.executeQuery(
                            "SELECT count() FROM " + DATABASE + "." + TABLE + " WHERE id >= 1000")) {
                require(resultSet.next() && resultSet.getLong(1) == 3, "inserted rows are not visible");
            }
        });

        return checks;
    }

    static String xml(String text) {
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
    }

    public static void main(String[] args) throws Exception {
        StringBuilder cases = new StringBuilder();
        int failures = 0;
        int total = 0;
        Connection connection = null;
        Throwable connectError = null;
        long start = System.nanoTime();
        try {
            connection = connect();
        } catch (Throwable error) {
            connectError = error;
        }
        Map<String, Check> all = new LinkedHashMap<>();
        all.put("connect", c -> {
        });
        all.putAll(checks());

        for (Map.Entry<String, Check> check : all.entrySet()) {
            total++;
            Throwable error = connectError;
            if (connection != null) {
                if (!check.getKey().equals("connect")) {
                    start = System.nanoTime();
                }
                try {
                    check.getValue().run(connection);
                } catch (Throwable e) {
                    error = e;
                }
            }
            double seconds = (System.nanoTime() - start) / 1e9;
            cases.append(String.format("  <testcase classname=\"smoke\" name=\"%s\" time=\"%.3f\"",
                    xml(check.getKey()), seconds));
            if (error == null) {
                System.out.println("OK    " + check.getKey());
                cases.append("/>\n");
            } else {
                failures++;
                StringWriter trace = new StringWriter();
                error.printStackTrace(new PrintWriter(trace));
                System.out.println("FAIL  " + check.getKey() + "\n" + trace);
                cases.append(String.format(">\n    <failure message=\"%s\">%s</failure>\n  </testcase>\n",
                        xml(String.valueOf(error)), xml(trace.toString())));
            }
        }
        if (connection != null) {
            connection.close();
        }
        String report = String.format("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<testsuite name=\"dbeaver smoke\" tests=\"%d\" failures=\"%d\">\n%s</testsuite>\n",
                total, failures, cases);
        Files.write(Paths.get(args[0]), report.getBytes(StandardCharsets.UTF_8));
    }
}
