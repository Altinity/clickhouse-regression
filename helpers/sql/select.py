from .query import Query


class Select(Query):
    """
    [WITH expr_list|(subquery)]
    SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list
    [FROM [db.]table | (subquery) | table_function] [FINAL]
    [SAMPLE sample_coeff]
    [ARRAY JOIN ...]
    [GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)
    [PREWHERE expr]
    [WHERE expr]
    [GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]
    [HAVING expr]
    [WINDOW window_expr_list]
    [QUALIFY expr]
    [ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]
    [LIMIT [offset_value, ]n BY columns]
    [LIMIT [n, ]m] [WITH TIES]
    [SETTINGS ...]
    [UNION  ...]
    [INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]
    [FORMAT format]
    """

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "Select(" f"{super().__repr__()}" ")"

    def set_query(self, query):
        self.query = query
        return self
