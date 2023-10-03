# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year, Month ORDER BY Year ASC, Month ASC);
```

```mermaid
     pie showData
         "ClickHouse" : 0.731156587600708
         "DuckDB" : 0.511176347732544
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5015225410461426
         "DuckDB" : 0.3359262943267822
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4671626091003418
         "DuckDB" : 0.335578441619873
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8414187431335449
         "DuckDB" : 0.5211935043334961
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9734489917755128
         "DuckDB" : 0.3844003677368164
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.8981578350067139
         "DuckDB" : 0.2761180400848388
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.150712013244629
         "DuckDB" : 0.5277070999145508
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.598792314529419
         "DuckDB" : 0.6866066455841064
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC, DestCityName ASC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.867773532867432
         "DuckDB" : 0.7832396030426025
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_ff4f97f3_61d6_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year ORDER BY Year ASC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.514664888381958
         "DuckDB" : 0.4151873588562011
```
