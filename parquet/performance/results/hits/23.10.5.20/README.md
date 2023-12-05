# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0701415538787841
         "DuckDB" : 0.1132433414459228
```
# query_1
```sql
 SELECT COUNT(*) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE AdvEngineID <> 0;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2387185096740722
         "DuckDB" : 0.1229314804077148
```
# query_2
```sql
 SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2595949172973633
         "DuckDB" : 0.1471397876739502
```
# query_3
```sql
 SELECT AVG(UserID) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2944226264953613
         "DuckDB" : 0.1734583377838134
```
# query_4
```sql
 SELECT COUNT(DISTINCT UserID) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.5360672473907471
         "DuckDB" : 0.591355562210083
```
# query_5
```sql
 SELECT COUNT(DISTINCT SearchPhrase) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.8988547325134277
         "DuckDB" : 0.7911076545715332
```
# query_6
```sql
 SELECT MIN(EventDate), MAX(EventDate) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2554836273193359
         "DuckDB" : 0.1205921173095703
```
# query_7
```sql
 SELECT AdvEngineID, COUNT(*) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2517809867858886
         "DuckDB" : 0.1231331825256347
```
# query_8
```sql
 SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) GROUP BY RegionID ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8727848529815674
         "DuckDB" : 0.6876447200775146
```
# query_9
```sql
 SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) GROUP BY RegionID ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.060654640197754
         "DuckDB" : 0.8834805488586426
```
# query_10
```sql
 SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5224864482879639
         "DuckDB" : 0.2728536128997803
```
# query_11
```sql
 SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5651447772979736
         "DuckDB" : 0.2900390625
```
# query_12
```sql
 SELECT SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.919297695159912
         "DuckDB" : 0.7395303249359131
```
# query_13
```sql
 SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.1385071277618408
         "DuckDB" : 1.0441563129425049
```
# query_14
```sql
 SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0730323791503906
         "DuckDB" : 0.8143675327301025
```
# query_15
```sql
 SELECT UserID, COUNT(*) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6336014270782471
         "DuckDB" : 0.7112445831298828
```
# query_16
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.888688087463379
         "DuckDB" : 1.4802119731903076
```
# query_17
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) GROUP BY UserID, SearchPhrase LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.5249714851379397
         "DuckDB" : 1.4944953918457031
```
# query_19
```sql
 SELECT UserID FROM file(hits_parquet_c3bde864_935d_11ee_9cb0_3b79d3d65d52.parquet) WHERE UserID = 435090932899640449;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2620744705200195
         "DuckDB" : 0.1718232631683349
```
