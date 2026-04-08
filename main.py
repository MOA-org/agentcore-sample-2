"""
Minimal Bedrock AgentCore–style HTTP surface for pipeline deploy testing.

AgentCore custom containers typically expose:
  - GET  /ping         — health (used before routing traffic)
  - POST /invocations — handle a turn (payload shape varies; this sample echoes)
"""

from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="agentcore-sample", version="1.0.0")


@app.get("/ping")
async def ping() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/health")
async def health_alias() -> Dict[str, str]:
    """Optional alias; some samples use /health instead of /ping."""
    return {"status": "healthy"}


@app.post("/invocations")
async def invocations(request: Request) -> JSONResponse:
    raw = await request.body()
    data: Any
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {"_raw": raw.decode("utf-8", errors="replace")}

    prompt = ""
    if isinstance(data, dict):
        inp = data.get("input")
        if isinstance(inp, dict):
            prompt = str(inp.get("prompt", "") or "")
        elif isinstance(inp, str):
            prompt = inp

    # Stub response for deploy testing — replace with real agent logic + Bedrock calls.
    out = {
        "output": (
            "agentcore-sample: OK. "
            f"keys={list(data.keys()) if isinstance(data, dict) else 'n/a'} "
            f"prompt_preview={prompt[:500]!r}"
        )
    }
    return JSONResponse(content=out)
