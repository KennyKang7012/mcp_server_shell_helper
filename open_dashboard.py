"""
簡單的儀表板啟動腳本
使用系統預設瀏覽器打開儀表板，並執行基本驗證
"""
import webbrowser
import httpx
import time
import argparse
from datetime import datetime


def check_server(host: str = "localhost", port: int = 8000, timeout: int = 5):
    """檢查服務器是否運行"""
    url = f"http://{host}:{port}/platform"
    try:
        response = httpx.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        return False


def open_dashboard_in_browser(host: str = "localhost", port: int = 8000):
    """在瀏覽器中打開儀表板"""
    dashboard_url = f"http://{host}:{port}/dashboard"

    print("=" * 60)
    print("Shell Helper Dashboard Launcher")
    print("=" * 60)

    # 檢查服務器
    print(f"\n[CHECK] Checking server status ({host}:{port})...")
    if check_server(host, port):
        print("[OK] Server is running")
    else:
        print("[ERROR] Server is not running!")
        print(f"\nPlease start the server first:")
        print(f"  python run.py")
        print(f"  or")
        print(f"  uv run uvicorn api.main:app --host 0.0.0.0 --port {port} --reload")
        return False

    # 打開瀏覽器
    print(f"\n[OPEN] Opening dashboard: {dashboard_url}")
    try:
        webbrowser.open(dashboard_url)
        print("[OK] Dashboard opened in browser!")

        print("\n[TIPS] Usage tips:")
        print("  1. Click test cards to expand/collapse details")
        print("  2. Use 'Expand All' button to expand all tests")
        print("  3. Use filter buttons to filter success/failure tests")
        print("  4. Use refresh interval settings to adjust update frequency")
        print("  5. Dashboard auto-refreshes every 5 seconds (adjustable)")

        return True
    except Exception as e:
        print(f"[ERROR] Failed to open browser: {str(e)}")
        print(f"\nPlease visit manually: {dashboard_url}")
        return False


async def verify_dashboard_api(host: str = "localhost", port: int = 8000):
    """驗證儀表板 API 端點"""
    base_url = f"http://{host}:{port}"

    print("\n[VERIFY] Verifying API endpoints...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 測試平台端點
        try:
            response = await client.get(f"{base_url}/platform")
            if response.status_code == 200:
                print(f"  [OK] /platform - {response.json()}")
            else:
                print(f"  [ERROR] /platform - HTTP {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] /platform - {str(e)}")

        # 測試儀表板端點
        try:
            response = await client.get(f"{base_url}/dashboard")
            if response.status_code == 200:
                print(f"  [OK] /dashboard - HTML page")
            else:
                print(f"  [ERROR] /dashboard - HTTP {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] /dashboard - {str(e)}")

        # 測試測試結果端點
        try:
            response = await client.get(f"{base_url}/api/test-results/raw")
            if response.status_code == 200:
                content = response.text
                lines = content.count('\n')
                print(f"  [OK] /api/test-results/raw - OK ({lines} lines)")
            else:
                print(f"  [ERROR] /api/test-results/raw - HTTP {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] /api/test-results/raw - {str(e)}")


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(description="儀表板啟動器")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="服務器主機（預設：localhost）"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服務器埠號（預設：8000）"
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="不自動打開瀏覽器，僅驗證"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="執行 API 端點驗證"
    )

    return parser.parse_args()


async def main():
    args = parse_arguments()

    # 驗證 API（如果要求）
    if args.verify:
        await verify_dashboard_api(args.host, args.port)

    # 打開瀏覽器（除非禁用）
    if not args.no_open:
        success = open_dashboard_in_browser(args.host, args.port)
        if success:
            print("\n[DONE] Please view the dashboard in your browser.")
            print(f"[TIP] Press Ctrl+F5 to force refresh and load latest updates.")
    else:
        print(f"\n[INFO] Dashboard URL: http://{args.host}:{args.port}/dashboard")


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Operation cancelled")
