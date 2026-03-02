# Project Index: OpenHands CLI (IronHands-CLI)

Generated: 2026-03-02 | Version: 1.13.0 | Python 3.12

## Overview

OpenHands V1 CLI — Terminal User Interface for the OpenHands AI Agent. Supports TUI, IDE (ACP), headless, web, and GUI server modes. Built on Textual with the OpenHands Software Agent SDK.

## 📁 Project Structure

```
openhands_cli/           # Main package (121 .py files)
├── entrypoint.py        # CLI main() — arg parsing, mode dispatch
├── setup.py             # First-run setup wizard
├── utils.py             # Shared utilities
├── locations.py         # Path constants (~/.openhands/)
├── theme.py             # Rich/Textual theming
├── terminal_compat.py   # Terminal compatibility checks
├── version_check.py     # Version update checking
├── gui_launcher.py      # GUI server launcher
├── acp_impl/            # Agent Communication Protocol (IDE integration)
│   ├── main.py          # ACP entry: asyncio.run(run_acp_server())
│   ├── agent/           # Agent implementations
│   │   ├── base_agent.py
│   │   ├── local_agent.py
│   │   ├── remote_agent.py
│   │   └── launcher.py
│   ├── runner.py        # ACP conversation runner
│   ├── confirmation.py  # User confirmation handling
│   ├── slash_commands.py # Slash command processing
│   ├── events/          # Event streaming & handling
│   │   ├── event.py
│   │   ├── shared_event_handler.py
│   │   ├── token_streamer.py
│   │   ├── tool_state.py
│   │   └── utils.py
│   └── utils/           # Conversion, MCP, resources
├── auth/                # Authentication (device flow, tokens, API client)
│   ├── device_flow.py
│   ├── login_command.py
│   ├── logout_command.py
│   ├── api_client.py
│   ├── http_client.py
│   └── token_storage.py
├── argparsers/          # CLI argument parsers
│   ├── main_parser.py   # Primary parser
│   ├── cloud_parser.py, acp_parser.py, mcp_parser.py
│   ├── web_parser.py, serve_parser.py, view_parser.py
│   └── auth_parser.py
├── stores/              # Settings persistence
│   ├── cli_settings.py  # CLI config store
│   └── agent_store.py   # Agent settings store
├── conversations/       # Conversation management
│   ├── models.py        # Data models
│   ├── display.py       # Conversation list display
│   ├── viewer.py        # Conversation viewer
│   ├── protocols.py     # Protocol interfaces
│   └── store/           # Local & cloud storage backends
├── cloud/               # Cloud backend integration
│   ├── command.py       # Cloud subcommand
│   └── conversation.py  # Cloud conversation API
├── mcp/                 # MCP (Model Context Protocol) integration
│   ├── mcp_commands.py
│   ├── mcp_utils.py
│   └── mcp_display_utils.py
├── shared/              # Shared utilities
│   └── delegate_formatter.py
└── tui/                 # Textual TUI (56 .py files)
    ├── textual_app.py   # OpenHandsApp — main Textual application
    ├── serve.py         # Web serve mode
    ├── messages.py      # TUI message types
    ├── core/            # TUI business logic
    │   ├── conversation_manager.py   # Central orchestrator
    │   ├── conversation_runner.py    # Agent conversation execution
    │   ├── conversation_crud_controller.py
    │   ├── conversation_switch_controller.py
    │   ├── user_message_controller.py
    │   ├── confirmation_flow_controller.py
    │   ├── confirmation_policy_service.py
    │   ├── refinement_controller.py  # Iterative refinement (critic)
    │   ├── runner_registry.py
    │   ├── runner_factory.py
    │   ├── commands.py, events.py, state.py
    │   └── __init__.py
    ├── widgets/         # Custom Textual widgets
    │   ├── input_area.py
    │   ├── main_display.py
    │   ├── status_line.py
    │   ├── splash.py, collapsible.py
    │   ├── richlog_visualizer.py
    │   └── user_input/  # Input field components
    ├── panels/          # Side panels
    │   ├── history_side_panel.py
    │   ├── plan_side_panel.py
    │   ├── mcp_side_panel.py
    │   ├── confirmation_panel.py
    │   └── *_style.py   # Panel CSS styles
    ├── modals/          # Modal dialogs
    │   ├── settings/    # Settings screen & tabs
    │   ├── exit_modal.py
    │   ├── confirmation_modal.py
    │   └── switch_conversation_modal.py
    ├── content/         # Static content (splash, resources)
    └── utils/critic/    # Critic feedback visualization

tests/                   # Test suite (112 .py files)
├── acp/                 # ACP agent tests
├── auth/                # Auth flow tests
├── cloud/               # Cloud integration tests
├── conversations/       # Conversation store tests
├── mcp/                 # MCP utility tests
├── settings/            # Settings preservation tests
├── shared/              # Shared utility tests
├── snapshots/           # Textual snapshot tests (CSS rendering)
│   └── e2e/             # End-to-end snapshot tests
├── stores/              # Store tests
├── tui/                 # TUI component tests
│   ├── core/            # Core logic tests
│   ├── panels/          # Panel tests
│   └── modals/          # Modal/settings tests
└── test_*.py            # Top-level tests (main, utils, CLI help, etc.)

tui_e2e/                 # E2E test framework
├── runner.py            # Test runner
├── mock_llm_server.py   # Mock LLM for testing
├── mock_critic.py       # Mock critic
├── models.py, trajectory.py, utils.py
└── test_*.py            # E2E test cases

scripts/acp/             # Debug scripts (jsonrpc_cli.py, debug_client.py)
hooks/                   # PyInstaller runtime hooks
.github/workflows/       # CI: tests, lint, type-check, release, binary build
```

## 🚀 Entry Points

| Entry Point | Command | Path |
|---|---|---|
| CLI main | `openhands` | `openhands_cli.entrypoint:main` |
| ACP server | `openhands-acp` | `openhands_cli.acp:main` |
| TUI App | (internal) | `openhands_cli.tui.textual_app:OpenHandsApp` |

## 🔧 Running Modes

| Mode | Command | Description |
|---|---|---|
| TUI | `openhands` | Interactive Textual terminal UI |
| IDE/ACP | `openhands acp` | Agent Communication Protocol for IDEs |
| Headless | `openhands --headless -t "task"` | CI/automation, requires `--task` or `--file` |
| Web | `openhands web` | Browser-based TUI via textual-serve |
| GUI Server | `openhands serve` | Full OpenHands web GUI |
| Cloud | `openhands cloud` | Cloud-hosted agent |

## 📦 Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| openhands-sdk | 1.11.5 | Agent SDK (conversation, LLM) |
| openhands-tools | 1.11.5 | Agent tool implementations |
| openhands-workspace | 1.11.1 | Workspace management |
| textual | >=8.0, <9.0 | TUI framework |
| agent-client-protocol | >=0.7.0, <0.8.0 | ACP protocol |
| rich | <14.3.0 | Terminal formatting |
| httpx | >=0.25.0 | HTTP client |
| pydantic | >=2.7 | Data validation |
| typer | >=0.17.4 | CLI framework |

## 🔗 Configuration

Stored in `~/.openhands/`:
- `agent_settings.json` — Agent/LLM settings (model, condenser)
- `cli_config.json` — CLI/TUI preferences (critic, theme)
- `mcp.json` — MCP server configuration

## 📚 Documentation

| File | Topic |
|---|---|
| README.md | Installation, usage, running modes |
| AGENTS.md | AI agent instructions |
| RELEASE_PROCEDURE.md | Release workflow |
| .dev/ | Development specs, research, bug tracking |

## 🧪 Testing

- **Unit/integration tests**: 112 files in `tests/`
- **Snapshot tests**: `tests/snapshots/` (Textual CSS rendering)
- **E2E tests**: `tui_e2e/` (mock LLM server, trajectory-based)
- **Run**: `pytest` (configured in pyproject.toml)
- **Lint**: `ruff` | **Type check**: `pyright` | **Pre-commit**: configured

## 📝 Quick Start

```bash
# Install
uv tool install openhands --python 3.12

# Run TUI
openhands

# Run headless
openhands --headless -t "fix the bug in main.py"

# Dev setup
uv sync --group dev
pytest
ruff check .
```
