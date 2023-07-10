You can run bench tests by using `./perfomance.py, which will allow you to test the performance of all available control
cluster configurations for your local ClickHouse binary.

If you want to test some special ClickHouse versions, you can add them with the `--clickhouse-binary-list` setting, as in 
the example below.

Example:
```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```
As output, you will receive a `bench_*.csv` file with a unique name for every run where numeric cell values are ratios 
between the mean values of insert times for column and row control cluster configurations.

The result file can be imported to Google Docks, where `Format-->Conditional formatting-->Color scale` can be applied 
to all numeric cells to receive more readable output.

Color scale setting example:

<img src="Color_scale.png" alt="Color scale img" width="400" height="600">

Final output example:

<img src="final_output.png" alt="final output img" width="1500" height="300">

