"""
Vertex Monitor — 预算代理服务（v3）
OpenAI 兼容端点 + liteLLM 计费 + 双模式预算 + Web UI

启动: python proxy.py    |   端口: 8899
Web UI: http://localhost:8899
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import litellm
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from store import load_store, save_store, record_call

# ── 配置加载 ──────────────────────────────────────────────
_data_dir = Path(__file__).parent / "data"
_data_dir.mkdir(parents=True, exist_ok=True)

SETTINGS_PATH = _data_dir / "settings.json"
_LEGACY_CONFIG_PATH = Path(__file__).parent / "config.json"

_DEFAULT_SETTINGS = {
    "vertex_project": "ai-project-384207",
    "vertex_location": "global",
    "vertex_model": "gemini-3.1-flash-lite",
    "models": [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.1-pro-preview",
    ],
}


def _load_config() -> dict:
    # 迁移：首次启动时将旧 config.json 合并到 data/settings.json
    if not SETTINGS_PATH.exists() and _LEGACY_CONFIG_PATH.exists():
        try:
            legacy = json.loads(_LEGACY_CONFIG_PATH.read_text(encoding="utf-8"))
            merged = {**_DEFAULT_SETTINGS, **legacy}
            SETTINGS_PATH.write_text(
                json.dumps(merged, indent=4, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except Exception:
            pass
    if SETTINGS_PATH.exists():
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    return dict(_DEFAULT_SETTINGS)


def _save_config(cfg: dict):
    SETTINGS_PATH.write_text(
        json.dumps(cfg, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


_config = _load_config()

VERTEX_PROJECT = _config.get("vertex_project", _DEFAULT_SETTINGS["vertex_project"])
VERTEX_LOCATION = _config.get("vertex_location", _DEFAULT_SETTINGS["vertex_location"])
DEFAULT_MODEL = _config.get("vertex_model", _DEFAULT_SETTINGS["vertex_model"])

ALLOWED_MODELS: set[str] = set(_config.get("models", _DEFAULT_SETTINGS["models"]))

# 服务账号凭证
_credentials_filename = _config.get("google_application_credentials", "vertex-key.json")

# 优先从数据卷读取（可写），回退到应用目录（Docker 构建时复制）
_creds_in_data = _data_dir / _credentials_filename
_creds_in_app = Path(__file__).parent / _credentials_filename

if _creds_in_data.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_creds_in_data.resolve())
elif _creds_in_app.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_creds_in_app.resolve())

# ── FastAPI 应用 ───────────────────────────────────────────
app = FastAPI(title="Vertex Monitor", version="3.0.0")

# 静态文件托管
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 显式路由（优先于 StaticFiles）


@app.get("/")
async def index():
    """Web UI 入口 — 仪表盘"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Vertex Monitor</h1><p>Web UI 未部署。API 端点可用。</p>")


@app.get("/settings")
async def settings_page():
    """设置页面"""
    settings_path = static_dir / "settings.html"
    if settings_path.exists():
        return HTMLResponse(settings_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>设置页面未部署</h1><p>请将 settings.html 放入 static/ 目录。</p>")


# ── 核心 API ─────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "models": sorted(ALLOWED_MODELS)}


@app.post("/api/test")
async def test_connectivity(request: Request):
    """连通性测试：用第一个可用模型发一条最小请求。"""
    # 优先使用请求中的 model 参数，否则取最可靠的测试模型
    model_to_test = DEFAULT_MODEL
    # 尝试取最轻量的模型做连通性测试（优先 gemini-3.1-flash-lite）
    preferred = "gemini-3.1-flash-lite"
    if preferred in ALLOWED_MODELS:
        model_to_test = preferred
    elif ALLOWED_MODELS:
        model_to_test = next(iter(ALLOWED_MODELS))
    try:
        body = await request.json()
        if body.get("model") and body["model"] in ALLOWED_MODELS:
            model_to_test = body["model"]
    except Exception:
        pass  # 请求体为空时使用默认

    try:
        response = litellm.completion(
            model=f"vertex_ai/{model_to_test}",
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=10,
            vertex_project=VERTEX_PROJECT,
            vertex_location=VERTEX_LOCATION,
        )
        content = response.choices[0].message.content if response.choices else ""
        return JSONResponse({
            "ok": True,
            "model": model_to_test,
            "response": (content or "").strip(),
        })
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"ok": False, "model": DEFAULT_MODEL, "error": str(e)},
        )


@app.get("/usage")
async def usage():
    """查询当前预算状态（兼容旧接口）。"""
    store = load_store()
    return JSONResponse(store.summary())


# ── 配置管理 API ─────────────────────────────────────────

@app.get("/api/config")
async def get_config():
    """获取计费配置 + 当前状态。"""
    store = load_store()
    store.check_and_reset()
    return JSONResponse(store.summary())


@app.post("/api/config")
async def update_config(request: Request):
    """更新计费配置。Body 中传要修改的字段即可。"""
    body = await request.json()
    store = load_store()
    store.update_billing(body)
    save_store(store)
    return JSONResponse({"ok": True, **store.summary()})


@app.post("/api/reset")
async def reset_now():
    """手动立即重置本期消费。"""
    store = load_store()
    store.reset_now()
    save_store(store)
    return JSONResponse({"ok": True, **store.summary()})


# ── 统计 API ─────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats():
    """获取模型消费统计。"""
    store = load_store()
    return JSONResponse({
        "models": store.summary()["models"],
        "lifetime": store.summary()["lifetime"],
        "period": store.summary()["period"],
    })


@app.get("/api/history")
async def get_history(limit: int = 50):
    """获取最近 N 条调用历史。"""
    history_path = Path(__file__).parent / "data" / "store_history.jsonl"
    if not history_path.exists():
        return JSONResponse([])

    lines = []
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip())
    # 返回最近 limit 条
    recent = lines[-limit:]
    return JSONResponse([json.loads(l) for l in recent])


# ── 设置管理 API ─────────────────────────────────────────


@app.get("/api/settings")
async def get_settings():
    """获取完整设置：模型列表、Key 状态、Vertex 配置。"""
    cfg = _load_config()
    creds_path = _data_dir / cfg.get("google_application_credentials", "vertex-key.json")
    has_key = creds_path.exists() and creds_path.stat().st_size > 0

    # 读取 key 文件内容
    key_content = ""
    key_preview = ""
    if has_key:
        try:
            raw = creds_path.read_text(encoding="utf-8").strip()
            key_data = json.loads(raw)
            key_preview = f"{key_data.get('project_id', '?')} / {key_data.get('client_email', '?')}"
            key_content = raw
        except Exception:
            key_preview = "已配置（无法解析）"

    return JSONResponse({
        "vertex_project": cfg.get("vertex_project", _DEFAULT_SETTINGS["vertex_project"]),
        "vertex_location": cfg.get("vertex_location", _DEFAULT_SETTINGS["vertex_location"]),
        "vertex_model": cfg.get("vertex_model", _DEFAULT_SETTINGS["vertex_model"]),
        "models": cfg.get("models", _DEFAULT_SETTINGS["models"]),
        "has_key": has_key,
        "key_preview": key_preview,
        "key_content": key_content,
        "credentials_path": cfg.get("google_application_credentials", "vertex-key.json"),
    })


@app.post("/api/settings")
async def update_settings(request: Request):
    """更新设置：Vertex 配置 + 模型列表 + Vertex Key JSON。"""
    body = await request.json()
    cfg = _load_config()

    modified = False

    # 更新 Vertex 项目配置
    for key in ("vertex_project", "vertex_location", "vertex_model"):
        if key in body and body[key]:
            cfg[key] = body[key]
            modified = True

    # 更新模型列表
    if "models" in body and isinstance(body["models"], list):
        cfg["models"] = body["models"]
        modified = True

    # 更新 Vertex Key
    if "vertex_key_json" in body and body["vertex_key_json"]:
        key_str = body["vertex_key_json"].strip()
        # 验证 JSON 有效性
        try:
            key_data = json.loads(key_str)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_key_json", "message": "Vertex Key 内容不是有效的 JSON"},
            )
        # 验证必要字段
        if "private_key" not in key_data and "client_email" not in key_data:
            raise HTTPException(
                status_code=400,
                detail={"error": "missing_key_fields", "message": "JSON 缺少必要字段（private_key / client_email）"},
            )

        creds_path = _data_dir / cfg.get("google_application_credentials", "vertex-key.json")
        creds_path.write_text(key_str, encoding="utf-8")

        # 更新环境变量
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path.resolve())

        cfg["google_application_credentials"] = str(creds_path.name)
        modified = True

    if modified:
        _save_config(cfg)
        # 重新加载全局变量
        global _config, ALLOWED_MODELS, VERTEX_PROJECT, VERTEX_LOCATION, DEFAULT_MODEL
        _config = cfg
        ALLOWED_MODELS = set(cfg.get("models", _DEFAULT_SETTINGS["models"]))
        VERTEX_PROJECT = cfg.get("vertex_project", _DEFAULT_SETTINGS["vertex_project"])
        VERTEX_LOCATION = cfg.get("vertex_location", _DEFAULT_SETTINGS["vertex_location"])
        DEFAULT_MODEL = cfg.get("vertex_model", _DEFAULT_SETTINGS["vertex_model"])

    return JSONResponse({"ok": True, "has_key": body.get("vertex_key_json", "") != ""})


# ── Skill API（供 AI Agent 调用）─────────────────────────────────

@app.get("/skill/balance")
async def skill_balance():
    """Skill: 查询当前余额与预算状态，供 AI Agent 作为工具调用。"""
    store = load_store()
    store.check_and_reset()
    cur = store.summary()["current"]
    status = "exhausted" if cur["exhausted"] or cur["expired"] else "warning" if cur["remaining"] < cur["balance"] * 0.2 else "healthy"
    status_emoji = {"healthy": "🟢", "warning": "🟡", "exhausted": "🔴"}.get(status, "🟢")
    message = (
        f"{status_emoji} Budget status: {status}. "
        f"Remaining ${cur['remaining']:.4f} of ${cur['balance']:.2f} "
        f"(spent ${cur['spent']:.6f})."
    )
    if cur["expired"]:
        message = f"🔴 Budget expired at {cur['expires_at']}."
    elif cur["exhausted"]:
        message = f"🔴 Budget exhausted. Spent ${cur['spent']:.6f} of ${cur['balance']:.2f}."
    return JSONResponse({
        "status": status,
        "balance": cur["balance"],
        "spent": cur["spent"],
        "remaining": cur["remaining"],
        "expires_at": cur["expires_at"],
        "mode": store.billing.mode,
        "message": message,
    })


@app.get("/skill/models")
async def skill_models():
    """Skill: 查询当前允许的模型列表，供 AI Agent 作为工具调用。"""
    return JSONResponse({
        "models": sorted(ALLOWED_MODELS),
        "default_model": DEFAULT_MODEL,
        "count": len(ALLOWED_MODELS),
    })

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI 兼容的聊天补全端点。"""
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", DEFAULT_MODEL)

    if not messages:
        raise HTTPException(status_code=400, detail="messages is required")

    if model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "model_not_allowed",
                "model": model,
                "allowed": sorted(ALLOWED_MODELS),
            },
        )

    # 预算检查
    store = load_store()
    store.check_and_reset()
    if store.exhausted:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "budget_exhausted",
                "message": "余额已耗尽" if not store.expired else "余额已过期",
                "spent": round(store.spent, 6),
                "remaining": round(store.remaining, 6),
                "balance": round(store._current_balance, 6),
                "mode": store.billing.mode,
            },
        )

    # 构建 liteLLM 调用参数 — 转发 Hermes 发来的所有关键字段
    vertex_model = f"vertex_ai/{model}"
    llm_kwargs: dict = {
        "model": vertex_model,
        "messages": messages,
        "vertex_project": VERTEX_PROJECT,
        "vertex_location": VERTEX_LOCATION,
    }

    # 转发可选参数
    for key in ("temperature", "max_tokens", "max_completion_tokens",
                 "top_p", "stop", "tools", "tool_choice",
                 "response_format"):
        if key in body:
            llm_kwargs[key] = body[key]

    # ⚠️ 关键：始终关闭流式。Vertex Monitor 不实现 SSE，
    # 但 Hermes 会发 stream:true → 必须显式关闭，否则 Hermes 的
    # SSE 解析器吃到完整 JSON 会解析失败，导致 "Empty response"
    llm_kwargs["stream"] = False

    try:
        response = litellm.completion(**llm_kwargs)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "vertex_error", "message": str(e)},
        )

    # 计费
    try:
        cost = litellm.completion_cost(completion_response=response)
    except Exception:
        cost = 0.0

    # 序列化响应 — 使用 liteLLM 原生 OpenAI 格式，仅追加 _budget
    resp_dict = response.model_dump() if hasattr(response, "model_dump") else dict(response)

    # 提取 token 用量记录
    usage_info = resp_dict.get("usage", {})
    prompt_tokens = usage_info.get("prompt_tokens", 0)
    completion_tokens = usage_info.get("completion_tokens", 0)

    store = record_call(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_usd=cost,
        model=model,
    )

    # 在原生响应上追加预算元数据（不影响 Hermes 解析）
    resp_dict["_budget"] = {
        "cost_usd": round(cost, 8),
        "remaining": round(store.remaining, 8),
        "mode": store.billing.mode,
    }

    # ═══ 处理客户端流式请求 ═══
    # 如果客户端发了 stream:true，代理必须返回 SSE 格式，否则 Hermes
    # 的流式解析器吃到纯 JSON 会解析失败 → "Empty response"。
    client_wants_stream = body.get("stream", False)

    if client_wants_stream:
        import time as _time
        import uuid as _uuid

        chunk_id = f"chatcmpl-{_uuid.uuid4().hex[:12]}"
        created = int(_time.time())
        content = resp_dict["choices"][0]["message"]["content"] if resp_dict.get("choices") else ""
        finish = resp_dict["choices"][0].get("finish_reason", "stop") if resp_dict.get("choices") else "stop"

        # 内容块（delta）
        chunk_content = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": content},
                "finish_reason": None,
            }],
        }

        # 结束块（含 usage + budget）
        usage_info = resp_dict.get("usage", {})
        chunk_done = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": finish,
            }],
            "usage": usage_info,
            "_budget": resp_dict["_budget"],
        }

        def sse_generator():
            yield f"data: {json.dumps(chunk_content)}\n\n"
            yield f"data: {json.dumps(chunk_done)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # 非流式：返回完整 JSON（原有行为）
    return JSONResponse(content=resp_dict)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"detail": str(exc.detail)},
    )


# ── 入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8899))
    store = load_store()
    store.check_and_reset()
    save_store(store)
    print(f"🔒 Vertex Monitor v3 启动 → http://localhost:{port}")
    print(f"   Web UI: http://localhost:{port}")
    print(f"   模式: {'手动' if store.billing.is_manual else '自动循环'}")
    print(f"   余额: ${store.remaining:.2f} / ${store._current_balance:.2f}")
    print(f"   模型: {', '.join(sorted(ALLOWED_MODELS))}")
    uvicorn.run(app, host=host, port=port, log_level="info")
