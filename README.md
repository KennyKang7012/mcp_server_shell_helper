# Shell Helper

這是一個跨平台的 Shell 指令執行輔助工具，可以在 Windows、Linux 和 macOS 上執行相應的 shell 指令。

## 專案描述

Shell Helper 是一個基於 Model Context Protocol (MCP) 的服務，提供以下功能：

- 自動識別作業系統平台
- 在 Windows 上執行 PowerShell 指令
- 在 Linux/macOS 上執行 Shell 指令
- 即時回傳指令執行結果和錯誤訊息
- 提供執行狀態和返回碼資訊

## 安裝步驟

1. 確保您已安裝 Python 3.11 或更新版本
2. 克隆此專案到本地端
3. 在專案根目錄執行以下指令安裝依賴套件：

   ```bash
   pip install .
   ```

## 使用說明

1. 啟動 MCP 伺服器：

   ```bash
   python server_shell_helper.py
   ```

2. 透過 MCP 客戶端呼叫服務：
   - `get_platform()`: 取得當前作業系統平台
   - `shell_helper(platform, shell_command)`: 執行 shell 指令
     - platform: "Windows" 或 "*nix"
     - shell_command: 要執行的指令

## 貢獻指南

1. Fork 此專案
2. 建立您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 授權資訊

此專案採用 MIT 授權 - 詳見 LICENSE 檔案了解更多資訊。
