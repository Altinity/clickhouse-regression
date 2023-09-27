# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0384230613708496
         "DuckDB" : 0.0128185749053955
```
# query_1
```sql
 SELECT pickup_ntaname, count(*) AS count FROM file(nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet) GROUP BY pickup_ntaname ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0579042434692382
         "DuckDB" : 0.0521886348724365
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0363545417785644
         "DuckDB" : 0.0342824459075927
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0329134464263916
         "DuckDB" : 0.0204555988311767
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.032301902770996
         "DuckDB" : 0.0236201286315917
```
# query_5
```sql
 SELECT MIN(pickup_datetime), MAX(pickup_datetime) FROM file('nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0343353748321533
         "DuckDB" : 0.0218749046325683
```
# query_6
```sql
 SELECT trip_id, COUNT(*) FROM file('nyc_taxi_parquet_1014e459_5d8a_11ee_8734_83580fb48b84.parquet') GROUP BY trip_id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 0.107790470123291
         "DuckDB" : 0.1989874839782714
```
