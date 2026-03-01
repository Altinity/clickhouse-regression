CREATE TABLE IF NOT EXISTS default.test_grafana
(
    event_time DateTime,
    service_name LowCardinality(String),
    from_user LowCardinality(String),
    country LowCardinality(String),
    too_big_value Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, service_name);

INSERT INTO default.test_grafana(event_time, service_name, from_user, country, too_big_value)
SELECT
    toDateTime(now() - (number * 10)) AS event_time,
    if(rand() % 2 = 1, 'mysql', 'postgresql') AS service_name,
    if(rand() % 2 = 1, 'bob', 'alice') AS from_user,
    multiIf(
        rand() % 5 = 1, 'US',
        rand() % 5 = 2, 'DE',
        rand() % 5 = 3, 'CN',
        rand() % 5 = 4, 'UK',
        'FR'
    ) AS country,
    1000000000.05 AS too_big_value
FROM numbers(100);
