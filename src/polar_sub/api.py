from __future__ import annotations

from pathlib import Path

import polars as pl

from .app import Driller
from .core.data import _demo_frame

Source = str | Path | pl.LazyFrame | pl.DataFrame | None


def _to_lazyframe(source: Source) -> pl.LazyFrame:
    if isinstance(source, pl.LazyFrame):
        return source
    if isinstance(source, pl.DataFrame):
        return source.lazy()
    if source is None:
        return _demo_frame()

    path = Path(source)
    if path.suffix == ".csv":
        return pl.scan_csv(path)
    if path.suffix == ".parquet":
        return pl.scan_parquet(path)

    raise ValueError(
        "source must be a .csv or .parquet file path, or a Polars DataFrame/LazyFrame"
    )


def run_driller(source: Source, table: str = "x") -> pl.LazyFrame:
    """
    Library entry point. Returns a LazyFrame so callers can keep chaining.
    """
    lf = _to_lazyframe(source)
    app = Driller(frame=lf, table_name=table)
    app.run()
    return lf
