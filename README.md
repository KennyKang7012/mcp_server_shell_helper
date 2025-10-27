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
- **即時監控儀表板**
  - 視覺化測試結果展示
  - 智能表格解析與格式化
  - 支援 PowerShell Format-Table 輸出
  - 響應式設計，美觀易用

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

### GET /dashboard
- 功能：即時監控儀表板
- 說明：提供視覺化的測試結果展示介面
- 特色：
  - 📊 即時顯示測試統計（總數、成功率等）
  - 📋 測試結果時間線展示
  - 🔍 過濾器（全部/成功/失敗）
  - 📈 智能表格解析，完美顯示 PowerShell Format-Table 輸出
  - 🎨 美觀的紫色漸層設計
  - 📱 響應式布局，支援各種螢幕尺寸

### GET /api/test-results/raw
- 功能：取得原始測試結果（Markdown 格式）
- 返回：JSON 字符串格式的 Markdown 內容

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

### 2. 開啟監控儀表板
```bash
# 啟動服務後，在瀏覽器中開啟
http://localhost:8000/dashboard

# 或使用提供的腳本自動開啟
python open_dashboard.py
```

**儀表板功能說明：**
- **測試統計卡片**：顯示總測試數、成功數、失敗數和成功率
- **過濾器**：可按狀態（全部/成功/失敗）或時間範圍篩選測試結果
- **展開/收合**：點擊測試項目可查看詳細資訊
- **批量操作**：使用「展開全部」或「收合全部」按鈕快速管理所有測試項目
- **表格智能解析**：自動識別並美化 PowerShell Format-Table 輸出
  - 支援 3-6 位數的 PID 顯示
  - 自動對齊數值列（右對齊）
  - 完整顯示所有欄位（ProcessName、PID、Memory(GB)、CPU(s) 等）

### 3. 基本命令執行
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

### 4. 系統監控範例
```bash
# 執行 30 分鐘的系統監控，每 5 分鐘一次
python test_quick_endpoint.py -i 300 -d 30

# 監控結果會自動保存到 quick_endpoint_test_results.md
# 可在儀表板 (http://localhost:8000/dashboard) 查看即時視覺化結果
```

### 5. 遠端監控範例
```bash
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
   - 可透過儀表板即時查看視覺化結果

5. **儀表板使用**
   - 首次開啟儀表板時，需先執行測試以產生數據
   - 儀表板會自動解析 Markdown 格式的測試結果
   - 支援即時刷新，無需重啟服務
   - 表格解析支援 PowerShell Format-Table 格式
   - 瀏覽器建議使用 Chrome、Edge 或 Firefox 最新版本

6. **相容性**
   - Windows 上使用 PowerShell 指令
   - Linux/macOS 上使用標準 Shell 指令
   - 注意跨平台指令的相容性

7. **資源使用**
   - 監控記憶體使用時會列出前 30 個最耗記憶體的程序
   - 長時間運行時注意日誌檔案大小
   - 考慮實作日誌輪替機制
   - 儀表板靜態資源（CSS/HTML）會快取以提升效能

## 儀表板技術細節

### 表格解析演算法
儀表板實作了智能表格解析功能，能夠正確處理 PowerShell `Format-Table -AutoSize` 產生的表格：

1. **列位置偵測**：根據分隔線（`---`）確定每個欄位的邊界
2. **靈活數據提取**：從分隔線位置向前搜索最多 10 個字符，確保不會遺漏超出邊界的數據
3. **智能欄位識別**：
   - 第一欄（ProcessName）：提取所有非數字的單詞組合
   - 其他欄位：提取最靠近該欄位位置的數值
4. **完整性驗證**：確保所有欄位（PID、Memory、CPU 等）都能正確解析

### 樣式設計
- **漸層效果**：使用紫色漸層（#667eea → #764ba2）營造現代感
- **響應式表格**：自動調整欄位寬度，支援 3-6 位數 PID 顯示
- **視覺回饋**：hover 效果、展開動畫、狀態標籤顏色編碼
- **可讀性優化**：數值欄位右對齊、等寬字體、適當的行距和留白

### 檔案結構
```
api/
├── templates/
│   └── dashboard.html      # 儀表板 HTML + JavaScript（620 行）
└── static/
    └── dashboard.css       # 儀表板樣式表（801 行）
```

#### dashboard.html 內容結構（620 行）

**1. HTML 頭部和元信息（1-20 行）**
- 文檔聲明和基本 meta 標籤
- 頁面標題設定
- CSS 樣式表引入

**2. 頁面布局和 DOM 結構（21-150 行）**
- **標題區域**：Shell Helper API 測試儀表板
- **統計卡片區**：總測試數、成功數、失敗數、成功率
- **控制面板**：
  - 批量操作按鈕（展開全部/收合全部）
  - 狀態過濾器（全部/成功/失敗）
  - 時間範圍過濾器和刷新間隔設定
- **測試結果時間線**：測試項目容器（動態生成）

**3. JavaScript 核心代碼（151-618 行）**

**3.1 格式化輸出函數（151-258 行）**
- `formatOutput(output)`: 主要格式化入口，處理測試輸出結果
  - 識別分段標題（以 `=====` 包圍）
  - 識別鍵值對（`key: value` 格式）
  - 偵測並解析表格
  - 處理空行和一般文本
- `parseTable(lines, startIndex)`: 解析 PowerShell Format-Table 輸出（核心演算法）

**3.2 表格解析函數（261-361 行）**
- **列位置偵測**：分析分隔線（`---`）確定欄位邊界
- **表頭提取**：從 headerLine 提取欄位名稱
- **智能數據提取**：
  - 從分隔線位置向前搜索 10 個字符
  - 第一欄（ProcessName）：提取所有非數字單詞組合
  - 其他欄位：提取最靠近該欄位位置的數值
- **HTML 表格生成**：輸出格式化的 HTML table

**3.3 Markdown 解析函數（363-400 行）**
- `parseTestResults(markdown)`: 解析 Markdown 格式測試結果
  - 按 `=====` 分割不同測試報告
  - 提取測試時間、執行時間、命令、平台等信息
  - 使用正則表達式匹配 Markdown 粗體標記（`**text**`）
  - 提取輸出結果（處理代碼塊 ` ``` `）
  - 構建測試對象數組

**3.4 渲染和顯示函數（403-485 行）**
- `updateSummaryCards(tests)`: 更新統計卡片（總數、成功率等）
- `renderTestItem(test, index)`: 渲染單個測試項目
  - 生成測試卡片 HTML
  - 包含狀態標籤、執行時間、平台信息
  - 可展開/收合的詳細信息區
  - 格式化輸出展示
- `renderAllTests()`: 渲染所有測試項目並應用過濾器
- `toggleTest(index)`: 切換單個測試項目的展開狀態
- `toggleAllTests()`: 批量展開或收合所有測試
- `filterByStatus(status)`: 按狀態過濾測試結果
- `filterByTimeRange(hours)`: 按時間範圍過濾

**3.5 數據加載和刷新（488-617 行）**
- `loadTestResults()`: 從 API 載入測試結果
  - 發送 GET 請求到 `/api/test-results/raw`
  - JSON 解析返回的 Markdown 內容
  - 調用 `parseTestResults()` 解析數據
  - 更新頁面顯示和最後更新時間
  - 錯誤處理和重試機制
- `saveSettings()`: 保存刷新間隔設定到 localStorage
- `loadSettings()`: 從 localStorage 載入設定
- `startAutoRefresh()`: 啟動自動刷新機制
- `stopAutoRefresh()`: 停止自動刷新
- **事件監聽器**：
  - `DOMContentLoaded`: 頁面載入完成時初始化
  - `beforeunload`: 頁面卸載時清理
  - `visibilitychange`: 頁面可見性變化時控制刷新

**4. 結束標籤（619-620 行）**
- `</body>` 和 `</html>` 標籤

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
