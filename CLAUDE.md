# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shell Helper is a cross-platform shell command execution tool built on the Model Context Protocol (MCP). It automatically detects the operating system and executes PowerShell commands on Windows or shell commands on Linux/macOS, returning results in real-time.

The project now supports **two transport mechanisms**:
1. **Stdio Transport** (Original) - Local process communication via stdin/stdout
2. **SSE Transport** (New) - HTTP-based communication with Server-Sent Events

### Components

**Stdio Transport (Local):**
- Server: [server_shell_helper.py](server_shell_helper.py) - Uses FastMCP framework
- Client: [client_with_servers.py](client_with_servers.py) - Launches servers as subprocesses
- Config: [mcp_servers.json](mcp_servers.json)

**SSE Transport (Network):**
- Server: [server_shell_helper_sse.py](server_shell_helper_sse.py) - FastAPI-based HTTP server
- Client: [client_with_servers_sse.py](client_with_servers_sse.py) - HTTP/SSE client
- Config: [mcp_servers_sse.json](mcp_servers_sse.json)

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv pip install fastapi uvicorn sse-starlette httpx mcp openai python-dotenv
```

### Running the Application

**Stdio Transport (Local):**
```bash
# Start server (managed by client)
python client_with_servers.py
```

**SSE Transport (Network):**
```bash
# Terminal 1: Start HTTP server
uv run python server_shell_helper_sse.py
# Or with uvicorn directly:
uvicorn server_shell_helper_sse:app --host 0.0.0.0 --port 8000

# Terminal 2: Start client
uv run python client_with_servers_sse.py
```

**Testing SSE Server:**
```bash
# Health check
curl http://localhost:8000/health

# Test tools list
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Test get_platform
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_platform", "arguments": {}}}'
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `OPENAI_API_KEY` - Required for the client to use OpenAI's API

## Architecture

### Core Tools
Both transport mechanisms expose the same two tools:
- `get_platform()` - Returns the current OS platform (Windows, *nix, or Unknown)
- `shell_helper(platform, shell_command)` - Executes shell commands based on platform
  - Uses `subprocess.Popen` with real-time stdout/stderr capture
  - Windows: Executes via PowerShell
  - *nix: Executes directly in shell

### Stdio Transport Architecture

**Server** ([server_shell_helper.py](server_shell_helper.py)):
- Uses FastMCP framework
- Runs as subprocess launched by client
- Communicates via stdin/stdout with newline-delimited JSON-RPC messages
- Launched with `mcp.run(transport='stdio')`

**Client** ([client_with_servers.py](client_with_servers.py)):
- `MCPClient` class manages stdio connections
- Uses `StdioServerParameters` and `stdio_client` from MCP SDK
- Launches servers as child processes via configuration

### SSE Transport Architecture

**Server** ([server_shell_helper_sse.py](server_shell_helper_sse.py)):
- FastAPI application with two endpoints:
  - `GET /sse` - SSE streaming endpoint (server-to-client)
  - `POST /sse/messages` - Message endpoint (client-to-server)
  - `GET /health` - Health check endpoint
- Implements JSON-RPC 2.0 protocol manually
- Supports multiple concurrent clients
- Sends heartbeat pings every 5 seconds to maintain connections
- Returns message URL in initial SSE event

**Client** ([client_with_servers_sse.py](client_with_servers_sse.py)):
- `SSEMCPClient` class manages HTTP/SSE connections
- Uses `httpx.AsyncClient` for HTTP communication
- Connects to SSE endpoint to receive message URL
- Sends JSON-RPC requests via HTTP POST
- Implements tool discovery and invocation via HTTP

**Client Flow:**
1. Load server configs from configuration file
2. Connect to SSE endpoint and extract message URL
3. Send initialization request via HTTP POST
4. Fetch available tools via HTTP POST
5. Enter chat loop with OpenAI integration
6. Route tool calls to appropriate servers
7. Return results to LLM for response generation

### Configuration Files
- [mcp_servers.json](mcp_servers.json) - Stdio transport (command/args format)
- [mcp_servers_sse.json](mcp_servers_sse.json) - SSE transport (url/transport format)

### Key Differences

| Aspect | Stdio | SSE |
|--------|-------|-----|
| Communication | Process stdin/stdout | HTTP + SSE |
| Deployment | Subprocess per client | Standalone HTTP service |
| Multi-client | No (1:1 process) | Yes (shared server) |
| Network | Local only | Local or remote |
| Dependencies | FastMCP | FastAPI, uvicorn, sse-starlette |
| Use Case | Development, CLI tools | Production, remote access |

See [SSE_MIGRATION.md](SSE_MIGRATION.md) for detailed migration guide and testing instructions.

## Language and Documentation

The codebase uses Traditional Chinese (繁體中文) for:
- Code comments and docstrings
- User-facing messages and output
- README and documentation

When modifying code, maintain consistency with existing Traditional Chinese text.
