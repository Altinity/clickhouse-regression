from testflows.core import *

xfails_file = {
    "final/force modifier/without experimental analyzer/select join clause": [
        (
            Fail,
            "doesn't work in clickhouse"
            " https://github.com/ClickHouse/"
            "ClickHouse/issues/8655",
        )
    ],
    "final/modifier": [(Fail, "not implemented")],
    "/selects/final/force modifier/with experimental analyzer/simple select group by/*": [(Fail, "group by conflict analyzer")],
    "/selects/final/force modifier/with experimental analyzer/simple select count/simple select count/distr_*": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/simple select limit/simple select limit/distr_*": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/simple select limit by/simple select limit by/distr_*": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/simple select distinct/simple select distinct/distr_*": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/simple select where/simple select where/distr_*": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select multiple join clause select/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select nested join clause select/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select join clause/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select prewhere subquery/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select nested subquery/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select where subquery/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select subquery/*": [
        (Fail, "unknown, need to debug")],
    "/selects/final/force modifier/with experimental analyzer/select with clause/*": [
        (Fail, "unknown, need to debug")],

}