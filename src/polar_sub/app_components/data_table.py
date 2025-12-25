from __future__ import annotations

from textual import events, on
from textual.message import Message
from textual.widgets import DataTable


class PolarDataTable(DataTable):
    class NewSqlQuery(Message):
        """Color selected message."""

        def __init__(self, operation, column, value) -> None:
            self.operation = operation
            self.column = column
            self.value = value
            super().__init__()

    @on(events.Click)
    def handle_double_click(self, event: events.Click):

        if event.button == 1 and getattr(event, "chain", 1) >= 2:
            col_index = self.cursor_column
            coord = self.cursor_coordinate
            all_cols = self.columns

            col = str(list(all_cols.values())[col_index].label)
            value = self.get_cell_at(coord)

            self.post_message(
                self.NewSqlQuery(operation="where", column=col, value=value)
            )
