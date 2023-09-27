# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0436403751373291
         "DuckDB" : 0.0259654521942138
```
# query_1
```sql
 SELECT pickup_ntaname, count(*) AS count FROM file(nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet) GROUP BY pickup_ntaname ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.1103103160858154
         "DuckDB" : 0.0929312705993652
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0576138496398925
         "DuckDB" : 0.0636413097381591
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.050018310546875
         "DuckDB" : 0.0371873378753662
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0467145442962646
         "DuckDB" : 0.0509572029113769
```
# query_5
```sql
 SELECT MIN(pickup_datetime), MAX(pickup_datetime) FROM file('nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0610013008117675
         "DuckDB" : 0.0362465381622314
```
# query_6
```sql
 SELECT trip_id, COUNT(*) FROM file('nyc_taxi_parquet_3767f60d_5d8b_11ee_924e_01a4aa584ed2.parquet') GROUP BY trip_id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0848152637481689
         "DuckDB" : 0.2903854846954345
```
