# ClickHouse vs DuckDB (Runtime in Seconds)

## Bar Chart
![Bar Chart](bar_chart.png)
# query_0
```sql
 SELECT COUNT(*) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.0598206520080566
         "DuckDB" : 0.1288607120513916
```
# query_1
```sql
 SELECT COUNT(*) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE AdvEngineID <> 0;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2703220844268799
         "DuckDB" : 0.1307125091552734
```
# query_2
```sql
 SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.279958963394165
         "DuckDB" : 0.1713714599609375
```
# query_3
```sql
 SELECT AVG(UserID) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2811939716339111
         "DuckDB" : 0.1794908046722412
```
# query_4
```sql
 SELECT COUNT(DISTINCT UserID) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.522141695022583
         "DuckDB" : 1.0648274421691897
```
# query_5
```sql
 SELECT COUNT(DISTINCT SearchPhrase) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.8747665882110596
         "DuckDB" : 1.1150240898132324
```
# query_6
```sql
 SELECT MIN(EventDate), MAX(EventDate) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet);
```

```mermaid
     pie showData
         "ClickHouse" : 0.2367756366729736
         "DuckDB" : 0.1280946731567382
```
# query_7
```sql
 SELECT AdvEngineID, COUNT(*) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2409629821777343
         "DuckDB" : 0.1307151317596435
```
# query_8
```sql
 SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) GROUP BY RegionID ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.8443126678466797
         "DuckDB" : 1.1555359363555908
```
# query_9
```sql
 SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) GROUP BY RegionID ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.979889154434204
         "DuckDB" : 1.4234943389892578
```
# query_10
```sql
 SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5245816707611084
         "DuckDB" : 0.3497250080108642
```
# query_11
```sql
 SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.5521256923675537
         "DuckDB" : 0.3956503868103027
```
# query_12
```sql
 SELECT SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.9148452281951904
         "DuckDB" : 0.9278545379638672
```
# query_13
```sql
 SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.142998218536377
         "DuckDB" : 1.448188304901123
```
# query_14
```sql
 SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.0950796604156494
         "DuckDB" : 1.0095441341400146
```
# query_15
```sql
 SELECT UserID, COUNT(*) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 0.6299171447753906
         "DuckDB" : 1.116593599319458
```
# query_16
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.8994295597076416
         "DuckDB" : 2.100460290908813
```
# query_17
```sql
 SELECT UserID, SearchPhrase, COUNT(*) FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) GROUP BY UserID, SearchPhrase LIMIT 10;
```

```mermaid
     pie showData
         "ClickHouse" : 1.4762623310089111
         "DuckDB" : 2.0793938636779785
```
# query_19
```sql
 SELECT UserID FROM file(hits_parquet_1760edbd_5ec3_11ee_924e_01a4aa584ed2.parquet) WHERE UserID = 435090932899640449;
```

```mermaid
     pie showData
         "ClickHouse" : 0.2559139728546142
         "DuckDB" : 0.1810007095336914
```
