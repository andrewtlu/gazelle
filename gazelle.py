from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, ListView, RichLog, TabPane, TabbedContent
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

from backend.connection import Connection


class Gazelle(App):
    CSS = ""
    KEYBINDS = [
        ("c", "connect"),
        ("d", "disconnect"),
        ("r", "refresh"),
        ("q", "quit"),
    ]
    selected_index: reactive[int] = reactive(0)

    def __init__(self):
        super().__init__()
        self.configs: list[Path] = []
        self.connection: Connection = Connection()

    def compose(self) -> ComposeResult:
        """App structure definition."""
        yield Header()
        with Horizontal():
            with Vertical(id="configs-pane"):
                yield ListView(id="configs")
                yield Label("No connection", id="status")
            with Vertical(id="log-pane"):
                with TabbedContent():
                    with TabPane("Logs", id="logs"):
                        yield RichLog(id="log", highlight=True, markup=True)
        yield Footer()
