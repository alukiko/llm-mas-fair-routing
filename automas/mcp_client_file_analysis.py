import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


PROJECT_ROOT = Path(r"C:/Users/oklad/Desktop/LLM_Games").resolve()
GAIA_FILES_ROOT = PROJECT_ROOT / "workspace" / "gaia_files"
MCP_MODULE = "automas.mcp.servers.document.server"  # это твой file-analysis server.py


def _build_env() -> Dict[str, str]:
    env = dict(os.environ)
    # чтобы python -m automas.mcp... точно импортился
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["GAIA_FILES_ROOT"] = str(GAIA_FILES_ROOT)
    return env


def _assert_allowed(file_path: str) -> str:
    p = Path(file_path).resolve()
    root = GAIA_FILES_ROOT.resolve()
    if root not in p.parents and p != root:
        raise ValueError(f"Path not allowed: {p}. Root: {root}")
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return str(p)


def _pack_texts(result) -> List[str]:
    # MCP result обычно содержит content items
    texts = []
    for c in getattr(result, "content", []) or []:
        if hasattr(c, "text"):
            texts.append(c.text)
        else:
            texts.append(str(c))
    if not texts:
        texts = [str(result)]
    return texts


async def call_file_analysis_tool(tool_name: str, payload: Dict[str, Any], timeout: int = 120) -> List[str]:
    """
    ВАЖНО: делаем 'одноразовый' lifecycle (stdio_client -> session -> close).
    Это самый стабильный режим на Windows.
    """
    server_params = StdioServerParameters(
        command="python",
        args=["-m", MCP_MODULE],
        env=_build_env(),
        cwd=str(PROJECT_ROOT),
    )

    # stderr лучше уводить в файл, чтобы не было блокировок
    errlog_path = PROJECT_ROOT / "file_analysis_mcp.stderr.log"
    errlog = open(errlog_path, "wb")

    async with stdio_client(server_params, errlog=errlog) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=10)
            res = await asyncio.wait_for(session.call_tool(tool_name, payload), timeout=timeout)
            return _pack_texts(res)


async def extract_text(file_path: str, timeout: int = 180) -> str:
    fp = _assert_allowed(file_path)
    texts = await call_file_analysis_tool("extract_text", {"file_path": fp}, timeout=timeout)
    return texts[0] if texts else ""
