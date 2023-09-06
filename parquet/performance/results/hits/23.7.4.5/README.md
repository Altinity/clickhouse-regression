# ClickHouse vs DuckDB (Runtime in Seconds)

## Versions:
  * ClickHouse: 23.7.4.5
  * DuckDB: 0.8.1


## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.3401939868927002
         "DuckDB" : 0.1281735897064209
```
# query_1
```sql
 SELECT COUNT(*) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE AdvEngineID <> 0;
```

```mermaid
     pie showData
         "ClickHouse" : 0.259256362915039
         "DuckDB" : 0.1364941596984863
```
# query_2
```sql
 SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2945344448089599
         "DuckDB" : 0.2008278369903564
```
# query_3
```sql
 SELECT AVG(UserID) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2571883201599121
         "DuckDB" : 0.1787335872650146
```
# query_4
```sql
 SELECT COUNT(DISTINCT UserID) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.5850119590759277
         "DuckDB" : 1.148700714111328
```
# query_5
```sql
 SELECT COUNT(DISTINCT SearchPhrase) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 1.017925500869751
         "DuckDB" : 1.4619593620300293
```
# query_6
```sql
 SELECT MIN(EventDate), MAX(EventDate) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2428970336914062
         "DuckDB" : 0.133103609085083
```
# query_7
```sql
 SELECT AdvEngineID, COUNT(*) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2418215274810791
         "DuckDB" : 0.148134708404541
```
# query_8
```sql
 SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) GROUP BY RegionID ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.877164363861084
         "DuckDB" : 1.2547028064727783
```
# query_9
```sql
 SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) GROUP BY RegionID ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0478403568267822
         "DuckDB" : 1.5364441871643066
```
# query_10
```sql
 SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5334362983703613
         "DuckDB" : 0.3780250549316406
```
# query_11
```sql
 SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6164987087249756
         "DuckDB" : 0.428917646408081
```
# query_12
```sql
 SELECT SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.055638313293457
         "DuckDB" : 1.1222264766693115
```
# query_13
```sql
 SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.3221850395202637
         "DuckDB" : 1.5536983013153076
```
# query_14
```sql
 SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.1991894245147705
         "DuckDB" : 1.0635216236114502
```
# query_15
```sql
 SELECT UserID, COUNT(*) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6847498416900635
         "DuckDB" : 1.261681079864502
```
# query_16
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.104289531707764
         "DuckDB" : 2.314905166625977
```
# query_17
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID, SearchPhrase LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.7720067501068115
         "DuckDB" : 2.1794605255126958
```
# query_19
```sql
 SELECT UserID FROM file(hits_parquet_76ec142b_4c10_11ee_924e_01a4aa584ed2.parquet) WHERE UserID = 435090932899640449;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2697896957397461
         "DuckDB" : 0.1872987747192382
```
