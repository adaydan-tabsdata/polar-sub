import sqlglot
from sqlglot import exp


def compile_sql_expression(self):
    query = self.current_query
    print(query)
    for i in [i for i in self.filters if i not in self.completed_filters]:
        query = add_filter(query, i)
        self.completed_filters.append(i)
    print(query)
    print(self.head_limit)
    return query


def add_filter(sql: str | exp.EQ, condition_sql: str | exp.EQ, dialect=None) -> str:
    if isinstance(sql, str):
        tree = sqlglot.parse_one(sql, dialect=dialect)
    else:
        tree = sql
    if isinstance(condition_sql, str):
        condition = sqlglot.parse_one(condition_sql, dialect=dialect)
    else:
        condition = condition_sql

    where = tree.args.get("where")
    if where:
        tree.set("where", exp.Where(this=exp.and_(where.this, condition)))
    else:
        tree.set("where", exp.Where(this=condition))
    return tree.sql(dialect=dialect)


def add_limit_if_missing(
    sql: str | exp.EQ, limit: int = 100, dialect: str | None = None
) -> str:
    if isinstance(sql, str):
        query = sqlglot.parse_one(sql)

    # Only applies to SELECT statements (and similar)
    if isinstance(query, exp.Select) or query.find(exp.Select):
        existing_limit = query.args.get("limit")
        print(":::")
        print(existing_limit)
        print(limit)
        if not existing_limit:
            query.set("limit", exp.Limit(expression=exp.Literal.number(limit)))
        print(query)
    return query.sql()


def eq_condition(col: str, value):
    left = exp.Column(this=col)

    # NULL must use IS NULL
    if value is None:
        return exp.Is(this=left, expression=exp.Null())

    # bools become TRUE/FALSE
    if isinstance(value, bool):
        right = exp.Boolean(this=value)
        return exp.EQ(this=left, expression=right)

    # numbers don’t need quotes
    if isinstance(value, (int, float)):
        right = exp.Literal.number(value)
        return exp.EQ(this=left, expression=right)

    # everything else treat as string (adds '')
    right = exp.Literal.string(str(value))
    return exp.EQ(this=left, expression=right)


print(eq_condition(col="test", value=5))
