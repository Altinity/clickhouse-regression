# Bloom Filter Performance Report

## 10M_rows_10_row_groups.parquet
| file                           | condition                | filter               |   rows_skipped |   total_rows |    elapsed |
|:-------------------------------|:-------------------------|:---------------------|---------------:|-------------:|-----------:|
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       10000000 |     10000000 | 0.0028871  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |     10000000 | 0.0786587  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       10000000 |     10000000 | 0.00258734 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |     10000000 | 0.0723596  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       10000000 |     10000000 | 0.00269287 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |     10000000 | 0.0728397  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       10000000 |     10000000 | 0.00245436 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |     10000000 | 0.0689852  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       10000000 |     10000000 | 0.00291524 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |     10000000 | 0.0718978  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       10000000 |     10000000 | 0.00273366 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |     10000000 | 0.0716659  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       10000000 |     10000000 | 0.00265446 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |     10000000 | 0.0834604  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       10000000 |     10000000 | 0.00275573 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |     10000000 | 0.0777444  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       10000000 |     10000000 | 0.00260466 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |     10000000 | 0.0703864  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       10000000 |     10000000 | 0.00287886 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |     10000000 | 0.0762873  |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       10000000 |     10000000 | 0.00336551 |
| 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |     10000000 | 0.0705788  |

## few_and_large_row_groups.parquet
| file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
| few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |     90000000 |   1.54169 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |     90000000 |   1.78121 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |     90000000 |   1.51795 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |     90000000 |   1.46112 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |     90000000 |   1.53778 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |     90000000 |   1.58261 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |     90000000 |   1.76884 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |     90000000 |   1.59048 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |     90000000 |   1.57792 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |     90000000 |   1.629   |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |     90000000 |   1.86707 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |     90000000 |   1.58747 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 |     90000000 |   1.60258 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |     90000000 |   1.61899 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |     90000000 |   1.49163 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |     90000000 |   1.54851 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |     90000000 |   1.58275 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |     90000000 |   1.5213  |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |     90000000 |   1.57707 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |     90000000 |   1.94956 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |     90000000 |   1.53205 |
| few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |     90000000 |   1.57396 |

## few_and_small_row_groups.parquet
| file                             | condition                | filter               |   rows_skipped |   total_rows |    elapsed |
|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|-----------:|
| few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |            900 |          900 | 0.0115726  |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |          900 | 0.00291189 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |            900 |          900 | 0.00242831 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |          900 | 0.00256513 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |            900 |          900 | 0.00256827 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |          900 | 0.0025374  |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |            900 |          900 | 0.00244389 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |          900 | 0.00296993 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |            900 |          900 | 0.00237293 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |          900 | 0.00274651 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |            900 |          900 | 0.00268994 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |          900 | 0.00263756 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |            900 |          900 | 0.00245723 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |          900 | 0.00268882 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |            900 |          900 | 0.00233905 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |          900 | 0.00279707 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |            900 |          900 | 0.00248216 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |          900 | 0.00270097 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |            900 |          900 | 0.00259726 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |          900 | 0.00278345 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |            900 |          900 | 0.00248859 |
| few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |          900 | 0.0127608  |

## lots_of_row_groups_large.parquet
| file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       90000000 |     90000000 |  0.125611 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |     90000000 |  1.63864  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       90000000 |     90000000 |  0.117112 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |     90000000 |  1.64939  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       90000000 |     90000000 |  0.12013  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |     90000000 |  1.78949  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       90000000 |     90000000 |  0.127329 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |     90000000 |  1.70522  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       90000000 |     90000000 |  0.117799 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |     90000000 |  1.67792  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       90000000 |     90000000 |  0.118061 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |     90000000 |  1.7308   |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       89100000 |     90000000 |  0.132354 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |     90000000 |  1.65073  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       90000000 |     90000000 |  0.119194 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |     90000000 |  1.65148  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       90000000 |     90000000 |  0.116665 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |     90000000 |  1.64883  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       90000000 |     90000000 |  0.117132 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |     90000000 |  1.65113  |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       90000000 |     90000000 |  0.117954 |
| lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |     90000000 |  1.90944  |

## lots_of_row_groups_small.parquet
| file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |           9000 |         9000 | 0.121259  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |         9000 | 0.0195848 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |           9000 |         9000 | 0.115979  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |         9000 | 0.0178154 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |           9000 |         9000 | 0.115816  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |         9000 | 0.0175223 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |           9000 |         9000 | 0.11157   |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |         9000 | 0.0207873 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |           9000 |         9000 | 0.118069  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |         9000 | 0.0167046 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |           9000 |         9000 | 0.115495  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |         9000 | 0.022709  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |           9000 |         9000 | 0.116198  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |         9000 | 0.0200592 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |           9000 |         9000 | 0.115906  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |         9000 | 0.0165844 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |           9000 |         9000 | 0.1143    |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |         9000 | 0.0185181 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |           9000 |         9000 | 0.114615  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |         9000 | 0.0183448 |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |           9000 |         9000 | 0.117667  |
| lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |         9000 | 0.0165025 |
