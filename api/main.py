from fastapi import FastAPI
from .agent import ShellAgent
from .models import ShellCommand, ShellResponse, PlatformResponse

app = FastAPI(
    title="Shell Helper API",
    description="提供跨平台執行 shell 命令的 API 服務",
    version="1.0.0"
)

shell_agent = ShellAgent()

@app.get("/platform", response_model=PlatformResponse)
async def get_platform():
    """取得作業系統平台資訊"""
    return {"platform": shell_agent.get_platform()}

@app.post("/execute", response_model=ShellResponse)
async def execute_command(command: ShellCommand):
    """執行 shell 命令"""
    return await shell_agent.execute_command(command.platform, command.shell_command)

@app.post("/quick")
async def quick_execute(command: ShellCommand):
    """同時取得平台並執行命令，回傳平台與執行結果"""
    platform = command.platform or shell_agent.get_platform()
    result = await shell_agent.execute_command(platform, command.shell_command)
    return {"platform": platform, "result": result}
