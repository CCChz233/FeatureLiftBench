#!/usr/bin/env python3
"""Legacy entrypoint — mostly unused in benchmark tasks."""

from vibe_app.app import create_app
from vibe_app.config_loader import bootstrap_config

if __name__ == "__main__":
    bootstrap_config("config")
    app = create_app()
    print("VibeShop stub ready", app.name)
