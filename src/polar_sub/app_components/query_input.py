from __future__ import annotations

from typing import Union

from textual import events, on
from textual.widgets import TextArea


class QueryInput(TextArea):
    """TextArea configured for SQL entry with double-click select-all."""

    @on(events.Click)
    async def handle_double_click(self, event: events.Click):
        if event.button == 1 and getattr(event, "chain", 1) >= 2:
            await self.select_entire_sql_input(event)

    @on(events.Key)
    async def handle_ctrl_a(self, event: events.Key):
        if event.key == "ctrl+a":
            await self.select_entire_sql_input(event)

    @on(events.Key)
    async def handle_ctrl_c(self, event: events.Key):
        if event.key == "ctrl+c":
            await self.quit_app()

    async def select_entire_sql_input(self, event: Union[events.Key, events.Click]):
        self.focus()
        self.select_all()
        event.stop()
        return

    async def quit_app(self):
        self.app.exit()
        return
