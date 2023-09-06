# ClickHouse vs DuckDB (Runtime in Seconds)

## Versions:
  * ClickHouse: 23.8.2.7
  * DuckDB: 0.8.1

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file(ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet) GROUP BY Year, Month);
```

```mermaid
     pie showData
         "ClickHouse" : 0.7671363353729248
         "DuckDB" : 0.5341982841491699
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file(ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet) WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5556008815765381
         "DuckDB" : 0.3645501136779785
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5830984115600586
         "DuckDB" : 0.3542814254760742
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9355881214141846
         "DuckDB" : 0.5594949722290039
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0176420211791992
         "DuckDB" : 0.4042205810546875
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.9654214382171632
         "DuckDB" : 0.2842752933502197
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.2400250434875488
         "DuckDB" : 0.546771764755249
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6762428283691406
         "DuckDB" : 0.730273962020874
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.061671018600464
         "DuckDB" : 0.8572335243225098
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_9f6790d3_4cc4_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5620408058166504
         "DuckDB" : 0.450514554977417
```
