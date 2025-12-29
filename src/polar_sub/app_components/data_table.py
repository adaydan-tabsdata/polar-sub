from __future__ import annotations

from textual import events, on
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable, ListItem, ListView, Static


class ContextMenu(ModalScreen[str | None]):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset_query", "Reset query"),
        ("ctrl+c", "quit", "Quit"),
    ]
    CSS = """
    ContextMenu { background: transparent; }
    #menu-box { width: auto; padding: 0; border: none; background: $surface; }

    #menu-list ListItem { padding: 0 1; background: blue; }
    #menu-list ListItem:hover { background: $accent 20%; }
    #menu-list ListItem.-selected { background: $accent 30%; }
    """

    def __init__(self, origin, items):
        super().__init__()
        self.origin = origin
        self.items = items

    def compose(self):
        yield Container(
            ListView(
                *[ListItem(Static(label, id=cmd)) for label, cmd in self.items],
                id="menu-list",
            ),
            id="menu-box",
        )

    def on_mount(self):
        menu_box = self.query_one("#menu-box")
        menu_list = self.query_one("#menu-list")
        max_len = max(len(label) for label, _ in self.items)

        menu_box.styles.offset = self.origin

        menu_box.styles.width = "auto"
        menu_box.styles.height = "auto"
        menu_box.styles.width = max_len + 2
        menu_list.styles.height = len(self.items)
        menu_list.styles.padding = 0

        self.query_one("#menu-list").focus()

    def on_list_view_selected(self, event: ListView.Selected):
        widget = event.item.query().first().id
        print(widget)
        self.dismiss(widget)

    @on(events.Click)
    def handle_click_out(self, event: events.Click):
        print("out")
        if isinstance(event.widget, ContextMenu):
            self.dismiss(None)

    def on_key(self, event):
        if event.key == "escape":
            self.dismiss(None)
        if event.key == "ctrl+c":
            self.dismiss(None)
            self.app.exit()


class PolarDataTable(DataTable):
    class NewSqlQuery(Message):
        """Color selected message."""

        def __init__(self, operation, column, value) -> None:
            self.operation = operation
            self.column = column
            self.value = value
            super().__init__()

    @on(events.Click)
    async def handle_double_click(self, event: events.Click):
        if event.button == 5 and getattr(event, "chain", 1) >= 2:
            col_index = self.cursor_column
            coord = self.cursor_coordinate
            all_cols = self.columns

            col = str(list(all_cols.values())[col_index].label)
            value = self.get_cell_at(coord)

            self.post_message(
                self.NewSqlQuery(operation="where", column=col, value=value)
            )

        if event.button == 1 and getattr(event, "chain", 1) >= 2:
            if isinstance(event.widget, DataTable):
                col_index = self.cursor_column
                coord = self.cursor_coordinate
                all_cols = self.columns

                col = str(list(all_cols.values())[col_index].label)
                value = self.get_cell_at(coord)

                meta = event.style.meta
                if "row" in meta and "column" in meta and meta["row"] >= 0:
                    # approximate anchor using screen coords from the click
                    origin = (event.screen_x, event.screen_y)

                    coord = Coordinate(row=meta["row"], column=meta["column"])
                    col = str(list(all_cols.values())[col_index].label)
                    value = self.get_cell_at(coord)

                    print(col)
                    print(value)

                    menu = ContextMenu(
                        origin=origin,
                        items=[("Filter on this value", "filter")],
                    )
                    worker = self.run_worker(
                        self.app.push_screen_wait(menu), exit_on_error=False
                    )
                    await worker.wait()
                    choice = worker.result
                    print("finished")
                    print(choice)
                    if choice == "filter":
                        self.post_message(
                            self.NewSqlQuery(operation="where", column=col, value=value)
                        )
                    event.stop()
