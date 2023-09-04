# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file(ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet) GROUP BY Year, Month);
```

```mermaid
     pie showData
         "ClickHouse" : 0.9405548572540284
         "DuckDB" : 0.468574047088623
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file(ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet) WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5309123992919922
         "DuckDB" : 0.3770914077758789
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6388671398162842
         "DuckDB" : 0.3282647132873535
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0202176570892334
         "DuckDB" : 0.5314204692840576
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8046214580535889
         "DuckDB" : 0.4115524291992187
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.8255805969238281
         "DuckDB" : 0.3291332721710205
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0619726181030271
         "DuckDB" : 0.5334749221801758
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6664388179779053
         "DuckDB" : 0.6474573612213135
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.1643035411834717
         "DuckDB" : 0.8073527812957764
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_9bd02b3a_45b9_11ee_9394_5d3e96bc1319.parquet') GROUP BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5149374008178711
         "DuckDB" : 0.3691968917846679
```
