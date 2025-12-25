import sqlglot
from sqlglot import exp


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
