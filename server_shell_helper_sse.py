from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import subprocess
import platform
import asyncio
import json
from typing import Dict, Any
import uuid

app = FastAPI(title="Shell Helper MCP Server")

# 儲存客戶端連接和訊息佇列
clients: Dict[str, asyncio.Queue] = {}

# 工具定義
TOOLS = [
    {
        "name": "get_platform",
        "description": "取得作業系統平台",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "shell_helper",
        "description": "可以依據 platform 指定的作業系統平台執行：Windows powershell 指令或是 Linux/MacOS shell 指令的工具函式",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "作業系統平台，\"Windows\" 為 Windows，\"*nix\" 為 Linux 或 MacOS",
                    "enum": ["Windows", "*nix"]
                },
                "shell_command": {
                    "type": "string",
                    "description": "要執行的指令，Windows 平台只接受 powershell 指令"
                }
            },
            "required": ["platform", "shell_command"]
        }
    }
]

async def get_platform_impl() -> str:
    """取得作業系統平台實作"""
    system = platform.system()
    if system == "Windows":
        return "Windows"
    elif system == "Linux" or system == "Darwin":
        return "*nix"
    else:
        return "Unknown"

async def shell_helper_impl(platform_param: str, shell_command: str) -> str:
    """執行 shell 指令的實作"""

    # 啟動子行程
    if platform_param == "Windows":
        args = ['powershell', '-Command', shell_command]
    elif platform_param == "*nix":
        args = shell_command
    else:
        return "不支援的作業系統平台"

    process = subprocess.Popen(
        args,
        shell=True,             # 在 shell 中執行
        stdout=subprocess.PIPE, # 擷取標準輸出
        stderr=subprocess.PIPE, # 擷取錯誤輸出
        text=True               # 以文字形式返回
    )

    result = '執行結果：\n\n```\n'

    # 即時讀取輸出
    while True:
        output = process.stdout.readline()
        # 如果沒有輸出且行程結束
        if output == '' and process.poll() is not None:
            break
        if output:
            result += output

    result += "```"

    # 檢查錯誤輸出
    error = process.stderr.read()
    if error:
        result += f"\n\n錯誤: {error}"

    # 等待行程結束並取得返回碼
    return_code = process.wait()
    result += f"\n\n命令執行完成，返回碼: {return_code}\n\n"

    return result

async def handle_jsonrpc_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """處理 JSON-RPC 請求"""
    method = request_data.get("method")
    params = request_data.get("params", {})
    request_id = request_data.get("id")

    try:
        if method == "initialize":
            # 初始化連接
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "shell_helper",
                        "version": "0.1.0"
                    }
                }
            }

        elif method == "tools/list":
            # 列出可用工具
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": TOOLS
                }
            }

        elif method == "tools/call":
            # 呼叫工具
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name == "get_platform":
                result = await get_platform_impl()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }

            elif tool_name == "shell_helper":
                platform_param = tool_args.get("platform")
                shell_command = tool_args.get("shell_command")
                result = await shell_helper_impl(platform_param, shell_command)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"工具不存在: {tool_name}"
                    }
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"方法不存在: {method}"
                }
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"內部錯誤: {str(e)}"
            }
        }

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE 端點 - 建立串流連接"""

    async def event_generator():
        # 為此客戶端建立唯一 ID 和訊息佇列
        client_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        clients[client_id] = queue

        try:
            # 發送初始端點資訊
            yield {
                "event": "endpoint",
                "data": json.dumps({
                    "url": f"{request.url.scheme}://{request.url.netloc}/sse/messages"
                })
            }

            # 保持連接並發送心跳
            while True:
                try:
                    # 等待訊息（帶超時）
                    message = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield {
                        "event": "message",
                        "data": json.dumps(message)
                    }
                except asyncio.TimeoutError:
                    # 發送心跳
                    yield {
                        "event": "ping",
                        "data": ""
                    }

                # 檢查客戶端是否斷開連接
                if await request.is_disconnected():
                    break

        finally:
            # 清理客戶端
            if client_id in clients:
                del clients[client_id]

    return EventSourceResponse(event_generator())

@app.post("/sse/messages")
async def message_endpoint(request: Request):
    """訊息端點 - 接收客戶端的 JSON-RPC 請求"""

    try:
        request_data = await request.json()
        response_data = await handle_jsonrpc_request(request_data)
        return JSONResponse(content=response_data)

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "解析錯誤：無效的 JSON"
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"內部錯誤: {str(e)}"
                }
            }
        )

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "server": "shell_helper",
        "version": "0.1.0",
        "active_clients": len(clients)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
