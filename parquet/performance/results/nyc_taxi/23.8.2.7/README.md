# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0537638664245605
         "DuckDB" : 0.0245544910430908
```
# query_1
```sql
 SELECT pickup_ntaname, count(*) AS count FROM file(nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet) GROUP BY pickup_ntaname ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.1874408721923828
         "DuckDB" : 0.159839391708374
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 0.1051983833312988
         "DuckDB" : 0.1048510074615478
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0848035812377929
         "DuckDB" : 0.0477464199066162
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0844802856445312
         "DuckDB" : 0.0726268291473388
```
# query_5
```sql
 SELECT MIN(pickup_datetime), MAX(pickup_datetime) FROM file('nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 0.0899469852447509
         "DuckDB" : 0.0552434921264648
```
# query_6
```sql
 SELECT trip_id, COUNT(*) FROM file('nyc_taxi_parquet_c0a2032e_5df6_11ee_924e_01a4aa584ed2.parquet') GROUP BY trip_id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2951877117156982
         "DuckDB" : 0.8291106224060059
```
