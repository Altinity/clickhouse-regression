# Parquet Performance

## Performance Tests flow

```mermaid
graph TD
    style B fill:#F9EBB2,stroke:#D4AF37,stroke-width:2px;
    style C fill:#B2D8F9,stroke:#4682B4,stroke-width:2px;
    style D,E fill:#C6E1C6,stroke:#3D9140,stroke-width:2px;
    style F fill:#F9EBB2,stroke:#D4AF37,stroke-width:2px;
    style G fill:#B2D8F9,stroke:#4682B4,stroke-width:2px;

    B[Insert dataset from S3 bucket into ClickHouse]
    B --> C[Generate Parquet file]
    C --> D[Run queries on Parquet file using DuckDB]
    C --> E[Run queries on Parquet file using ClickHouse]
    D --> F[Collect runtime results from each query]
    E --> F
    F --> G[Export results into CSV]
```
