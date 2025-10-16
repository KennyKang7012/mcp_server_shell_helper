# SSE Transport 遷移指南

本專案現在同時支援兩種 MCP 傳輸方式：

## 1. Stdio Transport (原始版本)

### 特點
- 本地進程通訊
- 客戶端啟動伺服器作為子程序
- 適合本地開發和 CLI 工具
- 低延遲、資源佔用少

### 使用方式

**啟動伺服器：**
```bash
python server_shell_helper.py
```

**啟動客戶端：**
```bash
python client_with_servers.py
```

**配置檔案：** `mcp_servers.json`
```json
{
    "mcpServers": {
        "shell_helper": {
            "command": "uv",
            "args": [
                "--directory",
                "/Users/kennykang/Desktop/VibeProj/shell_helper",
                "run",
                "server_shell_helper.py"
            ]
        }
    }
}
```

---

## 2. SSE Transport (HTTP Stream 新版本)

### 特點
- 網路通訊（HTTP + SSE）
- 伺服器作為獨立服務運行
- 支援遠端存取和多客戶端連接
- 適合生產環境和遠端部署

### 使用方式

**啟動伺服器：**
```bash
# 方式 1: 直接執行
python server_shell_helper_sse.py

# 方式 2: 使用 uvicorn（推薦）
uvicorn server_shell_helper_sse:app --host 0.0.0.0 --port 8000

# 方式 3: 背景執行
uvicorn server_shell_helper_sse:app --host 0.0.0.0 --port 8000 &
```

**啟動客戶端：**
```bash
python client_with_servers_sse.py
```

**配置檔案：** `mcp_servers_sse.json`
```json
{
    "mcpServers": {
        "shell_helper": {
            "url": "http://localhost:8000/sse",
            "transport": "sse"
        }
    }
}
```

---

## 從 Stdio 轉換到 SSE 的關鍵變更

### 1. 伺服器架構
- **Stdio**: 使用 `FastMCP` 框架，透過 `mcp.run(transport='stdio')` 啟動
- **SSE**: 使用 `FastAPI` 框架，實作兩個 HTTP 端點
  - `GET /sse` - SSE 串流端點（接收伺服器推送）
  - `POST /sse/messages` - 訊息端點（發送客戶端請求）

### 2. 客戶端通訊
- **Stdio**: 使用 `stdio_client` 和 `StdioServerParameters`
- **SSE**: 使用 `httpx.AsyncClient` 進行 HTTP 通訊

### 3. 訊息格式
- **Stdio**: 每行一個 JSON-RPC 訊息，用換行符分隔
- **SSE**:
  - SSE 事件格式（伺服器到客戶端）
  - JSON-RPC over HTTP POST（客戶端到伺服器）

### 4. 連接管理
- **Stdio**: 子程序生命週期管理
- **SSE**: HTTP 長連接、心跳機制、重連邏輯

---

## 測試

### 測試 SSE 伺服器健康狀態
```bash
curl http://localhost:8000/health
```

### 測試 SSE 端點
```bash
curl -N http://localhost:8000/sse
```

### 測試訊息端點（初始化）
```bash
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "0.1.0"
      }
    }
  }'
```

### 測試工具列表
```bash
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

### 測試工具呼叫 (get_platform)
```bash
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_platform",
      "arguments": {}
    }
  }'
```

### 測試工具呼叫 (shell_helper)
```bash
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "shell_helper",
      "arguments": {
        "platform": "*nix",
        "shell_command": "echo Hello from SSE"
      }
    }
  }'
```

---

## 注意事項

### 安全性
1. **身份驗證**: SSE 版本目前未實作身份驗證，生產環境需要加入 Token 驗證
2. **HTTPS**: 遠端部署建議使用 HTTPS
3. **CORS**: 如需跨域存取，需在 FastAPI 中設定 CORS

### 效能
1. **並發**: SSE 伺服器支援多客戶端，但需注意資源使用
2. **超時**: 已設定 30 秒 HTTP 超時，可依需求調整
3. **心跳**: SSE 連接每 5 秒發送心跳，保持連接活躍

### 部署
1. **進程管理**: 使用 `systemd` 或 `supervisor` 管理伺服器進程
2. **反向代理**: 建議使用 nginx 作為反向代理
3. **監控**: 可透過 `/health` 端點監控伺服器狀態

---

## 選擇建議

**選擇 Stdio 如果：**
- 純本地開發和測試
- 不需要遠端存取
- 希望簡單快速的設置

**選擇 SSE 如果：**
- 需要遠端存取
- 需要多客戶端同時連接
- 部署為網路服務
- 需要與其他系統整合

---

## 檔案對照表

| 功能 | Stdio 版本 | SSE 版本 |
|------|-----------|---------|
| 伺服器 | `server_shell_helper.py` | `server_shell_helper_sse.py` |
| 客戶端 | `client_with_servers.py` | `client_with_servers_sse.py` |
| 配置 | `mcp_servers.json` | `mcp_servers_sse.json` |
| 啟動方式 | 自動啟動子程序 | 獨立啟動伺服器 |

---

## 疑難排解

### SSE 連接失敗
1. 確認伺服器已啟動：`curl http://localhost:8000/health`
2. 檢查防火牆設定
3. 確認配置檔案中的 URL 正確

### 工具呼叫失敗
1. 檢查伺服器日誌
2. 確認 JSON-RPC 請求格式正確
3. 驗證工具參數符合 schema

### 客戶端超時
1. 增加 `httpx.AsyncClient` 的 timeout 設定
2. 檢查網路連線
3. 確認伺服器沒有卡住

---

## 未來改進方向

1. **HTTP Stream Transport**: MCP 最新規範已將 SSE 標記為棄用，建議升級至 HTTP Stream Transport
2. **身份驗證**: 加入 Bearer Token 或 API Key 驗證
3. **重連機制**: 客戶端實作自動重連邏輯
4. **錯誤處理**: 更完善的錯誤處理和日誌記錄
5. **監控指標**: 加入 Prometheus metrics

---

## 參考資源

- [MCP 規範文件](https://modelcontextprotocol.io/)
- [FastAPI 文件](https://fastapi.tiangolo.com/)
- [SSE-Starlette](https://github.com/sysid/sse-starlette)
