from textual.app import App


class Gazelle(App):
    CSS = ""
    KEYBINDS = [
        ("c", "connect"),
        ("d", "disconnect"),
        ("r", "refresh"),
        ("q", "quit"),
    ]

    def __init__(self):
        super().__init__()
        self.configs: list[str] = []
