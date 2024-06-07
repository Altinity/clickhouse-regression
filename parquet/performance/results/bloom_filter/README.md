# Bloom Filter Performance Report

## 10M_rows_10_row_groups.parquet
|    | file                           | condition                | filter               |   rows_skipped |   total_rows |    elapsed |
|---:|:-------------------------------|:-------------------------|:---------------------|---------------:|-------------:|-----------:|
| 44 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       10000000 |     10000000 | 0.0191311  |
| 45 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |     10000000 | 0.0786987  |
| 46 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       10000000 |     10000000 | 0.0043838  |
| 47 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |     10000000 | 0.0712366  |
| 48 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       10000000 |     10000000 | 0.0044338  |
| 49 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |     10000000 | 0.076776   |
| 50 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       10000000 |     10000000 | 0.00463544 |
| 51 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |     10000000 | 0.0739162  |
| 52 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       10000000 |     10000000 | 0.00430753 |
| 53 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |     10000000 | 0.0710788  |
| 54 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       10000000 |     10000000 | 0.00430488 |
| 55 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |     10000000 | 0.0690794  |
| 56 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       10000000 |     10000000 | 0.00450735 |
| 57 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |     10000000 | 0.0724526  |
| 58 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       10000000 |     10000000 | 0.00417351 |
| 59 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |     10000000 | 0.071301   |
| 60 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       10000000 |     10000000 | 0.00433952 |
| 61 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |     10000000 | 0.090507   |
| 62 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       10000000 |     10000000 | 0.00450015 |
| 63 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |     10000000 | 0.0680578  |
| 64 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       10000000 |     10000000 | 0.00417316 |
| 65 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |     10000000 | 0.070043   |

## few_and_large_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
|  0 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |     90000000 |   1.65719 |
|  1 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |     90000000 |   1.61344 |
|  2 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |     90000000 |   1.63114 |
|  3 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |     90000000 |   1.63639 |
|  4 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |     90000000 |   1.86298 |
|  5 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |     90000000 |   1.61988 |
|  6 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |     90000000 |   1.59852 |
|  7 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |     90000000 |   1.65801 |
|  8 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |     90000000 |   1.58641 |
|  9 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |     90000000 |   1.62501 |
| 10 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |     90000000 |   1.58675 |
| 11 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |     90000000 |   1.63473 |
| 12 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 |     90000000 |   1.58554 |
| 13 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |     90000000 |   1.57994 |
| 14 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |     90000000 |   1.66986 |
| 15 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |     90000000 |   1.65705 |
| 16 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |     90000000 |   1.59291 |
| 17 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |     90000000 |   1.61136 |
| 18 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |     90000000 |   1.59273 |
| 19 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |     90000000 |   1.58058 |
| 20 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |     90000000 |   1.60942 |
| 21 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |     90000000 |   1.63161 |

## few_and_small_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |   total_rows |    elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|-----------:|
| 22 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |            900 |          900 | 0.00390748 |
| 23 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |          900 | 0.00322702 |
| 24 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |            900 |          900 | 0.00311618 |
| 25 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |          900 | 0.00266319 |
| 26 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |            900 |          900 | 0.0031562  |
| 27 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |          900 | 0.00269077 |
| 28 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |            900 |          900 | 0.00348759 |
| 29 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |          900 | 0.00266745 |
| 30 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |            900 |          900 | 0.00365926 |
| 31 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |          900 | 0.00278834 |
| 32 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |            900 |          900 | 0.00310689 |
| 33 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |          900 | 0.00323267 |
| 34 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |            900 |          900 | 0.00310102 |
| 35 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |          900 | 0.00269797 |
| 36 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |            900 |          900 | 0.00330664 |
| 37 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |          900 | 0.00286342 |
| 38 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |            900 |          900 | 0.00318015 |
| 39 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |          900 | 0.00282927 |
| 40 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |            900 |          900 | 0.00318637 |
| 41 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |          900 | 0.00281761 |
| 42 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |            900 |          900 | 0.00300331 |
| 43 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |          900 | 0.0034598  |

## lots_of_row_groups_large.parquet
|    | file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
| 66 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       90000000 |     90000000 |  0.596177 |
| 67 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |     90000000 |  1.72671  |
| 68 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       90000000 |     90000000 |  0.571039 |
| 69 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |     90000000 |  1.71058  |
| 70 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       90000000 |     90000000 |  0.582764 |
| 71 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |     90000000 |  1.69689  |
| 72 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       90000000 |     90000000 |  0.590549 |
| 73 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |     90000000 |  1.70266  |
| 74 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       90000000 |     90000000 |  0.580083 |
| 75 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |     90000000 |  1.74237  |
| 76 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       90000000 |     90000000 |  0.570218 |
| 77 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |     90000000 |  1.73716  |
| 78 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       89100000 |     90000000 |  0.601269 |
| 79 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |     90000000 |  1.72916  |
| 80 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       90000000 |     90000000 |  0.573069 |
| 81 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |     90000000 |  1.70394  |
| 82 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       90000000 |     90000000 |  0.581462 |
| 83 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |     90000000 |  1.7167   |
| 84 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       90000000 |     90000000 |  0.574466 |
| 85 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |     90000000 |  1.76373  |
| 86 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       90000000 |     90000000 |  0.575962 |
| 87 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |     90000000 |  1.76032  |

## lots_of_row_groups_small.parquet
|     | file                             | condition                | filter               |   rows_skipped |   total_rows |   elapsed |
|----:|:---------------------------------|:-------------------------|:---------------------|---------------:|-------------:|----------:|
|  88 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |           9000 |         9000 | 0.573369  |
|  89 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |              0 |         9000 | 0.0203101 |
|  90 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |           9000 |         9000 | 0.561461  |
|  91 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |              0 |         9000 | 0.0200678 |
|  92 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |           9000 |         9000 | 0.563954  |
|  93 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |              0 |         9000 | 0.0221093 |
|  94 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |           9000 |         9000 | 0.549918  |
|  95 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |              0 |         9000 | 0.0205565 |
|  96 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |           9000 |         9000 | 0.554257  |
|  97 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |              0 |         9000 | 0.019628  |
|  98 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |           9000 |         9000 | 0.56869   |
|  99 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |              0 |         9000 | 0.0241289 |
| 100 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |           9000 |         9000 | 0.54585   |
| 101 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |              0 |         9000 | 0.0209206 |
| 102 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |           9000 |         9000 | 0.55451   |
| 103 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |              0 |         9000 | 0.0215541 |
| 104 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |           9000 |         9000 | 0.553686  |
| 105 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |              0 |         9000 | 0.020044  |
| 106 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |           9000 |         9000 | 0.545463  |
| 107 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |              0 |         9000 | 0.0207261 |
| 108 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |           9000 |         9000 | 0.568685  |
| 109 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |              0 |         9000 | 0.0190819 |
