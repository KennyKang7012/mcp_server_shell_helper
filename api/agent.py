import platform
import subprocess
from fastapi import HTTPException

class ShellAgent:
    def get_platform(self) -> str:
        """取得作業系統平台類型"""
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system in ["Linux", "Darwin"]:
            return "*nix"
        return "Unknown"

    async def execute_command(self, platform: str, shell_command: str) -> dict:
        """執行 shell 命令"""
        if platform not in ["Windows", "*nix"]:
            raise HTTPException(status_code=400, detail="不支援的作業系統平台")

        args = ['powershell', '-Command', shell_command] if platform == "Windows" else shell_command

        try:
            process = subprocess.Popen(
                args,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            result = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    result.append(output)

            error = process.stderr.read()
            return_code = process.wait()

            return {
                "output": "".join(result),
                "error": error if error else None,
                "return_code": return_code
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))