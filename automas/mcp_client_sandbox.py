# automas/mcp_client_sandbox.py
import os
import json
import asyncio
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Coroutine

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

PROJECT_ROOT = Path(r"C:/Users/oklad/Desktop/LLM_Games").resolve()
MCP_MODULE = "automas.mcp.servers.sandbox.server"  # твой E2B sandbox MCP server


def _build_env() -> Dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    if os.getenv("E2B_API_KEY"):
        env["E2B_API_KEY"] = os.getenv("E2B_API_KEY")

    return env



def _pack_texts(result) -> str:
    # Обычно fastmcp возвращает content[text=...]
    texts = []
    for c in getattr(result, "content", []) or []:
        if hasattr(c, "text"):
            texts.append(c.text)
        else:
            texts.append(str(c))
    return "\n".join(texts) if texts else str(result)


def run_coro(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Jupyter-safe запуск корутины:
    - если нет running loop → asyncio.run
    - если есть (Jupyter) → отдельный поток с новым loop
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    box: Dict[str, Any] = {"result": None, "error": None}

    def _runner():
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            box["result"] = loop.run_until_complete(coro)
        except Exception as e:
            box["error"] = e
        finally:
            try:
                loop.close()
            except Exception:
                pass

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    t.join()

    if box["error"] is not None:
        raise box["error"]
    return box["result"]


async def _call_tool(tool_name: str, payload: Dict[str, Any], timeout: int = 120) -> Any:
    server_params = StdioServerParameters(
        command="python",
        args=["-m", MCP_MODULE],
        env=_build_env(),
        cwd=str(PROJECT_ROOT),
    )

    errlog = open(PROJECT_ROOT / "sandbox_mcp.stderr.log", "ab")

    async with stdio_client(server_params, errlog=errlog) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=10)
            res = await asyncio.wait_for(session.call_tool(tool_name, payload), timeout=timeout)
            text = _pack_texts(res)

            # try parse json if it's json-like
            t = text.strip()
            if (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]")):
                try:
                    return json.loads(t)
                except Exception:
                    return text
            return text


async def e2b_create_sandbox(timeout: int = 120) -> Dict[str, Any]:
    """
    tool: e2b_create_sandbox_and_return_id
    Возвращает dict: {"result": {"sandbox_id": "...", "success": true}} или error
    """
    out = await _call_tool("e2b_create_sandbox_and_return_id", {}, timeout=timeout)
    return out if isinstance(out, dict) else {"result": {"error": out}}


async def e2b_run_code(code_block: str, sandbox_id: Optional[str] = None, timeout: int = 120) -> Any:
    """
    tool: e2b_run_code
    payload: {"code_block": "...", "sandbox_id": optional}
    """
    payload: Dict[str, Any] = {"code_block": code_block}
    if sandbox_id:
        payload["sandbox_id"] = sandbox_id
    return await _call_tool("e2b_run_code", payload, timeout=timeout)


def e2b_run_code_sync(code_block: str, sandbox_id: Optional[str] = None, timeout: int = 120) -> Any:
    return run_coro(e2b_run_code(code_block, sandbox_id=sandbox_id, timeout=timeout))


def e2b_create_sandbox_sync(timeout: int = 120) -> Dict[str, Any]:
    return run_coro(e2b_create_sandbox(timeout=timeout))


def sandbox_exec_sync(code: str, timeout: int = 120, sandbox_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Унифицированная функция для calculation_agent_node (E2B).
    Возвращает {ok, stdout, stderr, sandbox_id, raw}
    """
    try:
        raw = e2b_run_code_sync(code, sandbox_id=sandbox_id, timeout=timeout)

        # Если сервер вернул dict в формате E2B:
        # {"results": [], "logs": {"stdout": ["..."], "stderr": [...]}, "error": None, ...}
        if isinstance(raw, dict):
            err = raw.get("error")
            logs = raw.get("logs") or {}
            out_list = logs.get("stdout") or []
            err_list = logs.get("stderr") or []

            stdout = "".join(out_list) if isinstance(out_list, list) else str(out_list)
            stderr = "".join(err_list) if isinstance(err_list, list) else str(err_list)

            if err:
                return {"ok": False, "sandbox_id": sandbox_id, "stdout": stdout or None, "stderr": str(err), "raw": raw}

            # если stderr не пустой — не считаем ошибкой, но возвращаем
            return {"ok": True, "sandbox_id": sandbox_id, "stdout": stdout, "stderr": (stderr or None), "raw": raw}

        # Если вернулась строка — считаем stdout строкой
        return {"ok": True, "sandbox_id": sandbox_id, "stdout": str(raw), "stderr": None, "raw": raw}

    except Exception as e:
        return {"ok": False, "sandbox_id": sandbox_id, "stdout": None, "stderr": repr(e), "raw": None}
