# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') GROUP BY Year, Month ORDER BY Year ASC, Month ASC);
```

```mermaid
     pie showData
         "ClickHouse" : 0.8731534481048584
         "DuckDB" : 0.3035969734191894
```
# query_1
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.7244930267333984
         "DuckDB" : 0.3087160587310791
```
# query_2
```sql
 SELECT DayOfWeek, count(*) AS c FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6040854454040527
         "DuckDB" : 0.3097789287567138
```
# query_3
```sql
 SELECT Origin, count(*) AS c FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9281024932861328
         "DuckDB" : 0.6045033931732178
```
# query_4
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9184067249298096
         "DuckDB" : 0.4469466209411621
```
# query_5
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC
```

```mermaid
     pie showData
         "ClickHouse" : 1.0508229732513428
         "DuckDB" : 0.3337762355804443
```
# query_6
```sql
 SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 1.238755702972412
         "DuckDB" : 0.5465166568756104
```
# query_7
```sql
 SELECT Year, avg(DepDelay>10)*100 FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') GROUP BY Year ORDER BY Year;
```

```mermaid
     pie showData
         "ClickHouse" : 0.77567458152771
         "DuckDB" : 0.5094091892242432
```
# query_8
```sql
 SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC, DestCityName ASC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.113819360733032
         "DuckDB" : 0.7720577716827393
```
# query_9
```sql
 SELECT Year, count(*) AS c1 FROM file('ontime_parquet_2a8988cf_9a7b_11ee_8070_65293045c0d5.parquet') GROUP BY Year ORDER BY Year ASC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6354079246520996
         "DuckDB" : 0.2873151302337646
```
