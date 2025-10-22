import os
import sys
import pytest
from fastapi.testclient import TestClient
import platform

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

@pytest.fixture
def client():
    """建立測試用的 FastAPI 客戶端"""
    return TestClient(app)

def test_get_platform(client):
    """測試 GET /platform 端點"""
    response = client.get("/platform")
    assert response.status_code == 200
    assert "platform" in response.json()
    
    current_system = platform.system()
    if current_system == "Windows":
        assert response.json()["platform"] == "Windows"
    elif current_system in ["Linux", "Darwin"]:
        assert response.json()["platform"] == "*nix"

def test_execute_command(client):
    """測試 POST /execute 端點"""
    current_platform = "Windows" if platform.system() == "Windows" else "*nix"
    command = "echo 'test command'"
    
    response = client.post(
        "/execute",
        json={"platform": current_platform, "shell_command": command}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["return_code"] == 0
    assert result["error"] is None
    assert "test command" in result["output"]

def test_quick_execute_with_platform(client):
    """測試 POST /quick 端點（指定平台）"""
    current_platform = "Windows" if platform.system() == "Windows" else "*nix"
    command = "echo 'quick test'"
    
    response = client.post(
        "/quick",
        json={"platform": current_platform, "shell_command": command}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["platform"] == current_platform
    assert result["result"]["return_code"] == 0
    assert result["result"]["error"] is None
    assert "quick test" in result["result"]["output"]

def test_quick_execute_auto_platform(client):
    """測試 POST /quick 端點（自動檢測平台）"""
    command = "echo 'auto platform test'"
    
    response = client.post(
        "/quick",
        json={"platform": None, "shell_command": command}
    )
    
    assert response.status_code == 200
    result = response.json()
    current_system = platform.system()
    if current_system == "Windows":
        assert result["platform"] == "Windows"
    elif current_system in ["Linux", "Darwin"]:
        assert result["platform"] == "*nix"
    assert result["result"]["return_code"] == 0
    assert "auto platform test" in result["result"]["output"]

def test_quick_execute_invalid_command(client):
    """測試 POST /quick 端點（無效命令）"""
    current_platform = "Windows" if platform.system() == "Windows" else "*nix"
    
    response = client.post(
        "/quick",
        json={"platform": current_platform, "shell_command": "invalid_command_123"}
    )
    
    assert response.status_code == 200  # API 仍應回傳 200
    result = response.json()
    assert result["platform"] == current_platform
    assert result["result"]["return_code"] != 0  # 命令應該失敗
    assert result["result"]["error"] is not None  # 應該有錯誤訊息