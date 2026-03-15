"""Connection logic for openvpn cli connections."""

import asyncio
from pathlib import Path
from collections.abc import Callable


class Connection:
    """Wrapper for the currently open VPN connection."""

    def __init__(self):
        self.process: asyncio.subprocess.Process | None = None
        self.config_name: str = ""

    @property
    def is_connected(self) -> bool:
        return self.process is not None and self.process.returncode is None

    async def listen(self, log_callback: Callable[[], str], exit_callback: Callable[[], any]):
        """Establishes a stream between the current process' output and gazelle's TUI."""
        assert self.process and self.process.stdout

        async for raw in self.process.stdout:
            line = raw.decode().rstrip()
            await log_callback(line)

        # exit logic
        code = await self.process.wait()
        self.process = None
        self.config_name = ""
        return exit_callback(code)

    async def stop(self):
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()

        self.process = None
        self.config_name = ""
