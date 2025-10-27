# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shell Helper is a cross-platform shell command execution tool that supports **three distinct interfaces**:

1. **MCP Stdio Transport** - Model Context Protocol over stdin/stdout for local CLI integration
2. **MCP SSE Transport** - Model Context Protocol over HTTP/SSE for networked deployments
3. **FastAPI REST API** - Traditional HTTP REST endpoints for direct shell command execution

All interfaces provide cross-platform shell execution by auto-detecting the OS and using PowerShell on Windows or standard shell on Linux/macOS.

## Development Commands

### Installation
```bash
# Install all dependencies
uv pip install fastapi uvicorn sse-starlette httpx mcp openai python-dotenv pytest pytest-asyncio pytest-cov pydantic
```

### Running Services

**MCP Stdio (Local):**
```bash
python client_with_servers.py
```

**MCP SSE (Network):**
```bash
# Terminal 1: Start SSE server
python server_shell_helper_sse.py
# Or: uvicorn server_shell_helper_sse:app --host 0.0.0.0 --port 8000

# Terminal 2: Start client
python client_with_servers_sse.py
```

**FastAPI REST:**
```bash
# Using run script
python run.py

# Or directly with uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test files
uv run pytest tests/test_api.py -v
uv run pytest tests/test_shell_agent.py -v

# Run with coverage
uv run pytest tests/ --cov=api -v

# Test SSE server endpoints
curl http://localhost:8000/health
```

### Monitoring
```bash
# Basic monitoring
python test_quick_endpoint.py

# Custom parameters
python test_quick_endpoint.py -i 60 -d 120 --host localhost --port 8000
```

### Environment Configuration
Create `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

## Architecture

### Three-Interface Design

The project is organized into three independent interfaces that share common shell execution logic:

**1. MCP Stdio Transport** (`server_shell_helper.py`, `client_with_servers.py`)
- Uses FastMCP framework
- Communication: stdin/stdout with JSON-RPC 2.0
- Deployment: Client launches server as subprocess
- Config: `mcp_servers.json` with `command`/`args`

**2. MCP SSE Transport** (`server_shell_helper_sse.py`, `client_with_servers_sse.py`)
- Uses FastAPI + sse-starlette
- Communication: HTTP POST + Server-Sent Events
- Deployment: Standalone HTTP service on port 8000
- Config: `mcp_servers_sse.json` with `url`/`transport`
- Endpoints: `GET /sse`, `POST /sse/messages`, `GET /health`

**3. FastAPI REST API** (`api/main.py`, `api/agent.py`, `api/models.py`)
- Pure REST API without MCP protocol
- Endpoints:
  - `GET /platform` - Get OS platform info
  - `POST /execute` - Execute command with explicit platform
  - `POST /quick` - Auto-detect platform and execute
- Models defined in Pydantic (`ShellCommand`, `ShellResponse`, `PlatformResponse`)

### Core Execution Logic

All three interfaces use the same shell execution pattern:

```python
# Windows: PowerShell with args array
args = ['powershell', '-Command', shell_command]

# *nix: Direct shell execution
args = shell_command

# Real-time execution
process = subprocess.Popen(args, shell=True, stdout=PIPE, stderr=PIPE, text=True)
# Stream output line-by-line for real-time results
```

Location of execution logic:
- MCP Stdio: `server_shell_helper.py:shell_helper()` (lines 23-75)
- MCP SSE: `server_shell_helper_sse.py:shell_helper_impl()` (lines 58-99)
- FastAPI REST: `api/agent.py:ShellAgent.execute_command()` (lines 15-49)

### MCP Client Integration

Both MCP clients integrate with OpenAI's API to provide LLM-powered shell command generation:

**Flow:**
1. Load server configs from JSON
2. Connect to MCP server(s) and discover tools
3. Enter chat loop accepting user natural language input
4. LLM generates function calls to discovered MCP tools
5. Client executes tool calls via MCP protocol
6. Results returned to LLM for final response

**Key difference:** Stdio uses `stdio_client()` context manager, SSE uses `httpx.AsyncClient` with manual SSE parsing.

### Configuration Files

- `mcp_servers.json` - Stdio servers with `command` and `args`
- `mcp_servers_sse.json` - SSE servers with `url` and `transport: "sse"`
- Both follow MCP server configuration format

### Transport Comparison

| Aspect | Stdio | SSE | REST API |
|--------|-------|-----|----------|
| Protocol | MCP/JSON-RPC | MCP/JSON-RPC | HTTP REST |
| Communication | stdin/stdout | HTTP + SSE | HTTP only |
| Deployment | Subprocess | HTTP service | HTTP service |
| Multi-client | No | Yes | Yes |
| Network | Local only | Network capable | Network capable |
| LLM Integration | Built-in | Built-in | External |

## Language Convention

The codebase uses **Traditional Chinese (繁體中文)** for:
- Code comments and docstrings
- User-facing messages and log output
- README and documentation

Maintain this language consistency when modifying code.
