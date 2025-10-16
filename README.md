# Shell Helper

這是一個跨平台的 Shell 指令執行輔助工具，可以在 Windows、Linux 和 macOS 上執行相應的 shell 指令。

## 專案描述

Shell Helper 是一個基於 Model Context Protocol (MCP) 的服務，提供以下功能：

- 自動識別作業系統平台
- 在 Windows 上執行 PowerShell 指令
- 在 Linux/macOS 上執行 Shell 指令
- 即時回傳指令執行結果和錯誤訊息
- 提供執行狀態和返回碼資訊
- **支援兩種傳輸方式**: Stdio (本地) 和 SSE (網路)

## 安裝步驟

1. 確保您已安裝 Python 3.11 或更新版本
2. 克隆此專案到本地端
3. 在專案根目錄執行以下指令安裝依賴套件：

   ```bash
   uv pip install fastapi uvicorn sse-starlette httpx mcp openai python-dotenv
   ```

4. 複製 `.env.example` 為 `.env` 並設定 OpenAI API key（客戶端需要）

## 使用說明

### 方式一：Stdio Transport（本地使用）

直接啟動客戶端（會自動啟動伺服器）：

```bash
python client_with_servers.py
```

### 方式二：SSE Transport（網路使用）

**終端 1 - 啟動 SSE 伺服器：**

```bash
# 使用啟動腳本
./start_sse_server.sh

# 或直接執行
uv run python server_shell_helper_sse.py

# 或使用 uvicorn
uvicorn server_shell_helper_sse:app --host 0.0.0.0 --port 8000
```

**終端 2 - 啟動客戶端：**

```bash
uv run python client_with_servers_sse.py
```

### 測試 SSE 伺服器

```bash
# 健康檢查
curl http://localhost:8000/health

# 取得工具列表
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# 測試 get_platform 工具
curl -X POST http://localhost:8000/sse/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_platform", "arguments": {}}}'
```

## 可用工具

透過 MCP 客戶端可以呼叫以下工具：

- `get_platform()`: 取得當前作業系統平台
  - 返回: "Windows", "*nix", 或 "Unknown"

- `shell_helper(platform, shell_command)`: 執行 shell 指令
  - platform: "Windows" 或 "*nix"
  - shell_command: 要執行的指令

## 傳輸方式比較

| 特性 | Stdio Transport | SSE Transport |
|------|----------------|---------------|
| 通訊方式 | 本地進程 | HTTP + SSE |
| 適用場景 | 本地開發 | 網路服務 |
| 多客戶端 | ✗ | ✓ |
| 遠端存取 | ✗ | ✓ |
| 設定複雜度 | 低 | 中 |

詳細說明請參閱 [SSE_MIGRATION.md](SSE_MIGRATION.md)

## 文件

- [CLAUDE.md](CLAUDE.md) - 專案架構和開發指南
- [SSE_MIGRATION.md](SSE_MIGRATION.md) - SSE 遷移指南和測試說明
- [SSE_IMPLEMENTATION_SUMMARY.md](SSE_IMPLEMENTATION_SUMMARY.md) - SSE 實作總結

## 貢獻指南

1. Fork 此專案
2. 建立您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 授權資訊

此專案採用 MIT 授權 - 詳見 LICENSE 檔案了解更多資訊。
