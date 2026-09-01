# third_party/

> **Documentation status: reference · Last verified: 2026-08-29**

Pinned agent CLIs that are not vendored in Git. `./setup.sh` installs DeepSeek
Harness (`dsh`) and Codex (`codex`) into `runtimes/bin/`, the same bootstrap
level as host OpenHands (`INSTALL_OPENHANDS=1` / `uv tool install`).

`runtimes/` is gitignored. Re-install after a fresh clone:

```bash
./setup.sh
# or
./harness/scripts/pin_runtime_agents.sh
```

Pins live in `harness/config/runtime_pins.json`.
