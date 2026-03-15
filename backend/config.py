"""Parsing module for `ovpn` configurations."""

from pathlib import Path

# TODO: read from .config/gazelle/config.toml
CONFIG_DIR = Path.home() / "VPN"


def discover_configs() -> list[Path]:
    """Discovers configurations located in the configured directory."""

    # simply strips names, since those are only thing necessary for base connection
    # can be extended to store some configuration class to parse extra information if necessary in future
    return sorted(CONFIG_DIR.glob("*.ovpn"))
