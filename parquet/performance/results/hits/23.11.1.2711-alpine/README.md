# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.1155531406402587
         "DuckDB" : 0.1821296215057373
```
# query_1
```sql
 SELECT COUNT(*) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE AdvEngineID <> 0;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4384870529174804
         "DuckDB" : 0.2088930606842041
```
# query_2
```sql
 SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.5127604007720947
         "DuckDB" : 0.2442727088928222
```
# query_3
```sql
 SELECT AVG(UserID) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.4789795875549316
         "DuckDB" : 0.2156193256378173
```
# query_4
```sql
 SELECT COUNT(DISTINCT UserID) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.9274821281433104
         "DuckDB" : 0.9061830043792723
```
# query_5
```sql
 SELECT COUNT(DISTINCT SearchPhrase) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 1.2668683528900146
         "DuckDB" : 1.0955448150634766
```
# query_6
```sql
 SELECT MIN(EventDate), MAX(EventDate) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.4770076274871826
         "DuckDB" : 0.2066574096679687
```
# query_7
```sql
 SELECT AdvEngineID, COUNT(*) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5237884521484375
         "DuckDB" : 0.2244637012481689
```
# query_8
```sql
 SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) GROUP BY RegionID ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.5204095840454102
         "DuckDB" : 0.9848055839538574
```
# query_9
```sql
 SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) GROUP BY RegionID ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.6826729774475098
         "DuckDB" : 1.1844520568847656
```
# query_10
```sql
 SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8635084629058838
         "DuckDB" : 0.4077208042144775
```
# query_11
```sql
 SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.942640781402588
         "DuckDB" : 0.443080186843872
```
# query_12
```sql
 SELECT SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.4174933433532717
         "DuckDB" : 1.0830354690551758
```
# query_13
```sql
 SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.7686424255371094
         "DuckDB" : 1.5201301574707031
```
# query_14
```sql
 SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.6296217441558838
         "DuckDB" : 1.1713650226593018
```
# query_15
```sql
 SELECT UserID, COUNT(*) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9743387699127196
         "DuckDB" : 1.0483086109161377
```
# query_16
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.9735636711120605
         "DuckDB" : 2.083003282546997
```
# query_17
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) GROUP BY UserID, SearchPhrase LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 2.137901544570923
         "DuckDB" : 2.0573971271514893
```
# query_19
```sql
 SELECT UserID FROM file(hits_parquet_f0273e19_9879_11ee_9a07_9f7bda011822.parquet) WHERE UserID = 435090932899640449;
```

```mermaid
     pie showData
         "ClickHouse" : 0.4928452968597412
         "DuckDB" : 0.2726624011993408
```
