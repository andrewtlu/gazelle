"""Parsing module for `ovpn` configurations."""

from pathlib import Path

# TODO: read from .config/gazelle/config.toml
CONFIG_DIR = Path("/etc/openvpn/client")


def discover_configs() -> list[str]:
    """Discovers configurations located in the configured directory."""

    configs = []
    for p in sorted(CONFIG_DIR.glob("*.ovpn")):
        # simply strips names, since those are only thing necessary for base connection
        # can be extended to store some configuration class to parse extra information if necessary in future
        configs.append(p.name)

    return configs
