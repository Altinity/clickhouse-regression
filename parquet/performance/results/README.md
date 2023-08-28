# ClickHouse vs DuckDB (Runtime in Seconds)

# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file(ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet) GROUP BY Year, Month);
```

```mermaid
     pie showData
         "ClickHouse" : 0.060375690460205
         "DuckDB" : 0.0269708633422851
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file(ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet) WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.032463788986206
         "DuckDB" : 0.0139660835266113
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.031074047088623
         "DuckDB" : 0.0143713951110839
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.047696828842163
         "DuckDB" : 0.0157861709594726
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0450506210327148
         "DuckDB" : 0.015230655670166
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.0431509017944335
         "DuckDB" : 0.0149662494659423
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0433657169342041
         "DuckDB" : 0.0153958797454833
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0352249145507812
         "DuckDB" : 0.0390608310699462
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0591697692871093
         "DuckDB" : 0.0162482261657714
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_0735150d_45b0_11ee_9778_5ddce775f86b.parquet') GROUP BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0318517684936523
         "DuckDB" : 0.0232222080230712
```
