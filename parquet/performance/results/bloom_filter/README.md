# Bloom Filter Performance Report

## 10M_rows_10_row_groups.parquet
|    | file                           | condition                | filter               |   rows_skipped |   total_rows |    elapsed |
|---:|:-------------------------------|:-------------------------|:---------------------|---------------:|-------------:|-----------:|
| 44 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |     10000000 | 0.00894757 |
| 45 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       10000000 |     10000000 | 0.0940332  |
| 46 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |     10000000 | 0.00636743 |
| 47 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       10000000 |     10000000 | 0.0722231  |
| 48 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |     10000000 | 0.00469829 |
| 49 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       10000000 |     10000000 | 0.0722411  |
| 50 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |     10000000 | 0.00511971 |
| 51 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       10000000 |     10000000 | 0.0909525  |
| 52 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |     10000000 | 0.00431584 |
| 53 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       10000000 |     10000000 | 0.072355   |
| 54 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |     10000000 | 0.00434867 |
| 55 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       10000000 |     10000000 | 0.0838078  |
| 56 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 |     10000000 | 0.0044403  |
| 57 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       10000000 |     10000000 | 0.0791581  |
| 58 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |     10000000 | 0.00432757 |
| 59 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       10000000 |     10000000 | 0.072759   |
| 60 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |     10000000 | 0.026142   |
| 61 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       10000000 |     10000000 | 0.100487   |
| 62 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |     10000000 | 0.00321004 |
| 63 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       10000000 |     10000000 | 0.0855112  |
| 64 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |     10000000 | 0.00281314 |
| 65 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       10000000 |     10000000 | 0.0777141  |

## few_and_large_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
|  0 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       90000000 |     90000000 |   1.57244 |
|  1 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       90000000 |     90000000 |   1.48293 |
|  2 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       90000000 |     90000000 |   1.51319 |
|  3 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       90000000 |     90000000 |   1.53587 |
|  4 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       90000000 |     90000000 |   1.55952 |
|  5 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       90000000 |     90000000 |   1.53962 |
|  6 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       90000000 |     90000000 |   1.61341 |
|  7 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       90000000 |     90000000 |   1.45597 |
|  8 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       90000000 |     90000000 |   1.49622 |
|  9 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       90000000 |     90000000 |   1.54377 |
| 10 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       90000000 |     90000000 |   1.64901 |
| 11 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       90000000 |     90000000 |   1.66638 |
| 12 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       90000000 |     90000000 |   1.66618 |
| 13 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       90000000 |     90000000 |   1.61846 |
| 14 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       90000000 |     90000000 |   1.67642 |
| 15 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       90000000 |     90000000 |   1.75475 |
| 16 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       90000000 |     90000000 |   1.58376 |
| 17 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       90000000 |     90000000 |   1.49858 |
| 18 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       90000000 |     90000000 |   1.52152 |
| 19 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       90000000 |     90000000 |   1.54874 |
| 20 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       90000000 |     90000000 |   1.53243 |
| 21 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       90000000 |     90000000 |   1.56116 |

## few_and_small_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |   total_rows |    elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|-----------:|
| 22 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |          900 | 0.00419201 |
| 23 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |            900 |          900 | 0.00335266 |
| 24 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |          900 | 0.00304278 |
| 25 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |            900 |          900 | 0.00272472 |
| 26 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |          900 | 0.00279016 |
| 27 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |            900 |          900 | 0.00288933 |
| 28 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |          900 | 0.0105766  |
| 29 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |            900 |          900 | 0.00269455 |
| 30 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |          900 | 0.00275727 |
| 31 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |            900 |          900 | 0.00281893 |
| 32 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |          900 | 0.012723   |
| 33 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |            900 |          900 | 0.0027375  |
| 34 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 |          900 | 0.00286412 |
| 35 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |            900 |          900 | 0.00488002 |
| 36 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |          900 | 0.00298292 |
| 37 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |            900 |          900 | 0.00293585 |
| 38 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |          900 | 0.00288745 |
| 39 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |            900 |          900 | 0.0106778  |
| 40 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |          900 | 0.00302182 |
| 41 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |            900 |          900 | 0.0107744  |
| 42 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |          900 | 0.00282305 |
| 43 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |            900 |          900 | 0.0107422  |

## lots_of_row_groups_large.parquet
|    | file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
| 66 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |     90000000 |  0.143951 |
| 67 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       90000000 |     90000000 |  1.68535  |
| 68 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |     90000000 |  0.12833  |
| 69 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       90000000 |     90000000 |  1.77697  |
| 70 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |     90000000 |  0.125577 |
| 71 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       90000000 |     90000000 |  1.62882  |
| 72 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |     90000000 |  0.12298  |
| 73 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       90000000 |     90000000 |  1.63701  |
| 74 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |     90000000 |  0.119353 |
| 75 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       90000000 |     90000000 |  1.65198  |
| 76 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |     90000000 |  0.118884 |
| 77 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       90000000 |     90000000 |  1.63989  |
| 78 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |         900000 |     90000000 |  0.136381 |
| 79 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       90000000 |     90000000 |  1.64607  |
| 80 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |     90000000 |  0.119782 |
| 81 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       90000000 |     90000000 |  1.7003   |
| 82 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |     90000000 |  0.118526 |
| 83 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       90000000 |     90000000 |  1.63353  |
| 84 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |     90000000 |  0.11882  |
| 85 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       90000000 |     90000000 |  1.65018  |
| 86 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |     90000000 |  0.121181 |
| 87 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       90000000 |     90000000 |  1.63316  |

## lots_of_row_groups_small.parquet
|     | file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|----:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
|  88 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |         9000 | 0.121196  |
|  89 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |           9000 |         9000 | 0.019831  |
|  90 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |         9000 | 0.117424  |
|  91 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |           9000 |         9000 | 0.0184097 |
|  92 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |         9000 | 0.115795  |
|  93 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |           9000 |         9000 | 0.0191494 |
|  94 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |         9000 | 0.11463   |
|  95 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |           9000 |         9000 | 0.0186766 |
|  96 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |         9000 | 0.118012  |
|  97 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |           9000 |         9000 | 0.0187009 |
|  98 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |         9000 | 0.117642  |
|  99 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |           9000 |         9000 | 0.0177389 |
| 100 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 |         9000 | 0.117308  |
| 101 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |           9000 |         9000 | 0.0178182 |
| 102 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |         9000 | 0.116959  |
| 103 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |           9000 |         9000 | 0.0165666 |
| 104 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |         9000 | 0.116819  |
| 105 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |           9000 |         9000 | 0.0162377 |
| 106 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |         9000 | 0.12132   |
| 107 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |           9000 |         9000 | 0.0169857 |
| 108 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |         9000 | 0.11881   |
| 109 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |           9000 |         9000 | 0.0180275 |
