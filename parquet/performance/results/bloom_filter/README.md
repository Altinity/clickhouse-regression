
## 10M_rows_10_row_groups.parquet
|    | file                           | condition                | filter               |   rows_skipped |    elapsed | query                    |
|---:|:-------------------------------|:-------------------------|:---------------------|---------------:|-----------:|:-------------------------|
| 44 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 | 0.00287837 | WHERE t2 = 'third-99999' |
| 45 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       10000000 | 0.0870331  | WHERE t2 = 'third-99999' |
| 46 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 | 0.00287977 | WHERE t2 = 'third-90000' |
| 47 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       10000000 | 0.0813163  | WHERE t2 = 'third-90000' |
| 48 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 | 0.00279651 | WHERE t2 = 'third-80000' |
| 49 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       10000000 | 0.0745436  | WHERE t2 = 'third-80000' |
| 50 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 | 0.00280406 | WHERE t2 = 'third-70000' |
| 51 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       10000000 | 0.08127    | WHERE t2 = 'third-70000' |
| 52 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 | 0.00281425 | WHERE t2 = 'third-60000' |
| 53 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       10000000 | 0.0917417  | WHERE t2 = 'third-60000' |
| 54 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 | 0.00282242 | WHERE t2 = 'third-50000' |
| 55 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       10000000 | 0.0757989  | WHERE t2 = 'third-50000' |
| 56 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 | 0.00276585 | WHERE t2 = 'third-40000' |
| 57 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       10000000 | 0.0762542  | WHERE t2 = 'third-40000' |
| 58 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 | 0.00273917 | WHERE t2 = 'third-30000' |
| 59 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       10000000 | 0.0783938  | WHERE t2 = 'third-30000' |
| 60 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 | 0.00276159 | WHERE t2 = 'third-20000' |
| 61 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       10000000 | 0.0738126  | WHERE t2 = 'third-20000' |
| 62 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 | 0.00272667 | WHERE t2 = 'third-10000' |
| 63 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       10000000 | 0.0686539  | WHERE t2 = 'third-10000' |
| 64 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 | 0.00266619 | WHERE t2 = 'third-00000' |
| 65 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       10000000 | 0.0727245  | WHERE t2 = 'third-00000' |

## few_and_large_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |   elapsed | query                    |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|----------:|:-------------------------|
|  0 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |       90000000 |   1.54323 | WHERE t2 = 'third-99999' |
|  1 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       90000000 |   1.4708  | WHERE t2 = 'third-99999' |
|  2 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |       90000000 |   1.45345 | WHERE t2 = 'third-90000' |
|  3 | few_and_large_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       90000000 |   1.56715 | WHERE t2 = 'third-90000' |
|  4 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |       90000000 |   1.49589 | WHERE t2 = 'third-80000' |
|  5 | few_and_large_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       90000000 |   1.54116 | WHERE t2 = 'third-80000' |
|  6 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |       90000000 |   1.51507 | WHERE t2 = 'third-70000' |
|  7 | few_and_large_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       90000000 |   1.64116 | WHERE t2 = 'third-70000' |
|  8 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |       90000000 |   1.70684 | WHERE t2 = 'third-60000' |
|  9 | few_and_large_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       90000000 |   1.57994 | WHERE t2 = 'third-60000' |
| 10 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |       90000000 |   1.611   | WHERE t2 = 'third-50000' |
| 11 | few_and_large_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       90000000 |   1.60171 | WHERE t2 = 'third-50000' |
| 12 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |       90000000 |   1.71627 | WHERE t2 = 'third-40000' |
| 13 | few_and_large_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       90000000 |   1.55213 | WHERE t2 = 'third-40000' |
| 14 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |       90000000 |   1.47868 | WHERE t2 = 'third-30000' |
| 15 | few_and_large_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       90000000 |   1.47187 | WHERE t2 = 'third-30000' |
| 16 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |       90000000 |   1.49632 | WHERE t2 = 'third-20000' |
| 17 | few_and_large_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       90000000 |   1.50047 | WHERE t2 = 'third-20000' |
| 18 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |       90000000 |   1.55545 | WHERE t2 = 'third-10000' |
| 19 | few_and_large_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       90000000 |   1.5534  | WHERE t2 = 'third-10000' |
| 20 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |       90000000 |   1.54156 | WHERE t2 = 'third-00000' |
| 21 | few_and_large_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       90000000 |   1.58482 | WHERE t2 = 'third-00000' |

## few_and_small_row_groups.parquet
|    | file                             | condition                | filter               |   rows_skipped |    elapsed | query                    |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|-----------:|:-------------------------|
| 22 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 | 0.00497926 | WHERE t2 = 'third-99999' |
| 23 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |            900 | 0.00379482 | WHERE t2 = 'third-99999' |
| 24 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 | 0.0103133  | WHERE t2 = 'third-90000' |
| 25 | few_and_small_row_groups.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |            900 | 0.00281796 | WHERE t2 = 'third-90000' |
| 26 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 | 0.00317757 | WHERE t2 = 'third-80000' |
| 27 | few_and_small_row_groups.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |            900 | 0.0094086  | WHERE t2 = 'third-80000' |
| 28 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 | 0.00334323 | WHERE t2 = 'third-70000' |
| 29 | few_and_small_row_groups.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |            900 | 0.00686749 | WHERE t2 = 'third-70000' |
| 30 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 | 0.00341328 | WHERE t2 = 'third-60000' |
| 31 | few_and_small_row_groups.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |            900 | 0.0102121  | WHERE t2 = 'third-60000' |
| 32 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 | 0.00310689 | WHERE t2 = 'third-50000' |
| 33 | few_and_small_row_groups.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |            900 | 0.00305842 | WHERE t2 = 'third-50000' |
| 34 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 | 0.00345931 | WHERE t2 = 'third-40000' |
| 35 | few_and_small_row_groups.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |            900 | 0.0106642  | WHERE t2 = 'third-40000' |
| 36 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 | 0.00331963 | WHERE t2 = 'third-30000' |
| 37 | few_and_small_row_groups.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |            900 | 0.00991278 | WHERE t2 = 'third-30000' |
| 38 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 | 0.00319133 | WHERE t2 = 'third-20000' |
| 39 | few_and_small_row_groups.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |            900 | 0.00264098 | WHERE t2 = 'third-20000' |
| 40 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 | 0.003168   | WHERE t2 = 'third-10000' |
| 41 | few_and_small_row_groups.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |            900 | 0.00275028 | WHERE t2 = 'third-10000' |
| 42 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 | 0.00299982 | WHERE t2 = 'third-00000' |
| 43 | few_and_small_row_groups.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |            900 | 0.00281984 | WHERE t2 = 'third-00000' |

## lots_of_row_groups_large.parquet
|    | file                             | condition                | filter               |   rows_skipped |   elapsed | query                    |
|---:|:---------------------------------|:-------------------------|:---------------------|---------------:|----------:|:-------------------------|
| 66 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 |  0.123951 | WHERE t2 = 'third-99999' |
| 67 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |       90000000 |  1.67087  | WHERE t2 = 'third-99999' |
| 68 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 |  0.114995 | WHERE t2 = 'third-90000' |
| 69 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |       90000000 |  1.6207   | WHERE t2 = 'third-90000' |
| 70 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 |  0.114948 | WHERE t2 = 'third-80000' |
| 71 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |       90000000 |  1.62123  | WHERE t2 = 'third-80000' |
| 72 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 |  0.114838 | WHERE t2 = 'third-70000' |
| 73 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |       90000000 |  1.6392   | WHERE t2 = 'third-70000' |
| 74 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 |  0.114483 | WHERE t2 = 'third-60000' |
| 75 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |       90000000 |  1.63362  | WHERE t2 = 'third-60000' |
| 76 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 |  0.114291 | WHERE t2 = 'third-50000' |
| 77 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |       90000000 |  1.65187  | WHERE t2 = 'third-50000' |
| 78 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |         900000 |  0.133988 | WHERE t2 = 'third-40000' |
| 79 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |       90000000 |  1.70813  | WHERE t2 = 'third-40000' |
| 80 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 |  0.116839 | WHERE t2 = 'third-30000' |
| 81 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |       90000000 |  1.67418  | WHERE t2 = 'third-30000' |
| 82 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 |  0.180112 | WHERE t2 = 'third-20000' |
| 83 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |       90000000 |  1.67156  | WHERE t2 = 'third-20000' |
| 84 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 |  0.18373  | WHERE t2 = 'third-10000' |
| 85 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |       90000000 |  1.65607  | WHERE t2 = 'third-10000' |
| 86 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 |  0.114978 | WHERE t2 = 'third-00000' |
| 87 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |       90000000 |  1.70806  | WHERE t2 = 'third-00000' |

## lots_of_row_groups_small.parquet
|     | file                             | condition                | filter               |   rows_skipped |   elapsed | query                    |
|----:|:---------------------------------|:-------------------------|:---------------------|---------------:|----------:|:-------------------------|
|  88 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | with_bloom_filter    |              0 | 0.121384  | WHERE t2 = 'third-99999' |
|  89 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' | without_bloom_filter |           9000 | 0.0182405 | WHERE t2 = 'third-99999' |
|  90 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | with_bloom_filter    |              0 | 0.115014  | WHERE t2 = 'third-90000' |
|  91 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-90000' | without_bloom_filter |           9000 | 0.0236853 | WHERE t2 = 'third-90000' |
|  92 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | with_bloom_filter    |              0 | 0.136223  | WHERE t2 = 'third-80000' |
|  93 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-80000' | without_bloom_filter |           9000 | 0.0246839 | WHERE t2 = 'third-80000' |
|  94 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | with_bloom_filter    |              0 | 0.115462  | WHERE t2 = 'third-70000' |
|  95 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-70000' | without_bloom_filter |           9000 | 0.0191121 | WHERE t2 = 'third-70000' |
|  96 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | with_bloom_filter    |              0 | 0.117209  | WHERE t2 = 'third-60000' |
|  97 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-60000' | without_bloom_filter |           9000 | 0.0178325 | WHERE t2 = 'third-60000' |
|  98 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | with_bloom_filter    |              0 | 0.117687  | WHERE t2 = 'third-50000' |
|  99 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-50000' | without_bloom_filter |           9000 | 0.0205444 | WHERE t2 = 'third-50000' |
| 100 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | with_bloom_filter    |              0 | 0.125593  | WHERE t2 = 'third-40000' |
| 101 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-40000' | without_bloom_filter |           9000 | 0.0187945 | WHERE t2 = 'third-40000' |
| 102 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | with_bloom_filter    |              0 | 0.121137  | WHERE t2 = 'third-30000' |
| 103 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-30000' | without_bloom_filter |           9000 | 0.0223087 | WHERE t2 = 'third-30000' |
| 104 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | with_bloom_filter    |              0 | 0.119489  | WHERE t2 = 'third-20000' |
| 105 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-20000' | without_bloom_filter |           9000 | 0.0215384 | WHERE t2 = 'third-20000' |
| 106 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | with_bloom_filter    |              0 | 0.131952  | WHERE t2 = 'third-10000' |
| 107 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-10000' | without_bloom_filter |           9000 | 0.0236673 | WHERE t2 = 'third-10000' |
| 108 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | with_bloom_filter    |              0 | 0.12096   | WHERE t2 = 'third-00000' |
| 109 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-00000' | without_bloom_filter |           9000 | 0.0192453 | WHERE t2 = 'third-00000' |
