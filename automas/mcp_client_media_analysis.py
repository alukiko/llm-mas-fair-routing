# automas/mcp_client_media_analysis.py
import os, json, asyncio
from pathlib import Path
from typing import Dict, Any, List

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

PROJECT_ROOT = Path(r"C:/Users/oklad/Desktop/LLM_Games").resolve()
GAIA_FILES_ROOT = PROJECT_ROOT / "workspace" / "gaia_files"
MCP_MODULE = "automas.mcp.servers.media.server"


def _build_env() -> Dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["GAIA_FILES_ROOT"] = str(GAIA_FILES_ROOT)
    return env


def _join_content_text(res) -> str:
    parts: List[str] = []
    for c in getattr(res, "content", []) or []:
        parts.append(getattr(c, "text", str(c)))
    return "\n".join(parts).strip()


async def _call_tool(tool_name: str, payload: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
    errlog = open(PROJECT_ROOT / "media_mcp.stderr.log", "ab")

    params = StdioServerParameters(
        command="python",
        args=["-m", MCP_MODULE],
        env=_build_env(),
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(params, errlog=errlog) as (r, w):
        async with ClientSession(r, w) as session:
            await asyncio.wait_for(session.initialize(), timeout=10)
            res = await asyncio.wait_for(session.call_tool(tool_name, payload), timeout=timeout)

    raw = _join_content_text(res)

    # MCP tool возвращает JSON строкой {"analysis": "...", "error": null}
    try:
        data = json.loads(raw)
    except Exception:
        data = {"analysis": raw, "error": None}

    if data.get("error"):
        raise RuntimeError(data["error"])
    return data


async def analyze_image(file_path: str, prompt: str, max_tokens: int = 1024, timeout: int = 120) -> str:
    data = await _call_tool(
        "analyze_image",
        {"file_path": file_path, "prompt": prompt, "max_tokens": max_tokens},
        timeout=timeout,
    )
    return data.get("analysis", "")


async def transcribe_audio(file_path: str, prompt: str = "", max_tokens: int = 2048, timeout: int = 180) -> str:
    data = await _call_tool(
        "transcribe_audio",
        {"file_path": file_path, "prompt": prompt, "max_tokens": max_tokens},
        timeout=timeout,
    )
    return data.get("analysis", "")


async def analyze_video(file_path: str, prompt: str, max_tokens: int = 2048, timeout: int = 240) -> str:
    data = await _call_tool(
        "analyze_video",
        {"file_path": file_path, "prompt": prompt, "max_tokens": max_tokens},
        timeout=timeout,
    )
    return data.get("analysis", "")
