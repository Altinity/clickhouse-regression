# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.5346376895904541
         "DuckDB" : 0.3373122215270996
```
# query_1
```sql
 SELECT pickup_longitude, count(*) AS count FROM file(nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet) GROUP BY pickup_longitude ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 8.688949584960938
         "DuckDB" : 3.171584129333496
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 5.821465015411377
         "DuckDB" : 1.6888644695281982
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 4.4605934619903564
         "DuckDB" : 0.9681718349456788
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 8.381251096725464
         "DuckDB" : 2.249455690383911
```
# query_5
```sql
 SELECT MIN(pickup_date), MAX(pickup_date) FROM file('nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 4.399835109710693
         "DuckDB" : 0.5634846687316895
```
# query_6
```sql
 SELECT id, COUNT(*) FROM file('nyc_taxi_parquet_a32f3e03_9875_11ee_9a07_9f7bda011822.parquet') GROUP BY id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 4.303677558898926
         "DuckDB" : 0.8618049621582031
```
