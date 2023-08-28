# ClickHouse vs DuckDB (Runtime in Seconds)

# query_0
```sql 
SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file(ontime_parquet_34fc0f60_459e_11ee_9394_5d3e96bc1319.parquet) GROUP BY Year, Month);
```

```mermaid
     pie showData
         "ClickHouse" : 2.409494400024414
         "DuckDB" : 0.6034212112426758
```
# query_1
```sql 
SELECT DayOfWeek, count(*) AS c FROM {filename} WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;        
```

```mermaid
     pie showData
         "ClickHouse" : 1.700148582458496
         "DuckDB" : 0.4127607345581054
```
# query_2
```sql
SELECT DayOfWeek, count(*) AS c FROM file('{filename}') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
 ```

```mermaid
     pie showData
         "ClickHouse" : 1.3757545948028564
         "DuckDB" : 0.3804309368133545
```
# query_3
```sql
SELECT Origin, count(*) AS c FROM file('{filename}') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
 ```

```mermaid
     pie showData
         "ClickHouse" : 2.139869451522827
         "DuckDB" : 0.780264139175415
```
# query_4
```
SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('{filename}') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.8065414428710935
         "DuckDB" : 0.4958271980285644
```
# query_5
```sql
SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('{filename}') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC;
 ```

```mermaid
     pie showData
         "ClickHouse" : 1.8051981925964355
         "DuckDB" : 0.4003968238830566
```
# query_6
```sql
SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('{filename}') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
 ```

```mermaid
     pie showData
         "ClickHouse" : 2.236374616622925
         "DuckDB" : 0.7676131725311279
```
# query_7
```sql
SELECT Year, avg(DepDelay>10)*100 FROM file('{filename}') GROUP BY Year ORDER BY Year;
 ```

```mermaid
     pie showData
         "ClickHouse" : 2.3221664428710938
         "DuckDB" : 0.8610355854034424
```
# query_8
```sql
SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('{filename}') 
 ```

```mermaid
     pie showData
         "ClickHouse" : 4.8245768547058105
         "DuckDB" : 0.9731850624084472
```
# query_9
```sql 
SELECT Year, count(*) AS c1 FROM file('{filename}') GROUP BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 1.3513524532318115
         "DuckDB" : 0.4265286922454834
```
