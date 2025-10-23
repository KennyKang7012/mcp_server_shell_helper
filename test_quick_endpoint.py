import httpx
import json
import os
import sys
import argparse
import logging
from datetime import datetime
import asyncio
from typing import Optional

# 配置logging
def setup_logging():
    """設定日誌記錄器"""
    log_filename = f"monitoring_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] [%(process)d] %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 設定httpx的日誌級別為WARNING，避免過多的請求日誌
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def create_markdown_content(results):
    """將測試結果轉換為 Markdown 格式"""
    markdown = []
    
    # 添加標題
    markdown.append("# Shell Helper API 測試報告")
    markdown.append(f"\n## 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 添加測試結果摘要
    markdown.append("\n## 測試摘要")
    success_count = sum(1 for r in results if "error" not in r)
    total_count = len(results)
    markdown.append(f"- 總測試數: {total_count}")
    markdown.append(f"- 成功數: {success_count}")
    markdown.append(f"- 失敗數: {total_count - success_count}")
    
    # 詳細測試結果
    markdown.append("\n## 詳細測試結果")
    
    for i, result in enumerate(results, 1):
        markdown.append(f"\n### 測試 {i}")
        markdown.append(f"- **執行時間**: {result['timestamp']}")
        markdown.append(f"- **執行命令**: `{result['command']['shell_command']}`")
        markdown.append(f"- **指定平台**: {result['command']['platform'] or '自動偵測'}")
        
        if "error" in result:
            markdown.append(f"- **狀態**: ❌ 失敗")
            markdown.append(f"- **錯誤訊息**: {result['error']}")
        else:
            response = result["response"]
            is_success = response["result"]["return_code"] == 0
            status_icon = "✅" if is_success else "⚠️"
            
            markdown.append(f"- **狀態**: {status_icon} {'成功' if is_success else '失敗'}")
            markdown.append(f"- **實際平台**: {response['platform']}")
            markdown.append(f"- **返回碼**: {response['result']['return_code']}")
            
            # 格式化輸出結果
            if response["result"]["output"]:
                markdown.append("- **輸出結果**:")
                markdown.append("```")
                markdown.append(response["result"]["output"].strip())
                markdown.append("```")
            
            # 如果有錯誤訊息
            if response["result"]["error"]:
                markdown.append("- **錯誤訊息**:")
                markdown.append("```")
                markdown.append(response["result"]["error"])
                markdown.append("```")
    
    return "\n".join(markdown)

async def test_quick_endpoint(timeout_seconds: int = 30):
    """測試 /quick 端點並將結果寫入檔案
    
    Args:
        timeout_seconds: 請求超時時間（秒），預設30秒
    """
    logger = logging.getLogger(__name__)
    global base_url  # 使用全域變數，確保使用使用者指定的設定
    logger.info(f"測試 /quick 端點，服務器位址: {base_url}")
    
    # 準備測試命令
    test_commands = [
        {"platform": None, "shell_command": "echo 'Hello from auto-detected platform'"},
        {"platform": "Windows", "shell_command": "Get-Date"},
        {
            "platform": "Windows",
            "shell_command": "$os = Get-CimInstance Win32_OperatingSystem; $totalGB = [math]::Round($os.TotalVisibleMemorySize/1MB, 2); $freeGB = [math]::Round($os.FreePhysicalMemory/1MB, 2); $usedGB = [math]::Round($totalGB - $freeGB, 2); $usagePercent = [math]::Round(($usedGB / $totalGB) * 100, 1); Write-Output '===== 系統記憶體使用情況 ====='; Write-Output \"總記憶體: $totalGB GB\"; Write-Output \"已使用: $usedGB GB ($usagePercent%)\"; Write-Output \"可用記憶體: $freeGB GB\"; Write-Output ''; Write-Output '===== 前30個最耗記憶體的程序 ====='; Get-Process | Sort-Object WS -Descending | Select-Object -First 30 | Select-Object @{N='ProcessName';E={$_.Name}}, @{N='PID';E={$_.ID}}, @{N='Memory(GB)';E={[math]::Round($_.WS/1GB,2)}}, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{'N/A'}}} | Format-Table -AutoSize | Out-String"
        }
    ]
    
    # 建立 HTTP 客戶端，設定超時時間
    timeout = httpx.Timeout(timeout_seconds, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        results = []
        
        # 執行每個測試命令
        for cmd in test_commands:
            try:
                print(f"正在執行命令: {cmd['shell_command'][:50]}...")  # 只顯示命令的前50個字元
                response = await client.post(f"{base_url}/quick", json=cmd)
                response.raise_for_status()
                
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "command": cmd,
                    "response": response.json(),
                    "status_code": response.status_code
                }
            except httpx.TimeoutException as e:
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "command": cmd,
                    "error": f"請求超時 (超過 {timeout_seconds} 秒無回應)"
                }
                print(f"警告: 命令執行超時")
            except Exception as e:
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "command": cmd,
                    "error": str(e)
                }
                print(f"錯誤: {str(e)}")
            
            results.append(result)
            
        # 生成 Markdown 內容
        markdown_content = create_markdown_content(results)
        
        # 將結果追加寫入 Markdown 檔案
        output_md = "quick_endpoint_test_results.md"
        separator = "\n\n" + "="*80 + "\n\n"  # 新增分隔線
        
        # 如果檔案不存在，直接寫入
        if not os.path.exists(output_md):
            with open(output_md, "w", encoding="utf-8") as f:
                f.write(markdown_content)
        else:
            # 如果檔案存在，追加內容
            with open(output_md, "a", encoding="utf-8") as f:
                f.write(separator + markdown_content)
            
        # 同時保存最新的 JSON 資料（使用時間戳記）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_json = f"quick_endpoint_test_results_{timestamp}.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print(f"測試報告已追加到 {output_md}")
        print(f"本次測試的原始資料已保存到 {output_json}")

async def monitor_with_interval(interval_seconds: int, duration_minutes: Optional[int] = None, timeout_seconds: int = 30):
    """定期執行監控
    
    Args:
        interval_seconds: 監控間隔（秒）
        duration_minutes: 監控持續時間（分鐘），如果為 None 則持續執行
        timeout_seconds: 單次請求超時時間（秒）
    """
    logger = logging.getLogger(__name__)
    start_time = datetime.now()
    iteration = 1
    
    try:
        while True:
            logger.info(f"\n=== 開始第 {iteration} 次監控 ===")
            logger.info(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                # 檢查服務器狀態
                timeout = httpx.Timeout(timeout_seconds)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    try:
                        response = await client.get(f"{base_url}/platform")
                        if response.status_code == 200:
                            await test_quick_endpoint(timeout_seconds)
                        else:
                            logger.error("無法連接到服務器")
                    except httpx.TimeoutException:
                        logger.warning(f"警告: 連接超時（超過 {timeout_seconds} 秒無回應）")
                        logger.info("等待下一次嘗試...")
            except Exception as e:
                logger.error(f"錯誤: {str(e)}")
                logger.error("請確認服務器是否已啟動（執行 python run.py）")
            
            # 檢查是否達到監控持續時間
            if duration_minutes is not None:
                elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
                if elapsed_minutes >= duration_minutes:
                    print(f"\n已達到指定監控時間 {duration_minutes} 分鐘，停止監控")
                    break
            
            iteration += 1
            await asyncio.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n接收到終止信號，停止監控")
        
def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(description="系統資源監控工具")
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=300,
        help="監控間隔時間（秒），預設為 300 秒（5分鐘）"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        help="單次請求超時時間（秒），預設為 30 秒"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        help="監控持續時間（分鐘），不指定則持續執行直到手動停止"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="要監控的主機位址，預設為 localhost"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API 服務的埠號，預設為 8000"
    )
    return parser.parse_args()

async def main():
    # 設定日誌記錄器
    logger = setup_logging()
    
    args = parse_arguments()
    
    # 更新全域 base_url
    global base_url
    base_url = f"http://{args.host}:{args.port}"
    
    logger.info("\n** 系統資源監控工具啟動 **")
    logger.info(f"開始監控 {args.host}:{args.port}")
    logger.info(f"監控間隔: {args.interval} 秒")
    logger.info(f"請求超時: {args.timeout} 秒")
    if args.duration:
        logger.info(f"監控時間: {args.duration} 分鐘")
    else:
        logger.info("監控持續執行直到手動停止 (按 Ctrl+C 終止)")
    
    await monitor_with_interval(args.interval, args.duration, args.timeout)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n程式已終止")