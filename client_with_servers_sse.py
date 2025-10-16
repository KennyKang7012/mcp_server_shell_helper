import httpx
import asyncio
import json
import sys
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# 載入 .env 檔案
load_dotenv()

openai = OpenAI()

# 讀取 API 金鑰
api_key = os.getenv("OPENAI_API_KEY")

# 設置 OpenAI API
openai.api_key = api_key

class SSEMCPClient:
    """SSE Transport 的 MCP 客戶端"""

    def __init__(self):
        self.session_id = 0
        self.message_url: Optional[str] = None
        self.tools = []
        self.tool_names = []
        self.http_client: Optional[httpx.AsyncClient] = None
        self.server_name: Optional[str] = None

    async def connect_to_server(self, server_info: tuple):
        """連接到 SSE MCP 伺服器

        Args:
            server_info: (伺服器名稱, 伺服器配置) 的 tuple
        """
        self.server_name = server_info[0]
        server_config = server_info[1]
        sse_url = server_config.get("url")

        if not sse_url:
            raise ValueError(f"伺服器 {self.server_name} 缺少 URL 配置")

        # 建立 HTTP 客戶端
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # 連接到 SSE 端點並取得 message URL
        try:
            async with self.http_client.stream("GET", sse_url) as response:
                if response.status_code != 200:
                    raise Exception(f"連接失敗: HTTP {response.status_code}")

                # 讀取第一個事件（endpoint 資訊）
                async for line in response.aiter_lines():
                    line = line.strip()

                    if line.startswith("event:"):
                        event_type = line.split(":", 1)[1].strip()

                    elif line.startswith("data:"):
                        data = line.split(":", 1)[1].strip()

                        if event_type == "endpoint":
                            endpoint_info = json.loads(data)
                            self.message_url = endpoint_info.get("url")
                            # 取得 message URL 後就可以中斷 SSE 連接
                            break

                if not self.message_url:
                    raise Exception("未能從 SSE 端點取得 message URL")

        except Exception as e:
            if self.http_client:
                await self.http_client.aclose()
            raise Exception(f"連接 SSE 伺服器失敗: {str(e)}")

        # 初始化連接
        init_response = await self._send_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "shell_helper_client",
                    "version": "0.1.0"
                }
            }
        })

        if "error" in init_response:
            raise Exception(f"初始化失敗: {init_response['error']}")

        # 取得工具列表
        tools_response = await self._send_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        })

        if "error" in tools_response:
            raise Exception(f"取得工具列表失敗: {tools_response['error']}")

        # 轉換工具格式為 OpenAI 相容格式
        tools_data = tools_response.get("result", {}).get("tools", [])
        self.tools = [{
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["inputSchema"]
        } for tool in tools_data]
        self.tool_names = [tool["name"] for tool in tools_data]

        print('-' * 20)
        print(f"已連接 {self.server_name} 伺服器 (SSE)")
        print(f"Message URL: {self.message_url}")
        print('\n'.join([f'    - {name}' for name in self.tool_names]))
        print('-' * 20)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """呼叫 MCP 工具

        Args:
            tool_name: 工具名稱
            arguments: 工具參數

        Returns:
            工具執行結果
        """
        response = await self._send_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        })

        if "error" in response:
            raise Exception(f"工具呼叫失敗: {response['error']}")

        return response.get("result")

    async def _send_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """發送 JSON-RPC 請求到伺服器

        Args:
            request_data: JSON-RPC 請求資料

        Returns:
            JSON-RPC 回應資料
        """
        if not self.http_client or not self.message_url:
            raise Exception("客戶端未連接")

        try:
            response = await self.http_client.post(
                self.message_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise Exception(f"HTTP 請求失敗: {str(e)}")

    def _next_id(self) -> int:
        """產生下一個請求 ID"""
        self.session_id += 1
        return self.session_id

    async def cleanup(self):
        """清理資源"""
        if self.http_client:
            await self.http_client.aclose()

async def get_reply_text(clients: List[SSEMCPClient], query: str, prev_id: Optional[str]):
    """單次問答"""

    messages = [{"role": "user", "content": query}]

    # 把 clients 中個別項目的 tools 串接在一起
    tools = []
    for client in clients:
        tools += client.tools

    while True:
        # 使用 Responses API 請 LLM 生成回覆
        response = openai.responses.create(
            # model="gpt-4.1-mini",
            # model="gpt-4.1",
            model="gpt-4.1-nano",
            input=messages,
            tools=tools,
            previous_response_id=prev_id,
        )

        # 處理回應並執行工具
        final_text = []
        messages = []

        prev_id = response.id
        for output in response.output:
            if output.type == 'message':  # 一般訊息
                final_text.append(output.content[0].text)
            elif output.type == 'function_call':  # 使用工具
                tool_name = output.name
                tool_args = eval(output.arguments)

                # 尋找擁有此工具的客戶端
                client = None
                for c in clients:
                    if tool_name in c.tool_names:
                        client = c
                        break

                if not client:
                    # 如果沒有找到對應的工具，則跳過
                    continue

                print(f"準備使用 {tool_name}(**{tool_args})")
                print('-' * 20)

                # 使用 MCP 伺服器提供的工具
                try:
                    result = await client.call_tool(tool_name, tool_args)
                    result_text = result.get("content", [{}])[0].get("text", "")
                    print(f"{result_text}")
                except Exception as e:
                    result_text = f"工具執行錯誤: {str(e)}"
                    print(f"錯誤: {result_text}")

                print('-' * 20)

                messages.append({
                    # 建立可傳回函式執行結果的字典
                    "type": "function_call_output",  # 設為工具輸出類型的訊息
                    "call_id": output.call_id,  # 叫用函式的識別碼
                    "output": result_text  # 函式傳回值
                })

        if messages == []:
            break

    return "\n".join(final_text), prev_id

async def chat_loop(clients: List[SSEMCPClient]):
    """聊天迴圈"""
    print("直接按 ↵ 可結束對話")

    prev_id = None
    while True:
        try:
            query = input(">>> ").strip()

            if query == '':
                break

            reply, prev_id = await get_reply_text(clients, query, prev_id)
            print(reply)

        except Exception as e:
            print(f"\nError: {str(e)}")

async def main():
    """主程式"""

    if not os.path.exists("mcp_servers.json") or not os.path.isfile("mcp_servers.json"):
        print("Error: 找不到 mcp_servers.json 檔", file=sys.stderr)
        return

    with open("mcp_servers.json", "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
            server_infos = tuple(config.get('mcpServers', {}).items())
        except:
            print("Error: mcp_servers.json 檔案格式錯誤", file=sys.stderr)
            return

    if len(server_infos) == 0:
        print("Error: mcp_servers.json 檔案內沒有任何伺服器", file=sys.stderr)
        return

    clients = []
    try:
        # 連接所有 SSE 伺服器
        for server_info in server_infos:
            server_config = server_info[1]

            # 只處理 SSE transport 的伺服器
            if server_config.get("transport") == "sse" or "url" in server_config:
                client = SSEMCPClient()
                await client.connect_to_server(server_info)
                clients.append(client)
            else:
                print(f"警告: 跳過非 SSE 伺服器 {server_info[0]}")

        if not clients:
            print("Error: 沒有可用的 SSE 伺服器", file=sys.stderr)
            return

        # 開始聊天迴圈
        await chat_loop(clients)

    finally:
        # 清理所有客戶端資源
        for client in clients[::-1]:
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
