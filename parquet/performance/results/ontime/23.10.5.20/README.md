# ClickHouse vs DuckDB (Runtime in Seconds)

## Versions
  * ClickHouse: 23.10.5.20-alpine
  * DuckDB: 0.9.2

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') GROUP BY Year, Month ORDER BY Year ASC, Month ASC);
```

```mermaid
     pie showData
         "ClickHouse" : 0.696833610534668
         "DuckDB" : 0.2592790126800537
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4882149696350097
         "DuckDB" : 0.2476141452789306
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4863250255584717
         "DuckDB" : 0.2481269836425781
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8516449928283691
         "DuckDB" : 0.4794855117797851
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8539330959320068
         "DuckDB" : 0.3472535610198974
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.8321449756622314
         "DuckDB" : 0.2640671730041504
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.123063325881958
         "DuckDB" : 0.4475376605987549
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6227166652679443
         "DuckDB" : 0.4405481815338135
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC, DestCityName ASC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.837221622467041
         "DuckDB" : 0.6438937187194824
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_81aa1212_935b_11ee_9cb0_3b79d3d65d52.parquet') GROUP BY Year ORDER BY Year ASC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4962468147277832
         "DuckDB" : 0.2164168357849121
```
