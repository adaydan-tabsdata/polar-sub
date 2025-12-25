from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class FilterConfirm(ModalScreen[bool]):
    """Simple confirmation modal for filtering by a selected cell value."""

    def __init__(self, column: str, value: object):
        super().__init__()
        self.column = column
        self.value = value

    def compose(self) -> ComposeResult:
        display = "NULL" if self.value is None else repr(self.value)
        yield Container(
            Static(f"Filter rows where {self.column} = {display}?"),
            Container(
                Button("Apply", id="apply", variant="success"),
                Button("Cancel", id="cancel", variant="default"),
                id="filter-buttons",
            ),
            id="filter-modal",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        self.dismiss(event.button.id == "apply")
