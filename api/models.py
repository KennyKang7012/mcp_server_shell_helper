from pydantic import BaseModel
from typing import Optional

class ShellCommand(BaseModel):
    platform: Optional[str] = None
    shell_command: str

class ShellResponse(BaseModel):
    output: str
    error: Optional[str] = None
    return_code: int

class PlatformResponse(BaseModel):
    platform: str