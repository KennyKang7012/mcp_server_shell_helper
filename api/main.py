from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import aiofiles
import os
from pathlib import Path
from .agent import ShellAgent
from .models import ShellCommand, ShellResponse, PlatformResponse

app = FastAPI(
    title="Shell Helper API",
    description="提供跨平台執行 shell 命令的 API 服務",
    version="1.0.0"
)

# 設定靜態文件和模板目錄
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 測試結果文件路徑（位於專案根目錄）
TEST_RESULTS_FILE = BASE_DIR.parent / "quick_endpoint_test_results.md"

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

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """儀表板頁面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/test-results/raw")
async def get_test_results_raw():
    """獲取原始 Markdown 格式的測試結果"""
    if not TEST_RESULTS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="測試結果文件不存在。請先執行 test_quick_endpoint.py 生成測試結果。"
        )

    try:
        async with aiofiles.open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
        return content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"讀取測試結果文件時發生錯誤：{str(e)}"
        )
