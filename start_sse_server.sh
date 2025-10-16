#!/bin/bash

# Shell Helper SSE 伺服器啟動腳本

echo "========================================="
echo "Shell Helper SSE Server"
echo "========================================="
echo ""
echo "正在啟動 SSE 伺服器於 http://0.0.0.0:8000"
echo ""
echo "可用端點:"
echo "  - GET  /health         健康檢查"
echo "  - GET  /sse            SSE 串流端點"
echo "  - POST /sse/messages   訊息接收端點"
echo ""
echo "按 Ctrl+C 停止伺服器"
echo "========================================="
echo ""

# 啟動伺服器
uv run uvicorn server_shell_helper_sse:app --host 0.0.0.0 --port 8000
