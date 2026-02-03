# Testing namespace filter 

The `namespaces` database setting limits which catalog namespaces are visible to ClickHouse. You pass a comma-separated list of allowed namespace patterns; only tables in matching namespaces are visible. Supported catalog types: `rest`, `glue`, `unity`.

For nested namespaces (e.g. REST catalog): an exact pattern like `ns1` includes only tables in that namespace (e.g. `ns1.table1`, `ns1.table2`). A wildcard pattern `ns1.*` includes tables from all nested namespaces (e.g. `ns1.ns11.table1`) but **not** tables in the parent namespace—so `ns1.table1` is not included in `ns1.*`; use `namespaces='ns1,ns1.*'` to include both. However, AWS Glue only supports single-level namespaces.

**Tested catalogs:** The full test (14 nested namespaces, wildcards, filter sampling) runs for **REST** only. For **Glue**, only single-level namespace filtering is tested (nested namespaces are not supported).


Setup(14 namespaces and two tables in each namespace):
1. ns1
   - table1
   - table2
2. ns1.ns11
   - table1
   - table2
3. ns1.ns12
   - table1
   - table2
4. ns1.ns11.ns111
   - table1
   - table2
5. ns1.ns11.ns112
   - table1
   - table2
6. ns1.ns12.ns121
   - table1
   - table2
7. ns1.ns12.ns122
   - table1
   - table2
8. ns2
   - table1
   - table2
9. ns2.ns21
   - table1
   - table2
10. ns2.ns22
   - table1
   - table2
11. ns2.ns21.ns211
   - table1
   - table2
12. ns2.ns21.ns212
   - table1
   - table2
13. ns2.ns22.ns221
   - table1
   - table2
14. ns2.ns22.ns222
   - table1
   - table2

---

## How many different filters? 

**Filter primitives:** For each of the 14 namespaces we have two options:

- **Exact:** `ns` (only tables in that namespace, e.g. `ns1.table1`, `ns1.table2` for `ns1`; or `ns1.ns11` for tables in that nested namespace).
- **Wildcard:** `ns.*` (tables in all nested namespaces and their descendants, but not in the parent—e.g. `ns1.*` includes `ns1.ns11.table1` but not `ns1.table1`).

So there are **14 × 2 = 28** distinct filter primitives.

**A filter** is a subset of these 28 primitives (we allow 0, 1, 2, … up to 28 of them; order in the setting does not change semantics).

| Size *k* | Number of filters | Formula |
|----------|-------------------|--------|
| 0 | 1 | C(28,0) |
| 1 | 28 | C(28,1) |
| 2 | 378 | C(28,2) |
| 3 | 3,276 | C(28,3) |
| 4 | 20,475 | C(28,4) |
| 5 | 98,280 | C(28,5) |
| 6 | 376,740 | C(28,6) |
| 7 | 1,184,040 | C(28,7) |
| 8 | 3,108,105 | C(28,8) |
| 9 | 6,906,900 | C(28,9) |
| 10 | 13,123,110 | C(28,10) |
| … | … | C(28,*k*) |
| 28 | 1 | C(28,28) |

**Total number of different filters:**

$$
\sum_{k=0}^{28} \binom{28}{k} = 2^{28} = 268{,}435{,}456
$$

**If we only use filters of size 0..5** (e.g. for sampling in tests):

$$
\sum_{k=0}^{5} \binom{28}{k} = 1 + 28 + 378 + 3{,}276 + 20{,}475 + 98{,}280 = 122{,}438
$$

**If we only use filters of size 0..6:**

$$
\sum_{k=0}^{6} \binom{28}{k} = 122{,}438 + 376{,}740 = 499{,}178
$$

---

## Test setup

Create all possible combinations of length 0..5 from the list of 28 primitives + include invalid namespace paths.
Run test for random smaple of 100 filters.

Check that:
- all tables from the allowed namespaces are visible in `system.tables` (SHOW TABLES FROM database)
- all tables from the filtered namespaces are not visible in `system.tables` (SHOW TABLES FROM database)
- select works for allowed namespaces and fails for filtered namespaces
- drop table works for allowed namespaces and fails for filtered namespaces
- everything works after detaching/attaching DataLakeCatalog database
- when namespace filter is not specified, all tables are visible
- join works only if both tables are from allowed namespaces



