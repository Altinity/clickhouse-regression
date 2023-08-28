# ClickHouse vs DuckDB (Runtime in Seconds)

# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file(ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet) GROUP BY Year, Month);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0544080734252929
         "DuckDB" : 0.0271315574645996
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file(ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet) WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0334150791168212
         "DuckDB" : 0.0141968727111816
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0333015918731689
         "DuckDB" : 0.0149505138397216
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0413005352020263
         "DuckDB" : 0.0149910449981689
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0466895103454589
         "DuckDB" : 0.0167860984802246
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.0469555854797363
         "DuckDB" : 0.0153460502624511
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0466554164886474
         "DuckDB" : 0.0763881206512451
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0360302925109863
         "DuckDB" : 0.0390093326568603
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0627272129058837
         "DuckDB" : 0.0170352458953857
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_5dc41c59_45b8_11ee_9778_5ddce775f86b.parquet') GROUP BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.0329434871673584
         "DuckDB" : 0.0239274501800537
```
