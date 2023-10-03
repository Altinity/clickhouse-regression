# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0551517009735107
         "DuckDB" : 0.0281014442443847
```
# query_1
```sql
 SELECT pickup_ntaname, count(*) AS count FROM file(nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet) GROUP BY pickup_ntaname ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.1977884769439697
         "DuckDB" : 0.1606957912445068
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 0.1054592132568359
         "DuckDB" : 0.1118226051330566
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0804445743560791
         "DuckDB" : 0.055058479309082
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0905475616455078
         "DuckDB" : 0.0772218704223632
```
# query_5
```sql
 SELECT MIN(pickup_datetime), MAX(pickup_datetime) FROM file('nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0876927375793457
         "DuckDB" : 0.0614073276519775
```
# query_6
```sql
 SELECT trip_id, COUNT(*) FROM file('nyc_taxi_parquet_8b2a8b05_61d9_11ee_924e_01a4aa584ed2.parquet') GROUP BY trip_id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 0.3099191188812256
         "DuckDB" : 0.860234260559082
```
