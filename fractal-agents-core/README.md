# fractal-agents-core

Core crate structure for `fractal-agents-core`, modeled after the referenced `lumina_agents_core` layout.

Responsibilities:
- Shared utilities, stable interfaces, and common helper classes for FractalForge agents.
- Provide reusable infrastructure constructs, auth support, encoding, and remote file handling.

Structure:
- `ag_ui_strands/` — core package modules for agent behavior, config, streaming, and utilities.
- `tests/` — package-level tests covering core shared behavior.
- `pyproject.toml` — package metadata and pytest config.

Key modules:
- `agent.py` — main agent abstraction.
- `config.py` — environment configuration dataclass.
- `encoder.py` — payload encoding/decoding helper.
- `snapshots.py` — snapshot persistence abstraction.
- `stream.py` — stream/event helper.
- `auth_context.py` — auth context and role management.
- `errors.py` — core exception type.
- `http_client.py` — minimal HTTP client placeholder.
- `remote_file_store.py` — remote storage abstraction.
- `secrets.py` — secret manager helper.
- `tokens.py` — token lifecycle utility.

Getting started:
1. Install dependencies with `python -m pip install -e .`.
2. Run `pytest` from `fractal-agents-core`.
