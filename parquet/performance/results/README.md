# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file(ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet) GROUP BY Year, Month);
```

```mermaid
     pie showData
         "ClickHouse" : 0.7352383136749268
         "DuckDB" : 0.5942275524139404
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file(ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet) WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5144808292388916
         "DuckDB" : 0.3603942394256592
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5387084484100342
         "DuckDB" : 0.3724365234375
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9649007320404052
         "DuckDB" : 0.6133012771606445
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9510664939880372
         "DuckDB" : 0.4371564388275146
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 0.994737148284912
         "DuckDB" : 0.3032581806182861
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.1486093997955322
         "DuckDB" : 0.5890219211578369
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6709635257720947
         "DuckDB" : 0.765927791595459
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.0357553958892822
         "DuckDB" : 0.85992431640625
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_bbdb54cb_4b6a_11ee_924e_01a4aa584ed2.parquet') GROUP BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5217840671539307
         "DuckDB" : 0.4718611240386963
```
