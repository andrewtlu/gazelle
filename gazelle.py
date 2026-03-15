from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, ListItem, ListView, RichLog
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

from backend.connection import Connection
from backend.config import discover_configs


# TODO: figure out more elegant solution
PWD_FILE = Path.home() / "VPN" / "pass.txt"


class Gazelle(App):
    CSS = """
Screen { layout: horizontal; }

#configs-pane {
    width: 30%;
    border-right: solid $panel-darken-1;
    padding: 0 1;
}

#log-pane {
    width: 70%;
    padding: 0 1;
}
"""
    BINDINGS = [
        ("c", "connect", "Connect"),
        ("d", "disconnect", "Disconnect"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
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

    async def on_unmount(self):
        await self.connection.stop()

    async def action_quit(self) -> None:
        if self.connection.is_connected:
            self._log("[dim]Disconnecting before exit…[/dim]")
            await self.connection.stop()
        self.exit()

    # configs

    def action_refresh(self):
        self.configs = discover_configs()
        lv = self.query_one("#configs", ListView)
        lv.clear()
        for config in self.configs:
            lv.append(ListItem(Label(config.stem)))
        self._refresh_status()

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        if event.list_view.index is not None:
            self.selected_index = event.list_view.index

    def _selected_config(self) -> Path | None:
        if self.configs and 0 <= self.selected_index < len(self.configs):
            return self.configs[self.selected_index]
        return None

    # connection

    def action_connect(self):
        config = self._selected_config()
        if not config:
            return
        if self.connection.is_connected:
            self.notify("Already connected — disconnect first.", severity="warning")
            return
        self._do_connect(config)

    @work(exclusive=True)
    async def _do_connect(self, config: Path) -> None:
        log = self.query_one("#log", RichLog)
        log.clear()
        self._log(f"[dim]Connecting to {config.stem}…[/dim]")

        await self.connection.start(
            config_path=config,
            password_file=PWD_FILE,
            log_callback=self._on_log_line,
            exit_callback=self._on_exit,
        )
        self._refresh_status()

    async def _on_log_line(self, line: str) -> None:
        self._log(line)

    async def _on_exit(self, code: int) -> None:
        self._refresh_status()
        if code == 0:
            self._log("[green]Connection closed cleanly.[/green]")
        else:
            self._log(f"[red]openvpn exited with code {code}.[/red]")

    def action_disconnect(self) -> None:
        if not self.connection.is_connected:
            self.notify("Not connected.", severity="warning")
            return
        self._do_disconnect()

    @work
    async def _do_disconnect(self) -> None:
        self._log("[dim]Disconnecting…[/dim]")
        await self.connection.stop()
        self._refresh_status()
        self._log("[yellow]Disconnected.[/yellow]")

    # helpers

    def _log(self, msg: str) -> None:
        self.query_one("#log", RichLog).write(msg)

    def _refresh_status(self) -> None:
        label = self.query_one("#status", Label)
        if self.connection.is_connected:
            label.update(f"[green]● {self.connection.config_name}[/green]")
        else:
            label.update("[dim]○ Not connected[/dim]")
