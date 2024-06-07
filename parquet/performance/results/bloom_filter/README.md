
## 10M_rows_10_row_groups.parquet
|    | file                           | filter               |   rows_skipped |    elapsed |   query | conditions                                     |
|---:|:-------------------------------|:---------------------|---------------:|-----------:|--------:|:-----------------------------------------------|
|  4 | 10M_rows_10_row_groups.parquet | with_bloom_filter    |              0 | 0.00514088 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  5 | 10M_rows_10_row_groups.parquet | without_bloom_filter |       10000000 | 0.0735535  |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## few_and_large_row_groups.parquet
|    | file                             | filter               |   rows_skipped |   elapsed |   query | conditions                                     |
|---:|:---------------------------------|:---------------------|---------------:|----------:|--------:|:-----------------------------------------------|
|  0 | few_and_large_row_groups.parquet | with_bloom_filter    |       90000000 |   1.52308 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  1 | few_and_large_row_groups.parquet | without_bloom_filter |       90000000 |   1.50894 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## few_and_small_row_groups.parquet
|    | file                             | filter               |   rows_skipped |    elapsed |   query | conditions                                     |
|---:|:---------------------------------|:---------------------|---------------:|-----------:|--------:|:-----------------------------------------------|
|  2 | few_and_small_row_groups.parquet | with_bloom_filter    |              0 | 0.00340092 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  3 | few_and_small_row_groups.parquet | without_bloom_filter |            900 | 0.00303125 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## lots_of_row_groups_large.parquet
|    | file                             | filter               |   rows_skipped |   elapsed |   query | conditions                                     |
|---:|:---------------------------------|:---------------------|---------------:|----------:|--------:|:-----------------------------------------------|
|  6 | lots_of_row_groups_large.parquet | with_bloom_filter    |              0 |  0.117186 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  7 | lots_of_row_groups_large.parquet | without_bloom_filter |       90000000 |  1.66703  |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |

## lots_of_row_groups_small.parquet
|    | file                             | filter               |   rows_skipped |   elapsed |   query | conditions                                     |
|---:|:---------------------------------|:---------------------|---------------:|----------:|--------:|:-----------------------------------------------|
|  8 | lots_of_row_groups_small.parquet | with_bloom_filter    |              0 | 0.190154  |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
|  9 | lots_of_row_groups_small.parquet | without_bloom_filter |           9000 | 0.0214849 |     nan | WHERE t2 = 'third-99999' OR t2 = 'third-99998' |
