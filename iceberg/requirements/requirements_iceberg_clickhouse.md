# SRS-044 Iceberg 
# Software Requirements Specification

## Table of Contents


## Introduction

This Software Requirements Specification (SRS) defines the requirements for ClickHouse integration with Iceberg. ClickHouse now has 
- Iceberg() table function that provides a read-only table-like interface to Apache Iceberg tables in Amazon S3, Azure, HDFS or locally stored. 
- Iceberg engine that provides a read-only integration with existing Apache Iceberg tables in Amazon S3, Azure, HDFS and locally stored tables.

## Iceberg Table 

### Properties

- Catalog
    - Catalog Name
    - Path
    - Storage
    - Namespace
    - Type
        - REST
- Table
    - Catalog 
    - Namespace
    - Table Name
    - Table Properties
        - Format Version
    - Location
    - Schema
        - Field
            - Field Name
            - Field Type
            - Field ID
            - Required
    - Partitioning
        - Partition Field
            - Source ID
            - Field ID
            - Transform
    - Sort Order
        -Sort Field
            - Source ID
            - Field ID





### Schema Evolution
- Union by Name
- Add Column
- Rename Column
- Move Column
    - move_before
    - move_after
    - move_first
- Update Column Type
    - Update Column Type
    - Update Column Description
    - Update Required
- Delete Column 


### Partition evolution
- Add fields
- Remove fields
- Rename fields

### Table Properties
- Set Table Properties
- Remove Table Properties


## Iceberg Engine

For now ClickHouse only supports read-only access to Iceberg tables. 

### RBAC 
- Control read
    - Column-level RBAC
    - Row-level RBAC
       - Row policy

## Iceberg Table Function
