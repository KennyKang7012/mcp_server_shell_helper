# Shell Helper API

這是一個跨平台的 Shell 指令執行輔助工具，基於 FastAPI 框架開發，可以在 Windows、Linux 和 macOS 上執行相應的 shell 指令。

## 功能特點

- 基於 FastAPI 的 RESTful API 設計
- 自動識別作業系統平台
- 支援 Windows PowerShell 和 Linux/macOS Shell 命令執行
- 非同步處理請求
- 完整的錯誤處理和超時機制
- 詳細的日誌記錄
- 系統資源監控功能
- Markdown 格式的監控報告

## 安裝步驟

1. 確保您已安裝 Python 3.11 或更新版本
2. 克隆此專案到本地端
3. 使用 `uv` 安裝依賴套件：

```bash
# 安裝主要相依套件
uv pip install fastapi uvicorn pydantic httpx

# 安裝測試相依套件
uv pip install pytest pytest-asyncio pytest-cov
```

## API 端點

### GET /platform
- 功能：取得目前系統平台資訊
- 返回：`{"platform": "Windows"}` 或 `{"platform": "*nix"}`

### POST /execute
- 功能：執行 shell 命令，需指定平台
- 請求體：
```json
{
    "platform": "Windows",
    "shell_command": "Get-Date"
}
```
- 返回：包含執行結果、返回碼和錯誤信息（如果有）

### POST /quick
- 功能：快速執行命令，自動偵測平台
- 請求體：
```json
{
    "shell_command": "echo 'Hello World'"
}
```
- 返回：與 /execute 相同的結果格式

## 監控功能使用

### 基本監控
```bash
python test_quick_endpoint.py
```

### 自定義監控參數
```bash
# 設定監控間隔和持續時間
python test_quick_endpoint.py -i 60 -d 120

# 設定超時和目標主機
python test_quick_endpoint.py -t 45 --host remote.server --port 8080
```

### 監控參數選項

| 參數 | 說明 | 預設值 |
|------|------|--------|
| -i, --interval | 監控間隔（秒） | 300 |
| -t, --timeout | 請求超時時間（秒） | 30 |
| -d, --duration | 監控持續時間（分鐘） | 無限制 |
| --host | 目標主機位址 | localhost |
| --port | API 服務端口 | 8000 |

## 使用範例

### 1. 啟動服務
```bash
# 使用 run.py
python run.py

# 或直接使用 uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 基本命令執行
```python
import httpx
import asyncio

async def test_command():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/quick",
            json={"shell_command": "echo 'Hello from Shell Helper!'"}
        )
        print(response.json())

asyncio.run(test_command())
```

### 3. 系統監控範例
```python
# 執行 30 分鐘的系統監控，每 5 分鐘一次
python test_quick_endpoint.py -i 300 -d 30
```

### 4. 遠端監控範例
```python
# 監控遠端伺服器，設定 60 秒超時
python test_quick_endpoint.py --host remote.server --port 8000 -t 60
```

## 注意事項

1. **安全性考慮**
   - 預設只監聽 localhost
   - 生產環境建議設置適當的防火牆規則
   - 考慮實作認證機制

2. **效能最佳化**
   - 監控間隔建議不要小於 60 秒
   - 根據網路狀況調整超時時間
   - 大量請求時建議使用非同步客戶端

3. **錯誤處理**
   - 所有 API 呼叫都有適當的錯誤處理
   - 超時機制可防止程式懸死
   - 詳細的錯誤日誌記錄

4. **監控報告**
   - 報告存放在 `quick_endpoint_test_results.md`
   - JSON 格式的原始數據另存為時間戳記檔案
   - 日誌檔案格式為 `monitoring_YYYYMMDD.log`

5. **相容性**
   - Windows 上使用 PowerShell 指令
   - Linux/macOS 上使用標準 Shell 指令
   - 注意跨平台指令的相容性

6. **資源使用**
   - 監控記憶體使用時會列出前 30 個最耗記憶體的程序
   - 長時間運行時注意日誌檔案大小
   - 考慮實作日誌輪替機制

## 開發測試

```bash
# 執行所有測試
uv run pytest tests/ -v

# 執行特定測試檔案
uv run pytest tests/test_api.py -v
uv run pytest tests/test_shell_agent.py -v

# 執行含覆蓋率報告的測試
uv run pytest tests/ --cov=api -v
```

## 文件參考

- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [Pydantic 文檔](https://pydantic-docs.helpmanual.io/)
- [HTTPX 文檔](https://www.python-httpx.org/)
- [PowerShell 命令參考](https://docs.microsoft.com/en-us/powershell/)

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
