# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') GROUP BY Year, Month ORDER BY Year ASC, Month ASC);
```

```mermaid
     pie showData
         "ClickHouse" : 1.005176305770874
         "DuckDB" : 0.3052229881286621
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8874452114105225
         "DuckDB" : 0.3213262557983398
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9050502777099608
         "DuckDB" : 0.3316404819488525
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.3835062980651855
         "DuckDB" : 0.6223874092102051
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0712032318115234
         "DuckDB" : 0.4517276287078857
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 1.0868170261383057
         "DuckDB" : 0.3471949100494385
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.4992389678955078
         "DuckDB" : 0.5351767539978027
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9838869571685792
         "DuckDB" : 0.5335574150085449
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC, DestCityName ASC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.4244868755340576
         "DuckDB" : 0.7748916149139404
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_c8273ab0_987b_11ee_9a07_9f7bda011822.parquet') GROUP BY Year ORDER BY Year ASC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.851923942565918
         "DuckDB" : 0.281710147857666
```
