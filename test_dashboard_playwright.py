"""
Playwright 自動化測試腳本 - 儀表板截圖和驗證
"""
import asyncio
from playwright.async_api import async_playwright
import argparse
from datetime import datetime
import os


async def test_dashboard(
    url: str = "http://localhost:8000/dashboard",
    headless: bool = False,
    screenshot_dir: str = "screenshots",
    expand_tests: bool = True
):
    """
    自動化測試儀表板

    Args:
        url: 儀表板 URL
        headless: 是否使用無頭模式
        screenshot_dir: 截圖保存目錄
        expand_tests: 是否展開所有測試項目
    """
    # 創建截圖目錄
    os.makedirs(screenshot_dir, exist_ok=True)

    async with async_playwright() as p:
        # 啟動瀏覽器
        print(f"🚀 啟動瀏覽器 (無頭模式: {headless})...")
        browser = await p.chromium.launch(headless=headless)

        # 創建新頁面
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            # 訪問儀表板
            print(f"📱 訪問儀表板: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)

            # 等待內容載入
            print("⏳ 等待內容載入...")
            await page.wait_for_selector('.summary-cards', timeout=10000)
            await asyncio.sleep(2)  # 額外等待以確保所有資源載入

            # 截圖 - 初始狀態
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"{screenshot_dir}/dashboard_initial_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 初始狀態截圖已保存: {screenshot_path}")

            # 獲取統計數據
            total_tests = await page.locator('#total-tests').inner_text()
            success_tests = await page.locator('#success-tests').inner_text()
            failure_tests = await page.locator('#failure-tests').inner_text()
            success_rate = await page.locator('#success-rate').inner_text()

            print(f"\n📊 儀表板統計:")
            print(f"  總測試數: {total_tests}")
            print(f"  成功: {success_tests}")
            print(f"  失敗: {failure_tests}")
            print(f"  成功率: {success_rate}")

            # 展開所有測試項目
            if expand_tests:
                print("\n📖 展開所有測試項目...")
                expand_btn = page.locator('button:has-text("展開全部")')
                if await expand_btn.count() > 0:
                    await expand_btn.click()
                    await asyncio.sleep(2)  # 等待展開動畫完成

                    # 截圖 - 展開狀態
                    screenshot_path = f"{screenshot_dir}/dashboard_expanded_{timestamp}.png"
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"📸 展開狀態截圖已保存: {screenshot_path}")

            # 測試過濾功能
            print("\n🔍 測試過濾功能...")

            # 過濾成功項目
            success_filter = page.locator('#filter-success')
            await success_filter.click()
            await asyncio.sleep(1)
            screenshot_path = f"{screenshot_dir}/dashboard_filter_success_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 成功過濾截圖已保存: {screenshot_path}")

            # 過濾失敗項目
            failure_filter = page.locator('#filter-failure')
            await failure_filter.click()
            await asyncio.sleep(1)
            screenshot_path = f"{screenshot_dir}/dashboard_filter_failure_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 失敗過濾截圖已保存: {screenshot_path}")

            # 回到全部
            all_filter = page.locator('#filter-all')
            await all_filter.click()
            await asyncio.sleep(1)

            # 檢查表格是否正確渲染
            print("\n🔍 檢查表格渲染...")
            tables = await page.locator('.output-table').count()
            print(f"  找到 {tables} 個表格")

            if tables > 0:
                # 獲取第一個表格的信息
                first_table = page.locator('.output-table').first
                headers = await first_table.locator('th').all_text_contents()
                print(f"  表格表頭: {headers}")

                # 獲取表格行數
                rows = await first_table.locator('tbody tr').count()
                print(f"  表格行數: {rows}")

            # 檢查格式化的區塊標題
            section_titles = await page.locator('.output-section-title').count()
            print(f"  找到 {section_titles} 個區塊標題")

            # 檢查鍵值對
            key_values = await page.locator('.output-key-value').count()
            print(f"  找到 {key_values} 個鍵值對項目")

            # 最終截圖
            screenshot_path = f"{screenshot_dir}/dashboard_final_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 最終截圖已保存: {screenshot_path}")

            print("\n✅ 測試完成！")

        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
            # 錯誤時也截圖
            error_screenshot = f"{screenshot_dir}/dashboard_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=error_screenshot, full_page=True)
            print(f"📸 錯誤截圖已保存: {error_screenshot}")
            raise

        finally:
            # 關閉瀏覽器
            if not headless:
                print("\n⏸️  按 Enter 關閉瀏覽器...")
                input()
            await browser.close()


async def open_dashboard(
    url: str = "http://localhost:8000/dashboard",
    browser_type: str = "chromium"
):
    """
    僅打開儀表板，不關閉（用於手動測試）

    Args:
        url: 儀表板 URL
        browser_type: 瀏覽器類型 (chromium, firefox, webkit)
    """
    async with async_playwright() as p:
        # 選擇瀏覽器
        if browser_type == "firefox":
            browser = await p.firefox.launch(headless=False)
        elif browser_type == "webkit":
            browser = await p.webkit.launch(headless=False)
        else:
            browser = await p.chromium.launch(headless=False)

        print(f"🚀 啟動 {browser_type} 瀏覽器...")

        # 創建新頁面
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # 訪問儀表板
        print(f"📱 訪問儀表板: {url}")
        await page.goto(url, wait_until='networkidle')

        # 自動展開所有測試
        await asyncio.sleep(2)
        expand_btn = page.locator('button:has-text("展開全部")')
        if await expand_btn.count() > 0:
            print("📖 自動展開所有測試項目...")
            await expand_btn.click()

        print("\n✅ 儀表板已打開！")
        print("⏸️  按 Enter 關閉瀏覽器...")
        input()

        await browser.close()


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(description="Playwright 儀表板自動化測試")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000/dashboard",
        help="儀表板 URL（預設：http://localhost:8000/dashboard）"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="使用無頭模式運行"
    )
    parser.add_argument(
        "--screenshot-dir",
        type=str,
        default="screenshots",
        help="截圖保存目錄（預設：screenshots）"
    )
    parser.add_argument(
        "--no-expand",
        action="store_true",
        help="不展開測試項目"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["test", "open"],
        default="test",
        help="運行模式：test=自動化測試，open=僅打開瀏覽器（預設：test）"
    )
    parser.add_argument(
        "--browser",
        type=str,
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="瀏覽器類型（僅 open 模式）"
    )

    return parser.parse_args()


async def main():
    args = parse_arguments()

    print("=" * 60)
    print("🎭 Playwright 儀表板自動化測試工具")
    print("=" * 60)

    if args.mode == "open":
        # 僅打開模式
        await open_dashboard(url=args.url, browser_type=args.browser)
    else:
        # 自動化測試模式
        await test_dashboard(
            url=args.url,
            headless=args.headless,
            screenshot_dir=args.screenshot_dir,
            expand_tests=not args.no_expand
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  已取消")
