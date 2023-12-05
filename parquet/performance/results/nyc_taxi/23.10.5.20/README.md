# ClickHouse vs DuckDB (Runtime in Seconds)

## Versions
  * ClickHouse: 23.10.5.20-alpine
  * DuckDB: 0.9.2

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2411859035491943
         "DuckDB" : 0.2192013263702392
```
# query_1
```sql
 SELECT pickup_longitude, count(*) AS count FROM file(nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet) GROUP BY pickup_longitude ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 4.664350748062134
         "DuckDB" : 2.82434606552124
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 4.036071062088013
         "DuckDB" : 1.6346712112426758
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 2.4142653942108154
         "DuckDB" : 0.8447716236114502
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 6.256786823272705
         "DuckDB" : 2.1151680946350098
```
# query_5
```sql
 SELECT MIN(pickup_date), MAX(pickup_date) FROM file('nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 2.249696016311645
         "DuckDB" : 0.4512529373168945
```
# query_6
```sql
 SELECT id, COUNT(*) FROM file('nyc_taxi_parquet_bca58251_9353_11ee_9cb0_3b79d3d65d52.parquet') GROUP BY id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 2.701810598373413
         "DuckDB" : 0.857733964920044
```
