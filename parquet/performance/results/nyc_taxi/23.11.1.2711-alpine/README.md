# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.3586032390594482
         "DuckDB" : 0.3380982875823974
```
# query_1
```sql
 SELECT pickup_longitude, count(*) AS count FROM file(nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet) GROUP BY pickup_longitude ORDER BY count DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 9.215280532836914
         "DuckDB" : 3.211242198944092
```
# query_2
```sql
 SELECT passenger_count, avg(total_amount) FROM file('nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet') GROUP BY passenger_count;
```

```mermaid
     pie showData
         "ClickHouse" : 5.470726013183594
         "DuckDB" : 1.757521390914917
```
# query_3
```sql
 SELECT AVG(tip_amount) FROM file('nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 3.2928099632263184
         "DuckDB" : 0.9447808265686036
```
# query_4
```sql
 SELECT COUNT(DISTINCT payment_type) FROM file('nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 7.442264556884766
         "DuckDB" : 2.271575689315796
```
# query_5
```sql
 SELECT MIN(pickup_date), MAX(pickup_date) FROM file('nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet');
```

```mermaid
     pie showData
         "ClickHouse" : 2.941192150115967
         "DuckDB" : 0.5450942516326904
```
# query_6
```sql
 SELECT id, COUNT(*) FROM file('nyc_taxi_parquet_75b25586_9a7d_11ee_8070_65293045c0d5.parquet') GROUP BY id ORDER BY COUNT(*) DESC LIMIT 10;;
```

```mermaid
     pie showData
         "ClickHouse" : 3.4446396827697754
         "DuckDB" : 0.8681118488311768
```
