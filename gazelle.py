from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, ListItem, ListView, RichLog
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

from backend.connection import Connection
from backend.config import discover_configs


class Gazelle(App):
    CSS = """
Screen { layout: horizontal; }

#configs-pane {
    width: 30%;
    border-right: solid $panel-darken-1;
}

#log-pane {
    width: 70%;
}
"""
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
                yield RichLog(id="log", highlight=True, markup=True)
        yield Footer()

    def on_mount(self):
        self.action_refresh()

    # configs

    def action_refresh(self):
        self.configs = discover_configs()
        lv = self.query_one("#configs", ListView)
        lv.clear()
        for config in self.configs:
            lv.append(ListItem(Label(config.stem)))
        self._refresh_status()

    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.index is not None:
            self.selected_index = event.list_view.index

    def _selected_config(self) -> Path | None:
        if self.configs and 0 <= self.selected_index < len(self.configs):
            return self.configs[self.selected_index]
        return None

    # connection

    # helpers

    def _refresh_status(self) -> None:
        label = self.query_one("#status", Label)
        if self.connection.is_connected:
            label.update(f"[green]● {self.connection.config_name}[/green]")
        else:
            label.update("[dim]○ Not connected[/dim]")
