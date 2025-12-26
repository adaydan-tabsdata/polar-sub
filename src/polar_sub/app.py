from __future__ import annotations

import polars as pl
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Footer

from polar_sub.app_components import PolarDataTable, QueryInput
from polar_sub.core.data import (
    FrameLike,
    _stringify_row,
    materialize_frame,
    sql_context_for_frame,
)
from polar_sub.core.sql_parser import add_filter, eq_condition


class Driller(App):
    """Interactive TUI for browsing Polars data."""

    CSS = """
    Screen { layout: vertical; }
    #query-container {
        layout: horizontal;
        padding: 1;
        height: 1fr;
        min-height: 9;
        align-horizontal: left;
    }
    #sql-input { width: 1fr; min-height: 3; margin-right: 1; overflow-y: auto; }
    #status { width: 40; text-style: bold; }
    #data-container { height: 2fr}
    #filter-modal {
        padding: 1 2;
        border: round $accent;
    }
    #filter-buttons {
        layout: horizontal;
        padding-top: 1;
    }
    Button {
        border: round;
        background: transparent;
        min-height: 1;
        height: auto;
    }
    #sql-container { width: 4fr; }
    #run-button-container { grid-size: 2 2; }
    
    """

    filters = reactive(set(), init=False)
    current_query = reactive(set(), init=False)

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset_query", "Reset query"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        frame: FrameLike,
        table_name: str = "table",
        initial_query: str | None = None,
        head_limit: int | None = 100,
    ):
        super().__init__()
        # static
        self.base_df = materialize_frame(frame, head_limit=head_limit)
        self.table_name = table_name
        self.ctx = sql_context_for_frame(self.base_df, table_name=table_name)
        self.initial_query = initial_query or f"SELECT * FROM {self.table_name}"

        # dynamic
        self.current_df = self.base_df
        self.current_query = self.initial_query

        self._row_cache: list[list[object]] = []

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Container(
                Container(
                    QueryInput.code_editor(
                        self.initial_query,
                        placeholder="Enter SQL (ctrl+enter to run)",
                        id="sql-input",
                        language="sql",
                        soft_wrap=True,
                    ),
                    id="sql-container",
                ),
                Grid(
                    Button("Run", id="run-query"),
                    Button("Reset", id="reset-query"),
                    Button("Exit", id="exit-app"),
                    id="run-button-container",
                ),
                id="query-container",
            ),
            Container(
                PolarDataTable(id="data-table", zebra_stripes=True), id="data-container"
            ),
        )
        Footer()

    def on_mount(self) -> None:
        self.table = self.query_one(DataTable)
        self.table.cursor_type = "cell"
        self._refresh_table(self.current_df)

    async def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        if event.button.id == "run-query":
            await self._run_query()
        if event.button.id == "reset-query":
            await self.action_reset_query()
        if event.button.id == "exit-app":
            self.exit()

    def _run_query(self) -> None:
        query = self.initial_query
        for i in self.filters:
            query = add_filter(query, i)
            print(query)
        self.current_query = query
        result = self.ctx.execute(self.current_query)
        query_input = self.query_one(QueryInput)
        query_input.text = self.current_query
        df = result.collect() if isinstance(result, pl.LazyFrame) else result
        self.current_df = df
        self._refresh_table(df)

    def _refresh_table(self, df: pl.DataFrame) -> None:
        table = self.table
        table.clear(columns=True)
        self._row_cache = []
        if df.is_empty():
            table.add_column("(empty)")
            self._update_status("No rows")
            return
        table.add_columns(*df.columns)
        for row in df.iter_rows():
            row_list = list(row)
            self._row_cache.append(row_list)
            table.add_row(*_stringify_row(row_list))
        table.move_cursor(row=0, column=0)
        table.scroll_home(animate=False)

    def _update_status(self, message: str) -> None:
        self.app.notify(message, severity="information", timeout=2)

    async def action_reset_query(self) -> None:
        query_input = self.query_one(QueryInput)
        query_input.text = self.app.initial_query
        self.filters = set()
        self._refresh_table(self.base_df)
        self._update_status("Reset")
        self.current_df = self.base_df

    @on(PolarDataTable.NewSqlQuery)
    def handle_new_query_clause(self, event: PolarDataTable.NewSqlQuery):
        operation = event.operation
        column = event.column
        value = event.value
        starting_filters = set(self.filters)
        if operation == "where":
            clause = eq_condition(col=column, value=value)
            print(type(clause))
            starting_filters.add(clause)
            self.filters = starting_filters
        return

    def watch_filters(self, old, new):
        self._run_query()
