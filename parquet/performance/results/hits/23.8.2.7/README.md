# ClickHouse vs DuckDB (Runtime in Seconds)

## Versions
  * ClickHouse: 23.8.2.7
  * DuckDB: 0.8.1


## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0761182308197021
         "DuckDB" : 0.1201701164245605
```
# query_1
```sql
 SELECT COUNT(*) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE AdvEngineID <> 0;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2843554019927978
         "DuckDB" : 0.1381387710571289
```
# query_2
```sql
 SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2998368740081787
         "DuckDB" : 0.1796870231628418
```
# query_3
```sql
 SELECT AVG(UserID) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2738187313079834
         "DuckDB" : 0.1839239597320556
```
# query_4
```sql
 SELECT COUNT(DISTINCT UserID) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.5925347805023193
         "DuckDB" : 1.1639559268951416
```
# query_5
```sql
 SELECT COUNT(DISTINCT SearchPhrase) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.9350404739379884
         "DuckDB" : 1.160755634307861
```
# query_6
```sql
 SELECT MIN(EventDate), MAX(EventDate) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2678117752075195
         "DuckDB" : 0.1352081298828125
```
# query_7
```sql
 SELECT AdvEngineID, COUNT(*) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2763121128082275
         "DuckDB" : 0.1396887302398681
```
# query_8
```sql
 SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) GROUP BY RegionID ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.91864013671875
         "DuckDB" : 1.2516655921936035
```
# query_9
```sql
 SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) GROUP BY RegionID ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.048863410949707
         "DuckDB" : 1.5366559028625488
```
# query_10
```sql
 SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5646145343780518
         "DuckDB" : 0.3765144348144531
```
# query_11
```sql
 SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.598214864730835
         "DuckDB" : 0.4289960861206054
```
# query_12
```sql
 SELECT SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0045535564422607
         "DuckDB" : 0.980966329574585
```
# query_13
```sql
 SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.2528645992279053
         "DuckDB" : 1.545625925064087
```
# query_14
```sql
 SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.1455886363983154
         "DuckDB" : 1.054046630859375
```
# query_15
```sql
 SELECT UserID, COUNT(*) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6893224716186523
         "DuckDB" : 1.1808905601501465
```
# query_16
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.083770751953125
         "DuckDB" : 2.2257089614868164
```
# query_17
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID, SearchPhrase LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.571199893951416
         "DuckDB" : 2.2406346797943115
```
# query_19
```sql
 SELECT UserID FROM file(hits_parquet_8d18d12d_4cc2_11ee_924e_01a4aa584ed2.parquet) WHERE UserID = 435090932899640449;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2909743785858154
         "DuckDB" : 0.192225694656372
```
