# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0918262004852294
         "DuckDB" : 0.1925966739654541
```
# query_1
```sql
 SELECT COUNT(*) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE AdvEngineID <> 0;
```

```mermaid
     pie showData
         "ClickHouse" : 0.3464953899383545
         "DuckDB" : 0.2025656700134277
```
# query_2
```sql
 SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.3767292499542236
         "DuckDB" : 0.2146461009979248
```
# query_3
```sql
 SELECT AVG(UserID) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.419339656829834
         "DuckDB" : 0.2645909786224365
```
# query_4
```sql
 SELECT COUNT(DISTINCT UserID) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.8762063980102539
         "DuckDB" : 0.7902181148529053
```
# query_5
```sql
 SELECT COUNT(DISTINCT SearchPhrase) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 1.174343824386597
         "DuckDB" : 1.0332486629486084
```
# query_6
```sql
 SELECT MIN(EventDate), MAX(EventDate) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.3725993633270263
         "DuckDB" : 0.1938905715942382
```
# query_7
```sql
 SELECT AdvEngineID, COUNT(*) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4544603824615478
         "DuckDB" : 0.1753280162811279
```
# query_8
```sql
 SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) GROUP BY RegionID ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.2795648574829102
         "DuckDB" : 0.9281606674194336
```
# query_9
```sql
 SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) GROUP BY RegionID ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.577169418334961
         "DuckDB" : 1.0843982696533203
```
# query_10
```sql
 SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.7234306335449219
         "DuckDB" : 0.3541483879089355
```
# query_11
```sql
 SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8172826766967773
         "DuckDB" : 0.4329104423522949
```
# query_12
```sql
 SELECT SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.2939412593841553
         "DuckDB" : 0.9662575721740724
```
# query_13
```sql
 SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.650658369064331
         "DuckDB" : 1.4755356311798096
```
# query_14
```sql
 SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.5538649559020996
         "DuckDB" : 1.0770988464355469
```
# query_15
```sql
 SELECT UserID, COUNT(*) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9745876789093018
         "DuckDB" : 0.995509147644043
```
# query_16
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.728953123092652
         "DuckDB" : 1.9807538986206052
```
# query_17
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) GROUP BY UserID, SearchPhrase LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.0478687286376958
         "DuckDB" : 1.7957656383514404
```
# query_19
```sql
 SELECT UserID FROM file(hits_parquet_49c6d592_99cb_11ee_9042_dfb3f6149fdb.parquet) WHERE UserID = 435090932899640449;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4431614875793457
         "DuckDB" : 0.2546083927154541
```
