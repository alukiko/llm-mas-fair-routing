# mcp_client_web.py
import os
import json
import asyncio
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Coroutine

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

# === Настрой под себя ===
PROJECT_ROOT = Path(r"C:/Users/oklad/Desktop/LLM_Games").resolve()
# модуль, который запускает web/server.py
MCP_MODULE = "automas.mcp.servers.web.server"


def _build_env() -> Dict[str, str]:
    """
    Важно для Windows/Jupyter: гарантируем, что python -m automas... импортится.
    Плюс сюда можно добавить SEARXNG_URL и прочие переменные.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _pack_texts(result) -> List[str]:
    """
    MCP result обычно содержит content items.
    Для простых tool-ответов вернём список строк.
    """
    texts: List[str] = []
    for c in getattr(result, "content", []) or []:
        if hasattr(c, "text"):
            texts.append(c.text)
        else:
            texts.append(str(c))
    return texts or [str(result)]


def run_coro(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Безопасно запускает async-корутину:
    - если loop НЕ запущен -> asyncio.run
    - если loop УЖЕ запущен (Jupyter/IPython) -> отдельный поток + новый event loop

    Это убирает ошибку:
      asyncio.run() cannot be called from a running event loop
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # В обычном скрипте (нет running loop)
        return asyncio.run(coro)

    # В Jupyter loop уже запущен -> выполняем в отдельном потоке
    result_container: Dict[str, Any] = {"result": None, "error": None}

    def _runner() -> None:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result_container["result"] = loop.run_until_complete(coro)
        except Exception as e:
            result_container["error"] = e
        finally:
            try:
                loop.close()
            except Exception:
                pass

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    t.join()

    if result_container["error"] is not None:
        raise result_container["error"]
    return result_container["result"]


async def call_web_tool(
    tool_name: str,
    payload: Dict[str, Any],
    timeout: int = 90,
) -> Any:
    """
    Одноразовый lifecycle (stdio_client -> session -> close) — самый стабильный режим на Windows.
    Возвращает "сырое" MCP-значение (часто это JSON-строка или строка).
    """
    server_params = StdioServerParameters(
        command="python",
        args=["-m", MCP_MODULE],
        env=_build_env(),
        cwd=str(PROJECT_ROOT),
    )

    errlog_path = PROJECT_ROOT / "web_mcp.stderr.log"
    errlog = open(errlog_path, "ab")  # append, чтобы видеть историю

    async with stdio_client(server_params, errlog=errlog) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=10)
            res = await asyncio.wait_for(
                session.call_tool(tool_name, payload),
                timeout=timeout
            )

            texts = _pack_texts(res)

            # Часто сервер возвращает JSON строкой → попробуем распарсить
            if len(texts) == 1:
                t = texts[0].strip()
                if (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]")):
                    try:
                        return json.loads(t)
                    except Exception:
                        return t
                return t

            return texts


# =========================
# Удобные async функции-обёртки
# =========================

async def web_search(
    query: str,
    max_results: int = 5,
    engines: Optional[str] = None,
    categories: str = "general",
    language: str = "auto",
    safesearch: int = 1,
    timeout: int = 60,
) -> Union[Dict[str, Any], str]:
    """
    Tool: search (SearXNG). Возвращает SearchResponse (dict) или str с ошибкой.
    Требует запущенный SearXNG и env: SEARXNG_URL (иначе будет connection error).
    """
    return await call_web_tool(
        "search",
        {
            "query": query,
            "max_results": max_results,
            "engines": engines,
            "categories": categories,
            "language": language,
            "safesearch": safesearch,
        },
        timeout=timeout,
    )


async def web_extract(
    url: str,
    max_lines: Optional[int] = None,
    timeout: int = 120,
) -> str:
    """
    Tool: extract. Возвращает Markdown (строка).
    """
    payload: Dict[str, Any] = {"url": url}
    if max_lines is not None:
        payload["max_lines"] = max_lines
    out = await call_web_tool("extract", payload, timeout=timeout)
    return out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)


async def web_map(
    url: str,
    max_requests: int = 20,
    timeout: int = 180,
) -> Any:
    """
    Tool: map. Возвращает DatasetItemsListPage (обычно сериализуемый объект/словарь).
    """
    return await call_web_tool(
        "map",
        {"url": url, "max_requests": max_requests},
        timeout=timeout,
    )


async def web_screenshot_and_save(
    url: str,
    filename: str,
    timeout: int = 120,
) -> str:
    """
    Tool: screenshot_and_save.
    """
    out = await call_web_tool(
        "screenshot_and_save",
        {"url": url, "filename": filename},
        timeout=timeout,
    )
    return out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)


async def web_screenshot_and_analyze(
    url: str,
    filename: str,
    prompt: str,
    timeout: int = 180,
) -> str:
    """
    Tool: screenshot_and_analyze (использует OPENROUTER_API_KEY внутри сервера).
    """
    out = await call_web_tool(
        "screenshot_and_analyze",
        {"url": url, "filename": filename, "prompt": prompt},
        timeout=timeout,
    )
    return out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)


# =========================
# Sync-обёртки (для LangGraph nodes / обычного кода)
# =========================

def web_search_sync(*args, **kwargs):
    return run_coro(web_search(*args, **kwargs))

def web_extract_sync(*args, **kwargs):
    return run_coro(web_extract(*args, **kwargs))

def web_map_sync(*args, **kwargs):
    return run_coro(web_map(*args, **kwargs))

def web_screenshot_and_save_sync(*args, **kwargs):
    return run_coro(web_screenshot_and_save(*args, **kwargs))

def web_screenshot_and_analyze_sync(*args, **kwargs):
    return run_coro(web_screenshot_and_analyze(*args, **kwargs))
