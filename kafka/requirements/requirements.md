# SRS-040 ClickHouse Kafka Engine
# Software Requirements Specification

## Table of Contents


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification (SRS) covers the requirements for the [Kafka Engine] in [ClickHouse]. The Kafka engine in ClickHouse allows real-time streaming and ingestion of data from Kafka topics into ClickHouse tables for analytics and large-scale processing. This engine works with [Apache Kafka], which is a distributed event streaming platform designed for high-throughput, fault-tolerant data processing.

Kafka lets you:
- Publish or subscribe to data flows.
- Organize fault-tolerant storage.
- Process streams as they become available.

### Syntax
#### Creating a Table
```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name [ON CLUSTER cluster]
(
    name1 [type1] [ALIAS expr1],
    name2 [type2] [ALIAS expr2],
    ...
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'host:port',
    kafka_topic_list = 'topic1,topic2,...',
    kafka_group_name = 'group_name',
    kafka_format = 'data_format'[,]
    [kafka_schema = '',]
    [kafka_num_consumers = N,]
    [kafka_max_block_size = 0,]
    [kafka_skip_broken_messages = N,]
    [kafka_commit_every_batch = 0,]
    [kafka_client_id = '',]
    [kafka_poll_timeout_ms = 0,]
    [kafka_poll_max_batch_size = 0,]
    [kafka_flush_interval_ms = 0,]
    [kafka_thread_per_consumer = 0,]
    [kafka_handle_error_mode = 'default',]
    [kafka_commit_on_select = false,]
    [kafka_max_rows_per_message = 1];
```
**Required parameters:**

- kafka_broker_list — A comma-separated list of brokers (for example, localhost:9092).
- kafka_topic_list — A list of Kafka topics.
- kafka_group_name — A group of Kafka consumers. 
- kafka_format — Message format (for example JSONEachRow).

## Requirements

### RQ.SRS-040.ClickHouse.KafkaEngine.CreateTable
version: 1.0

[ClickHouse] SHALL support creating tables with the Kafka engine.

### RQ.SRS-040.ClickHouse.KafkaEngine.DefaultValues
version: 1.0  

[ClickHouse] SHALL not support columns with default values directly in Kafka tables.


### RQ.SRS-040.ClickHouse.KafkaEngine.MultipleTopics
version: 1.0  

[ClickHouse] SHALL support consuming data from multiple Kafka topics simultaneously.


### RQ.SRS-040.ClickHouse.KafkaEngine.Data Ingestion
version: 1.0  

[ClickHouse] SHALL reliably consume messages from specified Kafka topics and insert them into corresponding tables without data loss.

### RQ.SRS-040.ClickHouse.KafkaEngine.MaterializedViews
Version: 1.0  

[ClickHouse] SHALL support materialized views to automatically insert data from tables with Kafka engine into MergeTree tables.

### RQ.SRS-040.ClickHouse.KafkaEngine.OffsetManagement
Version: 1.0   

[ClickHouse] SHALL support both automatic and manual offset management for consuming messages from Kafka topics.


### RQ.SRS-040.ClickHouse.KafkaEngine.BatchConsumption
Version: 1.0

[ClickHouse] SHALL support configurable batch consumption of messages from Kafka topics using the kafka_max_block_size parameter.

### RQ.SRS-040.ClickHouse.KafkaEngine.SSL_TLS
Version: 1.0

[ClickHouse] SHALL support SSL/TLS encryption for secure communication between Kafka brokers and ClickHouse.


### RQ.SRS-040.ClickHouse.KafkaEngine.DataFormatSupport
Version: 1.0

[ClickHouse] SHALL support various message formats (e.g., JSONEachRow, Avro, Protobuf) for consuming Kafka messages.

### RQ.SRS-040.ClickHouse.KafkaEngine.SystemTable.Kafka_Consumers
Version: 1.0  

[ClickHouse] SHALL reflect information about Kafka consumers in the kafka_consumers system table.

### RQ.SRS-040.ClickHouse.KafkaEngine.LargeMessageSupport
Version: 1.0

[ClickHouse] SHALL support consumption of large Kafka messages by allowing configuration of the maximum message size through settings such as `kafka_max_partition_fetch_bytes` and `kafka_max_message_size`.

## References
* [Kafka Engine]
* [Apache Kafka]
* [ClickHouse]


[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/kafka/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/kafka/requirements/requirements.md
[ClickHouse]: https://clickhouse.com
[Kafka Engine]: https://clickhouse.com/docs/en/engines/table-engines/integrations/kafka
[Apache Kafka]: http://kafka.apache.org/