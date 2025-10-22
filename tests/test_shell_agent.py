import os
import sys
import pytest
from fastapi import HTTPException
import platform

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.agent import ShellAgent

@pytest.fixture
def shell_agent():
    """建立 ShellAgent 實例的 fixture"""
    return ShellAgent()

class TestShellAgent:
    def test_get_platform(self, shell_agent):
        """測試平台檢測功能"""
        current_system = platform.system()
        platform_type = shell_agent.get_platform()
        
        if current_system == "Windows":
            assert platform_type == "Windows"
        elif current_system in ["Linux", "Darwin"]:
            assert platform_type == "*nix"
        else:
            assert platform_type == "Unknown"

    @pytest.mark.asyncio
    async def test_execute_command_windows(self, shell_agent):
        """測試 Windows 平台指令執行"""
        if platform.system() != "Windows":
            pytest.skip("此測試只在 Windows 平台執行")
        
        result = await shell_agent.execute_command("Windows", "echo 'Hello World'")
        assert result["return_code"] == 0
        assert "Hello World" in result["output"]
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_execute_command_unix(self, shell_agent):
        """測試 Unix 平台指令執行"""
        if platform.system() not in ["Linux", "Darwin"]:
            pytest.skip("此測試只在 Unix-like 平台執行")
        
        result = await shell_agent.execute_command("*nix", "echo 'Hello World'")
        assert result["return_code"] == 0
        assert "Hello World" in result["output"]
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_invalid_platform(self, shell_agent):
        """測試無效的平台參數"""
        with pytest.raises(HTTPException) as exc_info:
            await shell_agent.execute_command("invalid", "echo test")
        assert exc_info.value.status_code == 400
        assert "不支援的作業系統平台" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_command_error(self, shell_agent):
        """測試指令執行錯誤的情況"""
        platform_type = "Windows" if platform.system() == "Windows" else "*nix"
        invalid_command = "invalid_command_123"
        
        result = await shell_agent.execute_command(platform_type, invalid_command)
        assert result["return_code"] != 0
        assert result["error"] is not None