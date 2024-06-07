
## 10M_rows_10_row_groups.parquet
|    | file                           | condition                                      | filter               |   rows_skipped |    elapsed | query                                          |
|---:|:-------------------------------|:-----------------------------------------------|:---------------------|---------------:|-----------:|:-----------------------------------------------|
|  8 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999'                       | with_bloom_filter    |              0 | 0.00899444 | WHERE t2 = 'third-99999'                       |
|  9 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999'                       | without_bloom_filter |       10000000 | 0.087605   | WHERE t2 = 'third-99999'                       |
| 10 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | with_bloom_filter    |              0 | 0.00476394 | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
| 11 | 10M_rows_10_row_groups.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | without_bloom_filter |       10000000 | 0.0707695  | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## few_and_large_row_groups.parquet
|    | file                             | condition                                      | filter               |   rows_skipped |   elapsed | query                                          |
|---:|:---------------------------------|:-----------------------------------------------|:---------------------|---------------:|----------:|:-----------------------------------------------|
|  0 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999'                       | with_bloom_filter    |       90000000 |   1.65043 | WHERE t2 = 'third-99999'                       |
|  1 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999'                       | without_bloom_filter |       90000000 |   1.52868 | WHERE t2 = 'third-99999'                       |
|  2 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | with_bloom_filter    |       90000000 |   1.52518 | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  3 | few_and_large_row_groups.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | without_bloom_filter |       90000000 |   1.49473 | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## few_and_small_row_groups.parquet
|    | file                             | condition                                      | filter               |   rows_skipped |    elapsed | query                                          |
|---:|:---------------------------------|:-----------------------------------------------|:---------------------|---------------:|-----------:|:-----------------------------------------------|
|  4 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999'                       | with_bloom_filter    |              0 | 0.00316074 | WHERE t2 = 'third-99999'                       |
|  5 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999'                       | without_bloom_filter |            900 | 0.00315599 | WHERE t2 = 'third-99999'                       |
|  6 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | with_bloom_filter    |              0 | 0.0026949  | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  7 | few_and_small_row_groups.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | without_bloom_filter |            900 | 0.00299067 | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## lots_of_row_groups_large.parquet
|    | file                             | condition                                      | filter               |   rows_skipped |   elapsed | query                                          |
|---:|:---------------------------------|:-----------------------------------------------|:---------------------|---------------:|----------:|:-----------------------------------------------|
| 12 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999'                       | with_bloom_filter    |              0 |  0.120305 | WHERE t2 = 'third-99999'                       |
| 13 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999'                       | without_bloom_filter |       90000000 |  1.63438  | WHERE t2 = 'third-99999'                       |
| 14 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | with_bloom_filter    |              0 |  0.116361 | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
| 15 | lots_of_row_groups_large.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | without_bloom_filter |       90000000 |  1.66466  | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## lots_of_row_groups_small.parquet
|    | file                             | condition                                      | filter               |   rows_skipped |   elapsed | query                                          |
|---:|:---------------------------------|:-----------------------------------------------|:---------------------|---------------:|----------:|:-----------------------------------------------|
| 16 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999'                       | with_bloom_filter    |              0 | 0.263251  | WHERE t2 = 'third-99999'                       |
| 17 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999'                       | without_bloom_filter |           9000 | 0.0202029 | WHERE t2 = 'third-99999'                       |
| 18 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | with_bloom_filter    |              0 | 0.121975  | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
| 19 | lots_of_row_groups_small.parquet | WHERE t2 = 'third-99999' OR t2 = 'third-99998' | without_bloom_filter |           9000 | 0.0179793 | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
