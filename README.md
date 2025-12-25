# polar-sub

Textual TUI for exploring Polars DataFrames and LazyFrames with an inline SQL bar.

## Features
- Materialize a Polars DataFrame or LazyFrame and browse it in a scrollable grid.
- Run SQL queries from a top input bar to filter or transform the data.
- Keyboard bindings for resetting the query and quitting (`r`, `q`).

## Installation
```
pip install -e .
```

## Usage
### From Python
```python
import polars as pl
from polar_sub import view_frame

df = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
view_frame(df, table_name="df", head_limit=100)  # opens the TUI (optionally limit rows)
```

### From the CLI
You can also launch the viewer directly with an optional data file:
```
polar-sub path/to/file.parquet
```
Supported formats: CSV (`.csv`), Parquet (`.parquet`), and IPC/Feather (`.feather`, `.ipc`). When no path is provided, a small demo dataset is shown.
Use `--limit 100` to only materialize the first N rows on load if you have a very large frame.

## Controls
- Type a SQL query into the bar at the top and press Enter to apply.
- `r`: reset to the original dataset.
- `q`: quit.
