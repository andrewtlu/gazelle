import asyncio
from pathlib import Path


class Connection:
    def __init__(self):
        self.process: asyncio.subprocess.Process | None = None
        self.config_name: str = ""

    @property
    def is_connected(self) -> bool:
        return self.process is not None and self.process.returncode is None
