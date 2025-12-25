from __future__ import annotations

import pathlib
from typing import Iterable, Union

import polars as pl

FrameLike = Union[pl.DataFrame, pl.LazyFrame]


def materialize_frame(frame: FrameLike, head_limit: int | None = None) -> pl.DataFrame:
    """Ensure we have an in-memory DataFrame, optionally limited to the first N rows."""
    if isinstance(frame, pl.LazyFrame):
        if head_limit is not None:
            frame = frame.limit(head_limit)
        return frame.collect()
    if isinstance(frame, pl.DataFrame):
        return frame.head(head_limit) if head_limit is not None else frame
    raise TypeError("frame must be a polars DataFrame or LazyFrame")


def load_frame_from_path(path: pathlib.Path) -> pl.DataFrame:
    """Load a DataFrame from a known file format."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pl.read_csv(path)
    if suffix in {".parquet"}:
        return pl.read_parquet(path)
    raise ValueError(f"Unsupported file format: {suffix}")


def sql_context_for_frame(
    frame: pl.DataFrame, table_name: str = "frame"
) -> pl.SQLContext:
    ctx = pl.SQLContext()
    ctx.register(table_name, frame)
    return ctx


def _stringify_row(row: Iterable[object]) -> list[str]:
    return ["" if value is None else value for value in row]


def _sql_literal(value: object) -> str:
    """Render a Python value as a Polars SQL literal."""
    if isinstance(value, (int, float)):
        return f"'{value}'"
    return value


def _build_filter_query(table_name: str, column: str, value: object) -> str:
    if value is None:
        return f'SELECT * FROM {table_name} WHERE "{column}" IS NULL'
    literal = _sql_literal(value)
    return f'SELECT * FROM {table_name} WHERE "{column}" = {literal}'


def _demo_frame() -> pl.DataFrame:
    return pl.LazyFrame(
        {
            "city": ["Oslo", "Paris", "Berlin", "Chicago"],
            "temp_c": [3, 12, 8, -1],
            "wind_kph": [12.5, 8.1, 14.2, 20.3],
        }
    )
