CREATE DATABASE IF NOT EXISTS lts;

CREATE TABLE IF NOT EXISTS lts.events
(
    event_time  DateTime,
    user_id     UInt64,
    country     LowCardinality(String),
    action      LowCardinality(String),
    amount      Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);

INSERT INTO lts.events (event_time, user_id, country, action, amount)
SELECT
    toDateTime('2024-01-01 00:00:00') + (number * 60) AS event_time,
    (number % 50) + 1                                  AS user_id,
    multiIf(
        number % 5 = 0, 'US',
        number % 5 = 1, 'DE',
        number % 5 = 2, 'FR',
        number % 5 = 3, 'UK',
        'JP'
    )                                                  AS country,
    multiIf(
        number % 3 = 0, 'view',
        number % 3 = 1, 'click',
        'purchase'
    )                                                  AS action,
    (number % 1000) * 0.5                              AS amount
FROM numbers(1000);
