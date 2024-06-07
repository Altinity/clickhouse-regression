# Bloom Filter Performance Report

## 10M_rows_10_row_groups.parquet
|    | file                           | condition                | filter               |   rows_skipped |    elapsed |
|---:|:-------------------------------|:-------------------------|:---------------------|---------------:|-----------:|
| 44 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 | 0.00300995 |
| 45 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       10000000 | 0.0837116  |
| 46 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 | 0.00272346 |
| 47 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       10000000 | 0.0770409  |
| 48 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 | 0.00274965 |
| 49 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       10000000 | 0.074277   |
| 50 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 | 0.00274385 |
| 51 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       10000000 | 0.0785217  |
| 52 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 | 0.0102825  |
| 53 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       10000000 | 0.0759541  |
| 54 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 | 0.00242091 |
| 55 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       10000000 | 0.0690834  |
| 56 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 | 0.00289974 |
| 57 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       10000000 | 0.0708569  |
| 58 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 | 0.00266039 |
| 59 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       10000000 | 0.0721974  |
| 60 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 | 0.00292691 |
| 61 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       10000000 | 0.068378   |
| 62 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 | 0.00272193 |
| 63 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       10000000 | 0.0684855  |
| 64 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 | 0.00256339 |
| 65 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       10000000 | 0.0693764  |

## few_and_large_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |   elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|----------:|
|  0 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       90000000 |   1.51282 |
|  1 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       90000000 |   1.55398 |
|  2 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       90000000 |   1.47117 |
|  3 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       90000000 |   1.51695 |
|  4 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       90000000 |   1.63447 |
|  5 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       90000000 |   1.5809  |
|  6 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       90000000 |   1.57301 |
|  7 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       90000000 |   1.55555 |
|  8 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       90000000 |   1.56745 |
|  9 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       90000000 |   1.6037  |
| 10 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       90000000 |   1.63883 |
| 11 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       90000000 |   1.60568 |
| 12 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       90000000 |   1.50469 |
| 13 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       90000000 |   1.50339 |
| 14 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       90000000 |   1.50247 |
| 15 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       90000000 |   1.48417 |
| 16 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       90000000 |   1.49949 |
| 17 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       90000000 |   1.51816 |
| 18 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       90000000 |   1.60621 |
| 19 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       90000000 |   1.61734 |
| 20 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       90000000 |   1.59982 |
| 21 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       90000000 |   1.51985 |

## few_and_small_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |    elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-----------:|
| 22 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 | 0.00342516 |
| 23 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |            900 | 0.00308307 |
| 24 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 | 0.00241001 |
| 25 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |            900 | 0.00301107 |
| 26 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 | 0.00245583 |
| 27 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |            900 | 0.00994526 |
| 28 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 | 0.0023658  |
| 29 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |            900 | 0.00271543 |
| 30 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 | 0.0102832  |
| 31 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |            900 | 0.00262827 |
| 32 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 | 0.0105986  |
| 33 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |            900 | 0.00260012 |
| 34 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 | 0.00235819 |
| 35 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |            900 | 0.00262589 |
| 36 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 | 0.00250618 |
| 37 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |            900 | 0.00271089 |
| 38 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 | 0.00334498 |
| 39 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |            900 | 0.00273408 |
| 40 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 | 0.00243194 |
| 41 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |            900 | 0.00282173 |
| 42 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 | 0.00273058 |
| 43 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |            900 | 0.00281977 |

## lots_of_row_groups_large.parquet
|    | file                             | condition                | filter               |   rows_skipped |   elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|----------:|
| 66 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |  0.124933 |
| 67 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       90000000 |  1.62397  |
| 68 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |  0.115465 |
| 69 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       90000000 |  1.63701  |
| 70 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |  0.115299 |
| 71 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       90000000 |  1.6385   |
| 72 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |  0.116443 |
| 73 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       90000000 |  1.62963  |
| 74 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |  0.114723 |
| 75 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       90000000 |  1.65713  |
| 76 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |  0.116301 |
| 77 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       90000000 |  1.65631  |
| 78 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |         900000 |  0.133057 |
| 79 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       90000000 |  1.65482  |
| 80 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |  0.118978 |
| 81 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       90000000 |  1.72747  |
| 82 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |  0.114326 |
| 83 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       90000000 |  1.6794   |
| 84 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |  0.116276 |
| 85 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       90000000 |  1.63895  |
| 86 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |  0.114894 |
| 87 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       90000000 |  1.65017  |

## lots_of_row_groups_small.parquet
|     | file                             | condition                | filter               |   rows_skipped |   elapsed |
|----:|:---------------------------------|:-------------------------|:---------------------|---------------:|----------:|
|  88 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 | 0.126463  |
|  89 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |           9000 | 0.0169976 |
|  90 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 | 0.119271  |
|  91 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |           9000 | 0.0172989 |
|  92 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 | 0.1177    |
|  93 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |           9000 | 0.0160487 |
|  94 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 | 0.115923  |
|  95 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |           9000 | 0.0174199 |
|  96 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 | 0.116365  |
|  97 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |           9000 | 0.0181109 |
|  98 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 | 0.116721  |
|  99 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |           9000 | 0.015578  |
| 100 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 | 0.11663   |
| 101 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |           9000 | 0.016583  |
| 102 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 | 0.116879  |
| 103 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |           9000 | 0.0187724 |
| 104 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 | 0.118441  |
| 105 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |           9000 | 0.0176816 |
| 106 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 | 0.11455   |
| 107 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |           9000 | 0.0173077 |
| 108 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 | 0.117262  |
| 109 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |           9000 | 0.0159654 |
