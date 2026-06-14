"""FastAPI приложение Paideia.

Запуск:
    uvicorn api.main:app --reload

Открыть:
    http://localhost:8000/        — каталог + фасеты
    http://localhost:8000/case/asu-createai
    http://localhost:8000/hypothesis/H1
    http://localhost:8000/map     — 2D-проекция корпуса
    http://localhost:8000/match   — подбор аналогов
    http://localhost:8000/api/... — JSON-эндпоинты
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from fastapi import Body, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import agent as agent_mod
from . import graph as graph_mod
from . import match as match_mod
from . import projection as proj_mod
from . import export as export_mod
from . import scenarios as scenarios_mod
from . import search as search_mod
from .db import open_db, fetch_all, fetch_one
from pydantic import BaseModel, Field

from .schemas import CANVAS_SECTIONS, _AXIS_DEFS, _TRANSFORM_MODE_IDS


class SaveSectionPayload(BaseModel):
    text: str
    source: str = "manual"
    status: str = "draft"


class ImportUrlPayload(BaseModel):
    url: str


class RunWavePayload(BaseModel):
    window_from: str
    window_to: str
    focus: str | None = Field(default=None)
    depth: str = Field(default="standard")


class RecheckHypothesisPayload(BaseModel):
    hypothesis_id: str
    window_from: str
    window_to: str


class ExplainMatchPayload(BaseModel):
    case_id: str
    situation: dict[str, Any] = Field(default_factory=dict)


class EntitySavePayload(BaseModel):
    id: str
    draft_md: str
    overwrite: bool = False


class ParseMatchPayload(BaseModel):
    description: str


class BulkExtractPayload(BaseModel):
    text: str = ""
    url: str = ""


class BulkSavePayload(BaseModel):
    candidates: list[dict[str, Any]]


class ProjectCreatePayload(BaseModel):
    id: str
    name: str
    author: str = ""
    summary: str = ""
    agentivity: int | None = None
    ai_pattern: str = ""
    transformation_mode: str = ""
    analogues: str = ""


_ENTITY_DIRS = {
    "type": "types",
    "hypothesis": "hypotheses",
    "tension": "tensions",
    "mode": "modes",
    "counter-signal": "counter-signals",
}

_ENTITY_SCHEMAS = {
    "type": "TypeFrontmatter",
    "hypothesis": "HypothesisFrontmatter",
    "tension": "TensionFrontmatter",
    "mode": "ModeFrontmatter",
    "counter-signal": "CounterSignalFrontmatter",
}


class MatchPayload(BaseModel):
    axes: dict[str, Any] = {}
    top_n: int = 10

ROOT = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))


# -- Jinja2 global: help_for(group, key) — для info-popover --
_HELP_CACHE: dict[str, dict] = {}


def _help_for(group: str, key: str) -> dict:
    """Подсказка из taxonomy/help/<group>.yaml. {} если нет."""
    import yaml as _yaml
    if group not in _HELP_CACHE:
        path = ROOT / "taxonomy" / "help" / f"{group}.yaml"
        if not path.exists():
            _HELP_CACHE[group] = {}
        else:
            try:
                data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                _HELP_CACHE[group] = (
                    data.get("sections")
                    or data.get("profiles")
                    or data.get("items")
                    or data
                    or {}
                )
            except Exception:
                _HELP_CACHE[group] = {}
    return _HELP_CACHE[group].get(key, {}) if isinstance(_HELP_CACHE[group], dict) else {}


templates.env.globals["help_for"] = _help_for


def _cmdk_projects() -> list[dict]:
    """Список проектов для Cmd+K. Кешируется в jinja_env."""
    import frontmatter as _fm
    projects_dir = ROOT / "content" / "projects"
    if not projects_dir.exists():
        return []
    out: list[dict] = []
    for p in sorted(projects_dir.glob("*.md")):
        try:
            post = _fm.load(p)
            out.append({
                "id": post.metadata.get("id", p.stem),
                "name": post.metadata.get("name", p.stem),
            })
        except Exception:
            pass
    return out


templates.env.globals["cmdk_projects"] = _cmdk_projects()


def _root() -> Path:
    return ROOT

app = FastAPI(title="Paideia", version="0.1")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


# ---------------------------------------------------------------------------
# Session + ContextVars middleware (F-token + F9 + F11)
# ---------------------------------------------------------------------------
from . import session as session_mod


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    incoming_sid = request.cookies.get(session_mod.COOKIE_NAME)
    sid = session_mod.ensure_session(incoming_sid)
    client_ip = request.client.host if request.client else None
    if request.headers.get("x-forwarded-for"):
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

    # F9: первый визит на корень → onboarding
    is_first_visit = (incoming_sid is None or incoming_sid != sid)
    has_role = bool(request.cookies.get(session_mod.ROLE_COOKIE))
    path = request.url.path
    SKIP_REDIRECT_PREFIXES = (
        "/onboarding", "/api/", "/static/", "/healthz", "/support",
        "/favicon", "/service",
    )
    if (path == "/" and is_first_visit and not has_role
            and not any(path.startswith(p) for p in SKIP_REDIRECT_PREFIXES)):
        resp = RedirectResponse(url="/onboarding", status_code=303)
        resp.set_cookie(
            key=session_mod.COOKIE_NAME, value=sid,
            max_age=60 * 60 * 24 * 365, httponly=True, samesite="lax",
        )
        return resp

    tok_s = session_mod.current_session.set(sid)
    tok_i = session_mod.current_ip.set(client_ip)
    try:
        response = await call_next(request)
    finally:
        session_mod.current_session.reset(tok_s)
        session_mod.current_ip.reset(tok_i)

    response.set_cookie(
        key=session_mod.COOKIE_NAME, value=sid,
        max_age=60 * 60 * 24 * 365, httponly=True, samesite="lax",
    )
    return response


# Jinja2-глобал: текущая сессия для шаблонов
def _ctx_session(request: Request) -> dict:
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    info = session_mod.get_session_info(sid) if sid else {}
    role = request.cookies.get(session_mod.ROLE_COOKIE)
    return {"sid": sid, "role": role, "info": info}


templates.env.globals["paideia_session"] = _ctx_session


# ---------------------------------------------------------------------------
# HTML страницы
# ---------------------------------------------------------------------------


ROLE_HOME_BLOCKS = {
    "teacher": {
        "title": "🎓 Преподаватель",
        "hint": "Спроектируй свой курс / модуль с опорой на корпус и ТРИЗ-приёмы.",
        "primary_cta": {"label": "🧭 Новый проект через Wizard", "url": "/project/new/wizard"},
        "secondary": [
            {"label": "🎯 Найти аналоги под мой замысел", "url": "/match"},
            {"label": "⚡ 40 ТРИЗ-приёмов под педдизайн", "url": "/methods"},
            {"label": "📚 Моя библиотека (книги, статьи)", "url": "/library"},
        ],
        "default_prompt": "У меня курс/модуль про X для аудитории Y, помоги собрать структуру и найти аналоги",
    },
    "methodologist": {
        "title": "🔬 Методолог / исследователь",
        "hint": "Работай с теорией корпуса: гипотезы, противоречия, сдвиги между волнами.",
        "primary_cta": {"label": "🗺 Карта корпуса", "url": "/map"},
        "secondary": [
            {"label": "📚 Типы / гипотезы / противоречия", "url": "/theory"},
            {"label": "📡 Мониторинг волн (диффы)", "url": "/waves"},
            {"label": "⚙️ Counter-signals (опровергатели)", "url": "/counter-signals"},
        ],
        "default_prompt": "Какие гипотезы корпуса сейчас слабее всего, какие новые противоречия видны",
    },
    "admin": {
        "title": "🏛️ Декан / администратор",
        "hint": "Подбор аналогов под программу, обстрел замысла стейкхолдерами, экспорт документов.",
        "primary_cta": {"label": "🎯 Подбор аналогов (Match)", "url": "/match"},
        "secondary": [
            {"label": "📁 Мои проекты", "url": "/projects"},
            {"label": "🎭 Сценарий: обстрел стейкхолдерами", "url": "/match"},
            {"label": "📋 Каталог · 118 кейсов", "url": "/catalog"},
        ],
        "default_prompt": "Хочу собрать программу переподготовки по X — какие аналоги, какие риски",
    },
    "student": {
        "title": "🎒 Студент / участник курса",
        "hint": "Доступ к материалам активного курса, разбор лекций и заданий.",
        "primary_cta": {"label": "🎓 Курсы", "url": "/courses"},
        "secondary": [
            {"label": "📖 Библиотека книг", "url": "/library"},
            {"label": "📋 Каталог кейсов", "url": "/catalog"},
        ],
        "default_prompt": "Объясни понятие X простыми словами на примерах из курса",
    },
}


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> Any:
    theory = graph_mod.list_all_theory()
    from .db import fetch_one, open_db, fetch_all
    conn = open_db()
    try:
        stats = {
            "cases": fetch_one(conn, "SELECT count(*) AS c FROM cases")["c"],
            "types": fetch_one(conn, "SELECT count(*) AS c FROM types")["c"],
            "hypotheses": fetch_one(conn, "SELECT count(*) AS c FROM hypotheses")["c"],
            "tensions": fetch_one(conn, "SELECT count(*) AS c FROM tensions")["c"],
            "modes": fetch_one(conn, "SELECT count(*) AS c FROM modes")["c"],
            "counter_signals": fetch_one(conn, "SELECT count(*) AS c FROM counter_signals")["c"],
        }
        # Мои проекты (для returning-user секции "Продолжить")
        my_projects = fetch_all(
            conn, "SELECT id, name, status FROM projects ORDER BY updated_at DESC LIMIT 10"
        ) or []

        # Recent activity: последние LLM-runs + последние AgentRun'ы + последние секции
        recent: list[dict] = []
        for r in fetch_all(conn,
            "SELECT id, purpose, target_kind, target_id, section_id, created_at "
            "FROM llm_runs ORDER BY id DESC LIMIT 5"):
            icon = "🧠"
            if r.get("section_id"):
                label = f"section-filler: {r['target_id']} / {r['section_id']}"
                url = f"/case/{r['target_id']}" if r.get("target_kind") == "case" else None
            else:
                label = f"{r['purpose']} → {r.get('target_id') or '?'}"
                url = None
            recent.append({"icon": icon, "label": label, "url": url,
                           "ts": (r.get("created_at") or "")[:16]})
        for r in fetch_all(conn,
            "SELECT id, project_id, profile, status, created_at FROM agent_runs "
            "ORDER BY created_at DESC LIMIT 5"):
            recent.append({
                "icon": "▶",
                "label": f"AgentRun: {r['profile']} на {r['project_id']} ({r['status']})",
                "url": f"/project/{r['project_id']}/run/{r['id']}",
                "ts": (r.get("created_at") or "")[:16],
            })
        recent.sort(key=lambda x: x["ts"], reverse=True)
    finally:
        conn.close()
    user_role = request.cookies.get(session_mod.ROLE_COOKIE)
    role_block = ROLE_HOME_BLOCKS.get(user_role) if user_role else None
    active_course = request.cookies.get(session_mod.COURSE_COOKIE)
    return templates.TemplateResponse(
        request, "home.html",
        {"stats": stats, "theory": theory, "my_projects": my_projects,
         "recent_activity": recent[:10],
         "user_role": user_role, "role_block": role_block,
         "active_course": active_course},
    )


@app.get("/catalog", response_class=HTMLResponse)
def catalog(request: Request, q: str | None = None,
          country: str | None = None, pattern: str | None = None,
          orchestration: str | None = None, pedagogy: str | None = None,
          control: str | None = None, transformation_mode: str | None = None,
          lifecycle_stage: str | None = None,
          agentivity_min: int | None = None, agentivity_max: int | None = None) -> Any:
    results = search_mod.search_cases(
        q=q, country=country, pattern=pattern,
        orchestration=orchestration, pedagogy=pedagogy, control=control,
        transformation_mode=transformation_mode, lifecycle_stage=lifecycle_stage,
        agentivity_min=agentivity_min, agentivity_max=agentivity_max,
        limit=200,
    )
    facets = search_mod.list_facet_values()
    theory = graph_mod.list_all_theory()
    return templates.TemplateResponse(
        request, "index.html",
        {
            "results": results, "facets": facets,
            "theory": theory, "query": {
                "q": q or "", "country": country, "pattern": pattern,
                "orchestration": orchestration, "pedagogy": pedagogy, "control": control,
                "transformation_mode": transformation_mode, "lifecycle_stage": lifecycle_stage,
                "agentivity_min": agentivity_min, "agentivity_max": agentivity_max,
            },
            "transformation_modes": sorted(_TRANSFORM_MODE_IDS),
        },
    )


@app.get("/theory", response_class=HTMLResponse)
def theory_page(request: Request) -> Any:
    return templates.TemplateResponse(
        request, "theory.html", {"theory": graph_mod.list_all_theory()},
    )


@app.get("/theory/new", response_class=HTMLResponse)
def theory_new_page(request: Request, kind: str = "counter-signal") -> Any:
    if kind not in _ENTITY_DIRS:
        kind = "counter-signal"
    templates_md = _entity_md_templates()
    return templates.TemplateResponse(
        request, "entity_edit.html",
        {"mode": "new", "kind": kind, "entity_id": "",
         "draft_md": templates_md[kind],
         "kinds": list(_ENTITY_DIRS.keys())},
    )


@app.get("/theory/{kind}/{entity_id}/edit", response_class=HTMLResponse)
def theory_edit_page(request: Request, kind: str, entity_id: str) -> Any:
    if kind not in _ENTITY_DIRS:
        raise HTTPException(400, f"unknown kind '{kind}'")
    path = _resolve_entity_path(kind, entity_id)
    if not path or not path.exists():
        raise HTTPException(404)
    return templates.TemplateResponse(
        request, "entity_edit.html",
        {"mode": "edit", "kind": kind, "entity_id": entity_id,
         "draft_md": path.read_text(encoding="utf-8"),
         "kinds": list(_ENTITY_DIRS.keys())},
    )


def _entity_md_templates() -> dict[str, str]:
    return {
        "type": """---
id: X
name: <название>
full_name: <развёрнутое название>
wave_introduced: wave-N
markers: []
related_types: []
---

## Описание

[описание паттерна]

## Условия принадлежности

- [маркер 1]
- [маркер 2]
""",
        "hypothesis": """---
id: H6
name: <название гипотезы>
wave_introduced: wave-N
status:
  current: proposed
  history:
    - { wave: wave-N, status: proposed }
markers: []
---

## Тезис

[формулировка гипотезы]

## Условия ложности

[при каких условиях гипотеза опровергается]
""",
        "tension": """---
id: <kebab-case-id>
name: <название противоречия>
pole_a: <полюс A>
pole_b: <полюс B>
---

## Описание

[описание напряжения между полюсами]
""",
        "mode": """---
id: <kebab-case-id>
name: <название моды>
---

## Описание

[описание стратегической моды]
""",
        "counter-signal": """---
id: <kebab-case-id>
name: <название контр-сигнала>
org_name: <организация / источник>
target_hypothesis: H?
wave_introduced: diff-2026-06
---

## Описание

[что произошло, какую гипотезу/тип опровергает или ослабляет]
""",
    }


@app.get("/case/{case_id}", response_class=HTMLResponse)
def case_page(request: Request, case_id: str) -> Any:
    import frontmatter
    case = search_mod.get_case(case_id)
    if not case:
        raise HTTPException(404, f"case '{case_id}' not found")
    # Canvas читаем прямо из md (он обновляется чаще, чем БД)
    md_path = ROOT / case["file_path"]
    canvas_data: dict[str, Any] = {}
    if md_path.exists():
        post = frontmatter.load(md_path)
        canvas_data = post.metadata.get("canvas") or {}
    case["frontmatter"] = json.loads(case.get("frontmatter_json") or "{}")
    section_titles = dict(CANVAS_SECTIONS)
    return templates.TemplateResponse(
        request, "case.html",
        {
            "case": case,
            "axis_defs": _AXIS_DEFS,
            "canvas_sections": CANVAS_SECTIONS,
            "canvas_data": canvas_data,
            "section_titles": section_titles,
        },
    )


# ---------------------------------------------------------------------------
# Canvas editing endpoints
# ---------------------------------------------------------------------------


@app.get("/api/case/{case_id}/canvas/{section_id}/history")
def api_case_section_history(case_id: str, section_id: str, limit: int = 20) -> JSONResponse:
    """git log по файлу кейса с фильтром на изменения секции (по тексту коммита)."""
    import subprocess
    md_path = ROOT / "content" / "cases" / f"{case_id}.md"
    if not md_path.exists():
        raise HTTPException(404, "case not found")
    if not (ROOT / ".git").exists():
        return JSONResponse({"commits": [], "note": "git not initialized"})
    try:
        rel = md_path.relative_to(ROOT)
        out = subprocess.run(
            ["git", "log", f"--max-count={limit}",
             "--pretty=format:%H|%ai|%s", "--", str(rel)],
            cwd=str(ROOT), capture_output=True, text=True, timeout=10, check=False,
        )
        commits = []
        for line in (out.stdout or "").strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                sha, ts, msg = parts
                relevant = section_id in msg or "canvas" in msg
                commits.append({"sha": sha[:12], "date": ts, "message": msg,
                                "section_relevant": relevant})
        return JSONResponse({"section_id": section_id, "case_id": case_id, "commits": commits})
    except Exception as exc:
        return JSONResponse({"commits": [], "error": str(exc)[:200]})


@app.get("/api/case/{case_id}/canvas/{section_id}/version/{sha}")
def api_case_section_version(case_id: str, section_id: str, sha: str) -> JSONResponse:
    """Получить версию секции из указанного git-коммита (через git show)."""
    import subprocess
    import frontmatter as fm_mod
    md_path = ROOT / "content" / "cases" / f"{case_id}.md"
    if not md_path.exists():
        raise HTTPException(404, "case not found")
    try:
        rel = md_path.relative_to(ROOT)
        out = subprocess.run(
            ["git", "show", f"{sha}:{rel}".replace("\\", "/")],
            cwd=str(ROOT), capture_output=True, text=True, timeout=10, check=False,
        )
        if out.returncode != 0:
            raise HTTPException(404, f"sha not found: {sha}")
        post = fm_mod.loads(out.stdout)
        canvas = (post.metadata.get("canvas") or {}).get(section_id) or {}
        return JSONResponse({
            "section_id": section_id, "sha": sha,
            "text": canvas.get("text", ""),
            "status": canvas.get("status"), "source": canvas.get("source"),
            "updated_at": canvas.get("updated_at"),
        })
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, str(exc)[:200])


@app.post("/api/case/{case_id}/canvas/{section_id}/llm-fill")
def api_canvas_llm_fill(case_id: str, section_id: str,
                        model_role: str = "search") -> JSONResponse:
    try:
        result = agent_mod.fill_section(case_id, section_id, model_role=model_role)
        # Автосохранение draft, чтобы юзер не терял результат при закрытии модалки
        if result.get("text"):
            agent_mod.save_section(case_id, section_id, result["text"],
                                   status="draft", source="llm")
            result["auto_saved"] = True
        return JSONResponse(result)
    except FileNotFoundError:
        raise HTTPException(404, f"case '{case_id}' not found")
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"llm error: {exc}")


@app.get("/api/case/{case_id}/canvas/empty-sections")
def api_canvas_empty_sections(case_id: str) -> JSONResponse:
    import frontmatter
    case = search_mod.get_case(case_id)
    if not case:
        raise HTTPException(404, f"case '{case_id}' not found")
    path = ROOT / case["file_path"]
    canvas = frontmatter.load(path).metadata.get("canvas") or {}
    empty = []
    for sid, title in CANVAS_SECTIONS:
        if not (canvas.get(sid) or {}).get("text"):
            empty.append({"id": sid, "title": title})
    return JSONResponse({"empty": empty, "total": len(CANVAS_SECTIONS),
                         "filled": len(CANVAS_SECTIONS) - len(empty)})


@app.post("/api/case/{case_id}/canvas/{section_id}/revert")
def api_canvas_revert(case_id: str, section_id: str) -> JSONResponse:
    """Откатить секцию к 'empty' — удалить запись из canvas."""
    import frontmatter
    case = search_mod.get_case(case_id)
    if not case:
        raise HTTPException(404, f"case '{case_id}' not found")
    path = ROOT / case["file_path"]
    post = frontmatter.load(path)
    canvas = post.metadata.get("canvas") or {}
    if section_id in canvas:
        del canvas[section_id]
        post.metadata["canvas"] = canvas
        raw = frontmatter.dumps(
            post, handler=frontmatter.YAMLHandler(),
            default_flow_style=False, allow_unicode=True, sort_keys=False,
        )
        path.write_text(raw + ("\n" if not raw.endswith("\n") else ""), encoding="utf-8")
    return JSONResponse({"ok": True, "reverted": section_id})


@app.post("/api/case/{case_id}/canvas/{section_id}/save")
def api_canvas_save(case_id: str, section_id: str, payload: SaveSectionPayload) -> JSONResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "empty text")
    try:
        agent_mod.save_section(case_id, section_id, text,
                               status=payload.status, source=payload.source)
        return JSONResponse({"ok": True})
    except FileNotFoundError:
        raise HTTPException(404, f"case '{case_id}' not found")
    except ValueError as exc:
        raise HTTPException(400, str(exc))


# ---------------------------------------------------------------------------
# URL importer
# ---------------------------------------------------------------------------


@app.get("/import", response_class=HTMLResponse)
def import_page(request: Request) -> Any:
    return templates.TemplateResponse(request, "import.html", {})


@app.get("/waves", response_class=HTMLResponse)
def waves_page(request: Request) -> Any:
    waves_dir = ROOT / "content" / "waves"
    waves = []
    if waves_dir.exists():
        for p in sorted(waves_dir.glob("*.md"), reverse=True):
            waves.append({
                "id": p.stem,
                "size_kb": round(p.stat().st_size / 1024, 1),
            })
    return templates.TemplateResponse(request, "waves.html", {"waves": waves})


@app.get("/wave/{wave_id}", response_class=HTMLResponse)
def wave_page(request: Request, wave_id: str) -> Any:
    path = ROOT / "content" / "waves" / f"{wave_id}.md"
    if not path.exists():
        raise HTTPException(404, f"wave '{wave_id}' not found")
    return templates.TemplateResponse(
        request, "wave.html",
        {"wave_id": wave_id, "body_md": path.read_text(encoding="utf-8")},
    )


@app.post("/api/run-wave")
def api_run_wave(payload: RunWavePayload) -> JSONResponse:
    try:
        result = agent_mod.run_wave(payload.window_from, payload.window_to,
                                    payload.focus, depth=payload.depth)
        return JSONResponse(result)
    except Exception as exc:
        raise HTTPException(500, f"wave-runner error: {exc}")


_ENTITY_TABLES = {
    "type": "types", "hypothesis": "hypotheses", "tension": "tensions",
    "mode": "modes", "counter-signal": "counter_signals",
}


def _resolve_entity_path(kind: str, entity_id: str) -> Path | None:
    """Найти md-файл сущности — сначала через БД по file_path, потом по glob."""
    if kind not in _ENTITY_DIRS:
        return None
    from .db import open_db
    conn = open_db()
    try:
        row = conn.execute(
            f"SELECT file_path FROM {_ENTITY_TABLES[kind]} WHERE id=?",
            (entity_id,),
        ).fetchone()
        if row and row["file_path"]:
            return ROOT / row["file_path"]
    finally:
        conn.close()
    # fallback: glob по дирe
    direct = ROOT / "content" / _ENTITY_DIRS[kind] / f"{entity_id}.md"
    if direct.exists():
        return direct
    for cand in (ROOT / "content" / _ENTITY_DIRS[kind]).glob(f"{entity_id}-*.md"):
        return cand
    for cand in (ROOT / "content" / _ENTITY_DIRS[kind]).glob(f"{entity_id}.md"):
        return cand
    return None


@app.get("/api/entity/{kind}/{entity_id}/source")
def api_entity_source(kind: str, entity_id: str) -> JSONResponse:
    if kind not in _ENTITY_DIRS:
        raise HTTPException(400, f"unknown kind '{kind}'")
    path = _resolve_entity_path(kind, entity_id)
    if not path or not path.exists():
        raise HTTPException(404, f"{kind} '{entity_id}' not found")
    return JSONResponse({"id": entity_id, "kind": kind,
                         "file_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                         "draft_md": path.read_text(encoding="utf-8")})


@app.post("/api/entity/{kind}/save")
def api_entity_save(kind: str, payload: EntitySavePayload) -> JSONResponse:
    import re, frontmatter
    from . import schemas as schemas_mod
    if kind not in _ENTITY_DIRS:
        raise HTTPException(400, f"unknown kind '{kind}'")
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", payload.id.strip()).strip("-")
    # типы у нас короткие (A..F) — не понижаем регистр
    if kind != "type":
        slug_lower = slug.lower()
        if slug_lower != slug:
            slug = slug_lower
    if not slug:
        raise HTTPException(400, "invalid id")
    target_dir = ROOT / "content" / _ENTITY_DIRS[kind]
    target_dir.mkdir(parents=True, exist_ok=True)
    # если редактируем существующую — найдём её актуальный путь (часто id ≠ basename)
    if payload.overwrite:
        existing = _resolve_entity_path(kind, slug)
        target = existing if existing else (target_dir / f"{slug}.md")
    else:
        target = target_dir / f"{slug}.md"
    if target.exists() and not payload.overwrite:
        raise HTTPException(409, f"{kind} '{slug}' already exists; use overwrite=true")
    try:
        post = frontmatter.loads(payload.draft_md)
        cls = getattr(schemas_mod, _ENTITY_SCHEMAS[kind])
        cls.model_validate(post.metadata)
    except Exception as exc:
        raise HTTPException(400, f"frontmatter validation failed: {exc}")
    target.write_text(payload.draft_md, encoding="utf-8")
    return JSONResponse({"ok": True, "kind": kind, "id": slug,
                         "path": str(target.relative_to(ROOT))})


@app.post("/api/recheck-hypothesis")
def api_recheck_hypothesis(payload: RecheckHypothesisPayload) -> JSONResponse:
    try:
        return JSONResponse(agent_mod.recheck_hypothesis(
            payload.hypothesis_id, payload.window_from, payload.window_to))
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"recheck error: {exc}")


@app.post("/api/bulk-extract")
async def api_bulk_extract(request: Request) -> JSONResponse:
    """Принимает либо multipart-form (файл) либо JSON {text|url}."""
    content_type = request.headers.get("content-type", "")
    text = ""
    src_label = ""

    if "multipart/form-data" in content_type:
        from .extractors import extract_file
        form = await request.form()
        upload = form.get("file")
        if upload is None:
            raise HTTPException(400, "no file uploaded")
        data = await upload.read()
        try:
            extracted = extract_file(upload.filename, data)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
        text = extracted["text"]
        src_label = upload.filename
    else:
        body = await request.json()
        text = (body.get("text") or "").strip()
        url = (body.get("url") or "").strip()
        if not text and url:
            # для URL — sonar-pro как и в обычном import-url, но возвращаем текст
            # упрощённая логика: качаем через web_search-обёртку llm.chat_search
            raise HTTPException(400, "URL bulk-mode TBD; пока используй textarea или файл")
        src_label = "pasted-text"

    if not text:
        raise HTTPException(400, "empty content")

    try:
        result = agent_mod.bulk_extract_candidates(text)
        result["source_label"] = src_label
        return JSONResponse(result)
    except Exception as exc:
        raise HTTPException(500, f"bulk extract error: {exc}")


@app.post("/api/bulk-save")
def api_bulk_save(payload: BulkSavePayload) -> JSONResponse:
    if not payload.candidates:
        raise HTTPException(400, "no candidates")
    try:
        return JSONResponse(agent_mod.save_bulk_candidates(payload.candidates))
    except Exception as exc:
        raise HTTPException(500, f"save error: {exc}")


@app.get("/project/new/wizard", response_class=HTMLResponse)
def project_wizard(request: Request, teacher_type: str = "") -> Any:
    import yaml as _yaml
    tt_data = _yaml.safe_load((ROOT / "taxonomy" / "teacher_types.yaml").read_text(encoding="utf-8"))
    tr_data = _yaml.safe_load((ROOT / "taxonomy" / "team_roles.yaml").read_text(encoding="utf-8"))
    teacher_types = tt_data.get("teacher_types") or []
    human_roles = tr_data.get("human_roles") or []
    ai_persona_kinds = tr_data.get("ai_persona_kinds") or []
    selected = next((t for t in teacher_types if t["id"] == teacher_type), None)
    return templates.TemplateResponse(
        request, "wizard.html",
        {"teacher_types": teacher_types, "teacher_type": selected,
         "human_roles": human_roles, "ai_persona_kinds": ai_persona_kinds},
    )


@app.post("/api/project/new/wizard")
async def api_project_wizard_submit(request: Request) -> Any:
    """Создаёт content/projects/<slug>.md с предзаполненным канвасом
    и SystemModel из ответов визарда. Перенаправляет на /project/<id>/system."""
    import frontmatter as fm_mod
    import yaml as _yaml
    from fastapi.responses import RedirectResponse
    from datetime import date as _date

    form = await request.form()
    project_id = form.get("project_id", "").strip()
    project_name = form.get("project_name", "").strip()
    teacher_type_id = form.get("teacher_type", "")
    kind = form.get("kind", "module")
    human_roles_picked = form.getlist("human_roles")
    ai_personas_picked = form.getlist("ai_personas")

    if not project_id or not project_name:
        raise HTTPException(400, "project_id и project_name обязательны")

    project_path = ROOT / "content" / "projects" / f"{project_id}.md"
    if project_path.exists():
        raise HTTPException(409, f"project '{project_id}' уже существует")

    tt_data = _yaml.safe_load((ROOT / "taxonomy" / "teacher_types.yaml").read_text(encoding="utf-8"))
    tr_data = _yaml.safe_load((ROOT / "taxonomy" / "team_roles.yaml").read_text(encoding="utf-8"))
    ttype = next((t for t in (tt_data.get("teacher_types") or []) if t["id"] == teacher_type_id), None)
    human_roles_all = {r["id"]: r for r in (tr_data.get("human_roles") or [])}
    ai_personas_all = {p["id"]: p for p in (tr_data.get("ai_persona_kinds") or [])}

    # Собираем ответы из формы
    answers: list[str] = []
    i = 0
    while True:
        a = form.get(f"answer_{i}")
        if a is None:
            break
        answers.append(a.strip())
        i += 1

    # Заполняем canvas из ответов (попадают в signature_context, problem_situation, effect_hypothesis)
    canvas: dict[str, Any] = {}
    today = _date.today().isoformat()
    if ttype and answers:
        # Первый ответ → signature_context, второй → problem_situation, третий → effect_hypothesis
        targets = ["signature_context", "problem_situation", "effect_hypothesis"]
        for j, ans in enumerate(answers):
            if not ans:
                continue
            tgt = targets[j] if j < len(targets) else "open_questions"
            existing = canvas.get(tgt, {}).get("text", "")
            new_text = (existing + "\n\n" + ans).strip() if existing else ans
            canvas[tgt] = {"text": new_text, "status": "draft",
                           "source": "manual", "updated_at": today}

    # Ролевая модель → team_roles
    team_text_lines = []
    for rid in human_roles_picked:
        r = human_roles_all.get(rid)
        if r:
            team_text_lines.append(f"- **{r['name']}** (human): {r['function'].strip()}")
    for pid in ai_personas_picked:
        p = ai_personas_all.get(pid)
        if p:
            team_text_lines.append(f"- **{p['name']}** (ai-persona): {p['when_useful']}")
    if team_text_lines:
        canvas["team_roles"] = {
            "text": "\n".join(team_text_lines),
            "status": "draft", "source": "manual", "updated_at": today,
        }

    # Frontmatter проекта
    fm = {
        "id": project_id,
        "name": project_name,
        "status": "draft",
        "ai": {"pattern": None, "agentivity": None, "technologies": []},
        "facets": {"orchestration": None, "pedagogy": None, "control": None, "economy": None},
        "transformation_mode": None,
        "created_at": today,
        "teacher_type_at_start": teacher_type_id,
        "canvas": canvas,
    }
    post = fm_mod.Post(content=f"# {project_name}\n\nСоздано через wizard.\n", **fm)
    raw = fm_mod.dumps(post, handler=fm_mod.YAMLHandler(),
                       default_flow_style=False, allow_unicode=True, sort_keys=False)
    project_path.write_text(raw + "\n", encoding="utf-8")

    # Триггерим build_system_models для нового проекта (LLM-вызов)
    try:
        from scripts.build_system_models import _build_one
        prompt_path = ROOT / "prompts" / "canvas_to_system_model.md"
        from .llm import get_llm
        _build_one(project_path, get_llm(), prompt_path.read_text(encoding="utf-8"))
    except Exception:
        pass  # не валим — пользователь увидит на странице

    suggested_run = ttype.get("suggest_run") if ttype else None
    if not suggested_run:
        # Фоллбек на default-профиль по роли пользователя (F9+5)
        ROLE_DEFAULT_PROFILE = {
            "teacher":       "kosmos",
            "methodologist": "hypothesis_forge",
            "admin":         "stakeholder_pressure",
            # student обычно не создаёт проекты — но если попал сюда, kosmos
            "student":       "kosmos",
        }
        user_role = request.cookies.get(session_mod.ROLE_COOKIE)
        suggested_run = ROLE_DEFAULT_PROFILE.get(user_role or "")
    if suggested_run:
        return RedirectResponse(
            url=f"/project/{project_id}/runs?suggest={suggested_run}",
            status_code=303,
        )
    return RedirectResponse(url=f"/project/{project_id}/system", status_code=303)


@app.get("/elective-space", response_class=HTMLResponse)
def elective_space_page(request: Request) -> Any:
    import yaml as _yaml
    path = ROOT / "taxonomy" / "elective_space.yaml"
    data = _yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    return templates.TemplateResponse(request, "elective_space.html", {"data": data})


@app.get("/counter-signals", response_class=HTMLResponse)
def counter_signals_page(request: Request) -> Any:
    signals = fetch_all(open_db(),
        "SELECT id, name, org_name, target_hypothesis, wave_introduced "
        "FROM counter_signals ORDER BY id")
    return templates.TemplateResponse(request, "counter_signals.html", {"signals": signals})


@app.get("/methods", response_class=HTMLResponse)
def methods_page(request: Request, q: str = "", applies_to: str = "") -> Any:
    import yaml as _yaml
    path = ROOT / "taxonomy" / "triz_methods_edu.yaml"
    if not path.exists():
        return templates.TemplateResponse(request, "methods.html",
            {"methods": [], "q": "", "applies_to": "", "fields": []})
    data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    methods = data.get("methods") or []

    # фильтры
    if q:
        ql = q.lower()
        methods = [m for m in methods if
            ql in (m.get("name_ru","") or "").lower()
            or ql in (m.get("classic","") or "").lower()
            or ql in (m.get("pedagogical","") or "").lower()
            or ql in (m.get("when_useful","") or "").lower()
        ]
    if applies_to:
        methods = [m for m in methods if applies_to in (m.get("applies_to") or [])]

    # поля для фильтра
    fields = sorted({f for m in (data.get("methods") or []) for f in (m.get("applies_to") or [])})
    return templates.TemplateResponse(request, "methods.html",
        {"methods": methods, "q": q, "applies_to": applies_to, "fields": fields})


def _build_project_stepper(project_id: str, current: str) -> dict:
    """Сбор информации о шагах workflow проекта для _project_stepper.html.

    current: dashboard | system | canvas | vepol | lab | runs | export
    """
    import frontmatter as _fm
    from .triz.repository import get_system_model
    from .triz.agent_run import list_runs as _list_runs

    out: dict = {"current": current}

    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if path.exists():
        post = _fm.load(path)
        canvas = post.metadata.get("canvas") or {}
        canvas_filled = sum(
            1 for v in canvas.values()
            if isinstance(v, dict) and (v.get("text") or "").strip()
        )
        out["canvas"] = f"{canvas_filled}/18 секций"
    else:
        out["canvas"] = "—"

    model = get_system_model(project_id)
    if model:
        out["system"] = f"✓ {model.maturity}"
        n_c = len(model.contradictions)
        n_r = len(model.working_organ)
        out["vepol"] = f"{n_r} ролей · {n_c} ⚡"
    else:
        out["system"] = "не построена"
        out["vepol"] = "—"

    runs = _list_runs(project_id, limit=50)
    if runs:
        applied = sum(1 for r in runs if r.get("status") == "applied")
        awaiting = sum(1 for r in runs if r.get("status") == "awaiting_approval")
        if awaiting:
            out["runs"] = f"{len(runs)} runs · {awaiting} ждёт"
        else:
            out["runs"] = f"{len(runs)} runs · {applied} ✓"
    else:
        out["runs"] = "пока нет"

    out["dashboard"] = "обзор"

    # Lab
    try:
        from .scenarios import list_runs as _scen_runs
        scen = _scen_runs(project_id, limit=30)
        out["lab"] = f"{len(scen)} прогонов" if scen else "24 сценария"
    except Exception:
        out["lab"] = "24 сценария"

    # Export
    exports_dir = ROOT / "content" / "exports" / project_id
    if exports_dir.exists():
        n = len(list(exports_dir.glob("*.md")))
        out["export"] = f"{n} док-в" if n else "пусто"
    else:
        out["export"] = "пусто"

    return out


@app.get("/service", response_class=HTMLResponse)
def service_page(request: Request) -> Any:
    """Сервисный режим — admin/devops landing."""
    import json as _json
    candidates_path = ROOT / "db" / "foundry_candidates.json"
    foundry_sources = 0; foundry_candidates = 0; foundry_high = 0
    if candidates_path.exists():
        try:
            data = _json.loads(candidates_path.read_text(encoding="utf-8"))
            sources = data.get("sources") or []
            foundry_sources = len(sources)
            foundry_candidates = sum(s.get("candidates_count", 0) for s in sources)
            foundry_high = sum(
                1
                for s in sources
                for c in (s.get("parsed", {}) or {}).get("candidates", [])
                if c.get("applicability_to_paideia") == "high"
            )
        except Exception:
            pass

    conn = open_db()
    try:
        llm_stats = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(duration_ms),0) AS d, "
            "COALESCE(SUM(cost_usd),0) AS cost FROM llm_runs"
        ).fetchone()
        counters = {
            "counter_signals": conn.execute("SELECT COUNT(*) FROM counter_signals").fetchone()[0],
            "types": conn.execute("SELECT COUNT(*) FROM types").fetchone()[0],
            "hypotheses": conn.execute("SELECT COUNT(*) FROM hypotheses").fetchone()[0],
            "tensions": conn.execute("SELECT COUNT(*) FROM tensions").fetchone()[0],
            "modes": conn.execute("SELECT COUNT(*) FROM modes").fetchone()[0],
            "l1_agents": conn.execute(
                "SELECT COUNT(*) FROM content_agents WHERE status='active'"
            ).fetchone()[0],
            "stakeholders": conn.execute("SELECT COUNT(*) FROM stakeholders").fetchone()[0],
            "feedback_threads": conn.execute("SELECT COUNT(*) FROM feedback_threads").fetchone()[0],
        }
    finally:
        conn.close()

    return templates.TemplateResponse(
        request, "service.html",
        {"stats": {
            "foundry_sources": foundry_sources,
            "foundry_candidates": foundry_candidates,
            "foundry_high": foundry_high,
            "llm_runs": llm_stats["n"],
            "llm_total_seconds": llm_stats["d"] / 1000,
            "llm_total_cost": llm_stats["cost"],
            **counters,
        }},
    )


@app.get("/library", response_class=HTMLResponse)
def library_page(request: Request) -> Any:
    from . import library as lib
    books = lib.list_books()
    conn = open_db()
    try:
        total_chunks = conn.execute("SELECT COALESCE(SUM(chunk_count),0) FROM library_books").fetchone()[0]
        total_concepts = conn.execute("SELECT COUNT(*) FROM library_concepts").fetchone()[0]
    finally:
        conn.close()
    return templates.TemplateResponse(
        request, "library.html",
        {"books": books, "total_chunks": total_chunks, "total_concepts": total_concepts},
    )


@app.get("/library/upload", response_class=HTMLResponse)
def library_upload_page(request: Request) -> Any:
    return templates.TemplateResponse(request, "library_upload.html", {})


@app.get("/library/conflicts", response_class=HTMLResponse)
def library_conflicts_page_early(request: Request, relation: str = "conflicts") -> Any:
    """F1 selector: пары concept × concept по отношениям. Регистрируется ДО /library/{book_id}."""
    from . import selector as sel_mod
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """SELECT cc.relation, cc.school_a, cc.school_b, cc.rationale,
                      cc.similarity, cc.created_at,
                      a.id AS a_id, a.name AS a_name, a.definition AS a_def,
                      ba.title AS a_book, ba.authors AS a_authors,
                      b.id AS b_id, b.name AS b_name, b.definition AS b_def,
                      bb.title AS b_book, bb.authors AS b_authors
               FROM concept_conflicts cc
               JOIN library_concepts a ON a.id = cc.concept_a_id
               JOIN library_concepts b ON b.id = cc.concept_b_id
               JOIN library_books ba ON ba.id = a.book_id
               JOIN library_books bb ON bb.id = b.book_id
               WHERE cc.relation = ?
               ORDER BY cc.similarity DESC LIMIT 300""",
            (relation,),
        )
    finally:
        conn.close()
    stats = sel_mod.stats()
    return templates.TemplateResponse(
        request, "library_conflicts.html",
        {"pairs": rows, "stats": stats, "filter_relation": relation},
    )


@app.get("/library/{book_id}", response_class=HTMLResponse)
def library_book_page(request: Request, book_id: str) -> Any:
    if book_id in ("conflicts", "upload", "new"):
        raise HTTPException(404)
    from . import library as lib
    book = lib.get_book(book_id)
    if not book:
        raise HTTPException(404, f"book '{book_id}' not found")
    return templates.TemplateResponse(request, "library_book.html", {"book": book})


@app.post("/api/library/upload")
async def api_library_upload(request: Request) -> Any:
    """multipart/form-data: file + title + authors + year. Запускает ingest синхронно."""
    from fastapi.responses import RedirectResponse
    from . import library as lib
    from scripts.library_ingest import phase_full

    form = await request.form()
    file = form.get("file")
    title = (form.get("title") or "").strip()
    authors = (form.get("authors") or "").strip()
    year_raw = (form.get("year") or "").strip()
    if not file or not title:
        raise HTTPException(400, "file + title required")
    year = int(year_raw) if year_raw.isdigit() else None

    ext = Path(file.filename).suffix.lower().lstrip(".") or "bin"
    book_id = lib.register_book(title=title, authors=authors, year=year,
                                source_kind=ext)
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        lib.set_status(book_id, "failed", "file > 50MB")
        raise HTTPException(400, "file too large (max 50 MB)")
    lib.save_source_file(book_id, file.filename, data)

    # запускаем pipeline синхронно (для простоты, без background-job)
    try:
        phase_full(book_id, max_sections=20)  # ограничение чтобы не разорить
    except Exception as exc:
        lib.set_status(book_id, "failed", str(exc)[:500])
        return RedirectResponse(url=f"/library/{book_id}", status_code=303)

    return RedirectResponse(url=f"/library/{book_id}", status_code=303)


@app.post("/api/library/{book_id}/extract-concepts")
def api_library_extract_concepts(book_id: str) -> Any:
    from fastapi.responses import RedirectResponse
    from scripts.library_ingest import phase_concepts
    try:
        phase_concepts(book_id, max_sections=20)
    except Exception as exc:
        raise HTTPException(500, f"extract failed: {exc}")
    return RedirectResponse(url=f"/library/{book_id}", status_code=303)


@app.get("/foundry", response_class=HTMLResponse)
def foundry_page(request: Request) -> Any:
    """Agent Foundry — обзор кандидатов из PDF-доноров + кнопка активации."""
    import json as _json
    candidates_path = ROOT / "db" / "foundry_candidates.json"
    sources: list[dict] = []
    if candidates_path.exists():
        try:
            data = _json.loads(candidates_path.read_text(encoding="utf-8"))
            sources = data.get("sources") or []
        except Exception:
            pass

    total_candidates = sum(s.get("candidates_count", 0) for s in sources)
    high = sum(
        1
        for s in sources
        for c in (s.get("parsed", {}) or {}).get("candidates", [])
        if c.get("applicability_to_paideia") == "high"
    )
    rejected = sum(
        len((s.get("parsed", {}) or {}).get("rejected", []) or [])
        for s in sources
    )

    from .triz.agents import list_agent_specs
    active = len(list_agent_specs(status="active"))

    return templates.TemplateResponse(
        request, "foundry.html",
        {
            "sources": sources,
            "stats": {
                "sources": len(sources),
                "candidates": total_candidates,
                "high_apply": high,
                "rejected": rejected,
                "active_agents": active,
            },
        },
    )


@app.post("/api/foundry/activate")
async def api_foundry_activate(request: Request) -> Any:
    """Сохранить кандидата как draft AgentSpec в content/agents/L1/."""
    import json as _json
    from fastapi.responses import RedirectResponse
    import yaml as _yaml

    form = await request.form()
    src_pdf = form.get("source_pdf", "")
    idx = int(form.get("candidate_index", "-1"))

    candidates_path = ROOT / "db" / "foundry_candidates.json"
    if not candidates_path.exists():
        raise HTTPException(404, "foundry_candidates.json not found")
    data = _json.loads(candidates_path.read_text(encoding="utf-8"))
    source = next((s for s in (data.get("sources") or []) if s.get("source") == src_pdf), None)
    if not source:
        raise HTTPException(404, f"source '{src_pdf}' not in candidates")
    candidates = (source.get("parsed", {}) or {}).get("candidates") or []
    if idx < 0 or idx >= len(candidates):
        raise HTTPException(400, "invalid candidate_index")

    cand = candidates[idx]
    agent_id = cand.get("name_normalized") or f"imported-{src_pdf}-{idx}"
    target_dir = ROOT / "content" / "agents" / cand.get("level", "L1")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{agent_id}.md"

    fm = {
        "agent_id": agent_id,
        "name": cand.get("name_orig", agent_id),
        "level": cand.get("level", "L1"),
        "class": "working",
        "purpose": cand.get("purpose", ""),
        "field_function": cand.get("field_function", ""),
        "activation_conditions": cand.get("activation_conditions", []),
        "inputs": cand.get("inputs", []),
        "outputs": cand.get("outputs", []),
        "allowed_actions": cand.get("allowed_actions", []),
        "forbidden_actions": cand.get("forbidden_actions", []),
        "version": "0.1.0",
        "provenance": f"foundry-import: {src_pdf}",
        "status": "draft",
    }
    body = (
        f"## Kernel prompt\n\n{cand.get('kernel_prompt_draft', '')}\n\n"
        f"## Adaptation notes\n\n{cand.get('adaptation_notes', '')}\n"
    )

    raw = "---\n" + _yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + body
    target.write_text(raw, encoding="utf-8")

    return RedirectResponse(url="/foundry", status_code=303)


@app.get("/llm-runs", response_class=HTMLResponse)
def llm_runs_page(request: Request, purpose: str = "", status: str = "",
                  limit: int = 200) -> Any:
    conn = open_db()
    try:
        where, params = [], []
        if purpose:
            where.append("purpose = ?")
            params.append(purpose)
        if status:
            where.append("status = ?")
            params.append(status)
        sql = "SELECT * FROM llm_runs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        runs = fetch_all(conn, sql, tuple(params))
        purposes = [r["purpose"] for r in fetch_all(conn,
            "SELECT DISTINCT purpose FROM llm_runs WHERE purpose IS NOT NULL ORDER BY purpose")]
        total_row = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(duration_ms),0) AS d, "
            "COALESCE(SUM(tokens_total),0) AS tok, "
            "COALESCE(SUM(cost_usd),0) AS cost, "
            "COALESCE(SUM(cached),0) AS cached_n "
            "FROM llm_runs"
        ).fetchone()
        total = total_row["n"]
        total_seconds = total_row["d"] / 1000
        total_tokens = total_row["tok"]
        total_cost = total_row["cost"]
        cached_count = total_row["cached_n"]
    finally:
        conn.close()
    return templates.TemplateResponse(
        request, "llm_runs.html",
        {"runs": runs, "purposes": purposes, "total": total,
         "total_seconds": total_seconds, "total_tokens": total_tokens,
         "total_cost": total_cost, "cached_count": cached_count,
         "filter_purpose": purpose, "filter_status": status},
    )


@app.get("/llm-runs/{run_id}", response_class=HTMLResponse)
def llm_run_page(request: Request, run_id: int) -> Any:
    conn = open_db()
    try:
        rows = fetch_all(conn, "SELECT * FROM llm_runs WHERE id = ?", (run_id,))
        if not rows:
            raise HTTPException(404, "run not found")
        run = rows[0]
    finally:
        conn.close()
    return templates.TemplateResponse(request, "llm_run.html", {"run": run})


@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request) -> Any:
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """
            SELECT id, name, author, status, org_name, pattern, agentivity
            FROM projects ORDER BY COALESCE(created_at, '') DESC, name
            """,
        )
    finally:
        conn.close()
    return templates.TemplateResponse(request, "projects.html", {"projects": rows})


@app.get("/project/new", response_class=HTMLResponse)
def project_new_form(request: Request) -> Any:
    return templates.TemplateResponse(
        request, "project_new.html",
        {"transformation_modes": sorted(_TRANSFORM_MODE_IDS)},
    )


@app.post("/project/new")
def project_new_submit(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    author: str = Form(""),
    summary: str = Form(""),
    agentivity: int | None = Form(None),
    ai_pattern: str = Form(""),
    transformation_mode: str = Form(""),
    analogues: str = Form(""),
) -> Any:
    import frontmatter as fm_mod
    pid = id.strip().lower()
    if not pid or not all(c.isalnum() or c in "-_" for c in pid):
        raise HTTPException(400, "id must be a slug (alnum + - + _)")
    path = ROOT / "content" / "projects" / f"{pid}.md"
    if path.exists():
        raise HTTPException(409, f"project '{pid}' already exists")
    path.parent.mkdir(parents=True, exist_ok=True)

    fm: dict[str, Any] = {
        "id": pid, "name": name.strip(), "kind": "project",
        "status": "draft",
    }
    if author.strip():
        fm["author"] = author.strip()
    if ai_pattern:
        fm["ai"] = {"pattern": ai_pattern}
    if agentivity is not None:
        fm.setdefault("ai", {})["agentivity"] = agentivity
    if transformation_mode:
        fm["transformation_mode"] = transformation_mode
    analogue_ids = [a.strip() for a in analogues.split(",") if a.strip()]
    if analogue_ids:
        fm["analogues"] = analogue_ids
    if summary.strip():
        from datetime import date
        fm["canvas"] = {
            "signature_context": {
                "text": summary.strip(), "status": "draft", "source": "manual",
                "updated_at": date.today().isoformat(),
            },
        }
    body = f"\n## Замысел\n\n{summary.strip() or '(пока пусто — заполни через канвас)'}\n"
    post = fm_mod.Post(content=body, **fm)
    raw = fm_mod.dumps(post, handler=fm_mod.YAMLHandler(),
                       default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(raw + "\n", encoding="utf-8")
    return RedirectResponse(f"/project/{pid}", status_code=303)


@app.get("/project/{project_id}/runs", response_class=HTMLResponse)
def project_runs_page(request: Request, project_id: str) -> Any:
    import frontmatter as fm_mod
    from .triz.agent_run import list_runs
    from .triz.agents import load_spaces

    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    project = {
        "id": post.metadata.get("id", project_id),
        "name": post.metadata.get("name", project_id),
    }
    runs = list_runs(project_id)
    spaces = load_spaces()
    return templates.TemplateResponse(
        request, "agent_runs_list.html",
        {"project": project, "runs": runs, "spaces": spaces,
         "stepper": _build_project_stepper(project_id, "runs")},
    )


@app.get("/project/{project_id}/run/{run_id}", response_class=HTMLResponse)
def project_run_page(request: Request, project_id: str, run_id: str) -> Any:
    import frontmatter as _fm
    from .triz.agent_run import get_run as _get_run
    run = _get_run(run_id)
    if not run or run.get("project_id") != project_id:
        raise HTTPException(404, "run not found")
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    project = {"id": project_id, "name": project_id}
    if path.exists():
        post = _fm.load(path)
        project = {"id": post.metadata.get("id", project_id),
                   "name": post.metadata.get("name", project_id)}
    return templates.TemplateResponse(
        request, "agent_run.html",
        {"run": run, "project": project,
         "stepper": _build_project_stepper(project_id, "runs")},
    )


@app.post("/api/project/{project_id}/agent-run/start")
def api_agent_run_start(project_id: str, profile: str = Form("default"),
                        space_id: str = Form(""), goal: str = Form("")) -> Any:
    """Создать AgentRun + сразу execute + редирект на страницу run."""
    from fastapi.responses import RedirectResponse
    from .triz.agent_run import AgentRunSpec, create_run, execute_run
    from .triz.repository import get_system_model

    model = get_system_model(project_id)
    if not model:
        raise HTTPException(400, "system model not found — сначала build её из канваса")

    spec = AgentRunSpec(
        project_id=project_id,
        profile=profile,
        target_object_kind="system_model",
        target_object_id=model.id,
        goal=goal,
        space_id=space_id or None,
    )
    run_id = create_run(spec)
    # запускаем сразу (синхронно — может занять 30-90 с)
    try:
        execute_run(run_id)
    except Exception as exc:
        # не валим — пользователь увидит статус на странице
        pass
    return RedirectResponse(url=f"/project/{project_id}/run/{run_id}", status_code=303)


@app.post("/api/agent-run/{run_id}/execute")
def api_agent_run_execute(run_id: str) -> Any:
    from fastapi.responses import RedirectResponse
    from .triz.agent_run import execute_run, get_run as _get_run
    run = _get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    try:
        execute_run(run_id)
    except Exception as exc:
        raise HTTPException(500, f"execute failed: {exc}")
    return RedirectResponse(url=f"/project/{run['project_id']}/run/{run_id}", status_code=303)


@app.post("/api/agent-run/{run_id}/apply")
async def api_agent_run_apply(run_id: str, request: Request) -> Any:
    from fastapi.responses import RedirectResponse
    from .triz.agent_run import apply_run, get_run as _get_run
    form = await request.form()
    approved = form.getlist("approved_op_ids")
    run = _get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    apply_run(run_id, approved_op_ids=approved)
    return RedirectResponse(url=f"/project/{run['project_id']}/run/{run_id}", status_code=303)


@app.get("/api/agent-run/{run_id}/cancel")
def api_agent_run_cancel(run_id: str) -> Any:
    from fastapi.responses import RedirectResponse
    from .triz.agent_run import cancel_run, get_run as _get_run
    run = _get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    cancel_run(run_id)
    return RedirectResponse(url=f"/project/{run['project_id']}/run/{run_id}", status_code=303)


@app.get("/project/{project_id}/dashboard", response_class=HTMLResponse)
def project_dashboard(request: Request, project_id: str) -> Any:
    import frontmatter as fm_mod
    from .triz.repository import get_system_model
    from .triz.agent_run import list_runs as _list_runs

    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    project = {"id": post.metadata.get("id", project_id),
               "name": post.metadata.get("name", project_id)}
    canvas = post.metadata.get("canvas") or {}
    canvas_filled = sum(1 for v in canvas.values()
                        if isinstance(v, dict) and (v.get("text") or "").strip())
    model = get_system_model(project_id)
    runs = _list_runs(project_id)
    last_run = runs[0] if runs else None
    applied_runs = sum(1 for r in runs if r.get("status") == "applied")
    return templates.TemplateResponse(
        request, "project_dashboard.html",
        {"project": project, "canvas_filled": canvas_filled, "model": model,
         "runs": runs, "last_run": last_run, "applied_runs": applied_runs,
         "stepper": _build_project_stepper(project_id, "dashboard")},
    )


@app.get("/project/{project_id}/vepol", response_class=HTMLResponse)
def project_vepol(request: Request, project_id: str) -> Any:
    import frontmatter as fm_mod
    from .triz.repository import get_system_model
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    project = {"id": post.metadata.get("id", project_id),
               "name": post.metadata.get("name", project_id)}
    model = get_system_model(project_id)
    if not model:
        raise HTTPException(400, "SystemModel не построена для проекта")
    return templates.TemplateResponse(
        request, "vepol.html",
        {"project": project, "model": model,
         "stepper": _build_project_stepper(project_id, "vepol")},
    )


@app.get("/project/{project_id}/system", response_class=HTMLResponse)
def project_system_view(request: Request, project_id: str) -> Any:
    """Default view проекта v3 — EducationalSystemModel."""
    import frontmatter as fm_mod
    from .triz.repository import get_system_model

    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    project = {
        "id": post.metadata.get("id", project_id),
        "name": post.metadata.get("name", project_id),
    }
    model = get_system_model(project_id)
    return templates.TemplateResponse(
        request, "system_view.html",
        {"project": project, "model": model,
         "stepper": _build_project_stepper(project_id, "system")},
    )


@app.post("/api/project/{project_id}/system/build")
def api_build_system_model(project_id: str) -> Any:
    """Запустить миграцию канваса → SystemModel для проекта (LLM-вызов)."""
    import frontmatter as fm_mod
    import json as _json
    from scripts.build_system_models import _build_one
    from .llm import get_llm

    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")

    prompt_path = ROOT / "prompts" / "canvas_to_system_model.md"
    if not prompt_path.exists():
        raise HTTPException(500, "canvas_to_system_model.md missing")

    system_prompt = prompt_path.read_text(encoding="utf-8")
    llm = get_llm()
    result = _build_one(path, llm, system_prompt, dry_run=False)
    if result.get("status") != "ok":
        raise HTTPException(500, f"build failed: {result}")
    # после успешной сборки — редирект на /system
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/project/{project_id}/system", status_code=303)


@app.get("/project/{project_id}", response_class=HTMLResponse)
def project_page(request: Request, project_id: str) -> Any:
    import frontmatter as fm_mod
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    fm = post.metadata
    project = {
        "id": fm.get("id"), "name": fm.get("name"), "author": fm.get("author"),
        "status": fm.get("status") or "draft",
        "pattern": (fm.get("ai") or {}).get("pattern"),
        "agentivity": (fm.get("ai") or {}).get("agentivity"),
        "orchestration": (fm.get("facets") or {}).get("orchestration"),
        "pedagogy": (fm.get("facets") or {}).get("pedagogy"),
        "control": (fm.get("facets") or {}).get("control"),
        "transformation_mode": fm.get("transformation_mode"),
    }
    canvas_data = fm.get("canvas") or {}
    analogue_ids = fm.get("analogues") or []
    analogues = []
    if analogue_ids:
        conn = open_db()
        try:
            analogues = fetch_all(
                conn,
                f"SELECT id, name FROM cases WHERE id IN ({','.join('?'*len(analogue_ids))})",
                tuple(analogue_ids),
            )
        finally:
            conn.close()
    return templates.TemplateResponse(
        request, "project.html",
        {
            "project": project,
            "canvas_sections": CANVAS_SECTIONS,
            "canvas_data": canvas_data,
            "section_titles": dict(CANVAS_SECTIONS),
            "section_ids": [k for k, _ in CANVAS_SECTIONS],
            "analogues": analogues,
            "stepper": _build_project_stepper(project_id, "canvas"),
        },
    )


@app.post("/api/project/{project_id}/canvas/{section_id}/llm-fill")
def api_project_canvas_llm_fill(project_id: str, section_id: str) -> JSONResponse:
    try:
        return JSONResponse(agent_mod.fill_project_section(project_id, section_id))
    except FileNotFoundError:
        raise HTTPException(404, f"project '{project_id}' not found")
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"llm error: {exc}")


@app.get("/project/{project_id}/lab", response_class=HTMLResponse)
def project_lab(request: Request, project_id: str) -> Any:
    import frontmatter as fm_mod
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    project = {"id": post.metadata.get("id"), "name": post.metadata.get("name")}
    scenarios = scenarios_mod.load_registry()
    runs = scenarios_mod.list_runs(project_id, limit=30)
    return templates.TemplateResponse(
        request, "lab.html",
        {"project": project, "scenarios": scenarios, "runs": runs,
         "stepper": _build_project_stepper(project_id, "lab")},
    )


@app.get("/project/{project_id}/run/{run_id}", response_class=HTMLResponse)
def scenario_run_page(request: Request, project_id: str, run_id: int) -> Any:
    run = scenarios_mod.get_run(run_id)
    if not run or run["project_id"] != project_id:
        raise HTTPException(404, "run not found")
    project = {"id": project_id, "name": project_id}
    return templates.TemplateResponse(
        request, "scenario_result.html",
        {"project_id": project_id, "project": project, "run": run,
         "stepper": _build_project_stepper(project_id, "lab")},
    )


@app.post("/api/project/{project_id}/scenario/{scenario_id}/run")
def api_run_scenario(project_id: str, scenario_id: str,
                     case_param: str | None = None) -> JSONResponse:
    try:
        result = scenarios_mod.run_scenario(project_id, scenario_id, case_param=case_param)
        return JSONResponse({
            "run_id": result["run_id"],
            "duration_ms": result["duration_ms"],
            "context_meta": result.get("context_meta"),
        })
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"scenario error: {exc}")


@app.get("/project/{project_id}/export", response_class=HTMLResponse)
def project_export_page(request: Request, project_id: str) -> Any:
    import frontmatter as fm_mod
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise HTTPException(404, f"project '{project_id}' not found")
    post = fm_mod.load(path)
    project = {"id": post.metadata.get("id"), "name": post.metadata.get("name")}
    return templates.TemplateResponse(
        request, "export.html",
        {"project": project, "docs": export_mod.DOCS,
         "exports": export_mod.list_exports(project_id),
         "stepper": _build_project_stepper(project_id, "export")},
    )


@app.post("/api/project/{project_id}/export/{doc_id}")
def api_build_export(project_id: str, doc_id: str) -> JSONResponse:
    try:
        return JSONResponse(export_mod.build_document(project_id, doc_id))
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"export error: {exc}")


@app.get("/project/{project_id}/export/{filename}", response_class=HTMLResponse)
def project_export_file(request: Request, project_id: str, filename: str) -> Any:
    try:
        content = export_mod.read_export(project_id, filename)
    except FileNotFoundError:
        raise HTTPException(404, "export not found")
    # рендер MD прямо как plain
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content)


@app.post("/api/project/{project_id}/canvas/{section_id}/save")
def api_project_canvas_save(project_id: str, section_id: str,
                            payload: SaveSectionPayload) -> JSONResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "empty text")
    try:
        agent_mod.save_section(project_id, section_id, text,
                               status=payload.status, source=payload.source,
                               entity_kind="project")
        return JSONResponse({"ok": True})
    except FileNotFoundError:
        raise HTTPException(404, f"project '{project_id}' not found")
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.get("/archive", response_class=HTMLResponse)
def archive_page(request: Request, q: str = "") -> Any:
    from . import retrieve as retrieve_mod
    files = retrieve_mod.list_archive_files()
    stats = retrieve_mod.archive_stats()
    hits = retrieve_mod.retrieve_archive(q, top_k=8) if q.strip() else []
    return templates.TemplateResponse(
        request, "archive.html",
        {"files": files, "stats": stats, "query": q, "hits": hits},
    )


class AskConciergePayload(BaseModel):
    text: str
    mode: str = "explore"           # explore | project
    model_role: str = "fast"        # F10: fast | deep | search


@app.post("/api/ask")
def api_ask_concierge(payload: AskConciergePayload, request: Request) -> JSONResponse:
    # F11: rate-limit
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    if request.headers.get("x-forwarded-for"):
        ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    rl = session_mod.check_rate_limit(sid, ip, payload.model_role)
    if not rl["allowed"]:
        reason = rl["reason"]
        msg = ("Дневной бюджет платформы исчерпан. Попробуй завтра или поддержи "
               "проект на /support — supporter без лимитов."
               if reason == "global_budget_exhausted" else
               f"Лимит для модели «{payload.model_role}» исчерпан "
               f"({rl.get('used_today',0)}/{rl['limit']} сегодня). "
               "Попробуй модель fast или загляни на /support.")
        return JSONResponse(
            {"error": "rate_limited", "reason": reason, "limit_info": rl, "message": msg},
            status_code=429,
        )
    try:
        user_role = request.cookies.get(session_mod.ROLE_COOKIE)
        active_course = request.cookies.get(session_mod.COURSE_COOKIE)
        return JSONResponse(agent_mod.ask_concierge(
            payload.text, payload.mode, model_role=payload.model_role,
            user_role=user_role, active_course_id=active_course))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"concierge error: {exc}")


@app.get("/api/session/stats")
def api_session_stats(request: Request) -> JSONResponse:
    """F-token: токены и стоимость текущей сессии для навбара."""
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    stats = session_mod.session_stats(sid)
    stats["budget"] = session_mod.daily_budget_status()
    return JSONResponse(stats)


@app.get("/api/session/limits")
def api_session_limits(request: Request, model_role: str = "fast") -> JSONResponse:
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    return JSONResponse(session_mod.check_rate_limit(sid, ip, model_role))


@app.post("/api/parse-match-situation")
def api_parse_match_situation(payload: ParseMatchPayload) -> JSONResponse:
    try:
        return JSONResponse(agent_mod.parse_match_situation(payload.description))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"parse error: {exc}")


@app.post("/api/explain-match")
def api_explain_match(payload: ExplainMatchPayload) -> JSONResponse:
    try:
        return JSONResponse(agent_mod.explain_match(payload.case_id, payload.situation))
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"explain error: {exc}")


@app.post("/api/import-url")
def api_import_url(payload: ImportUrlPayload) -> JSONResponse:
    if not payload.url.strip():
        raise HTTPException(400, "url required")
    try:
        return JSONResponse(agent_mod.import_from_url(payload.url.strip()))
    except Exception as exc:
        raise HTTPException(500, f"import error: {exc}")


class ImportSavePayload(BaseModel):
    id: str
    draft_md: str
    overwrite: bool = False


@app.post("/api/import-save")
def api_import_save(payload: ImportSavePayload) -> JSONResponse:
    import re
    import frontmatter
    slug = re.sub(r"[^a-z0-9-]+", "-", payload.id.lower().strip()).strip("-")
    if not slug:
        raise HTTPException(400, "invalid id")
    target = ROOT / "content" / "cases" / f"{slug}.md"
    if target.exists() and not payload.overwrite:
        raise HTTPException(409, f"case '{slug}' already exists; use overwrite=true")
    # сначала валидируем фронтматтер через ту же схему, что и тесты
    try:
        post = frontmatter.loads(payload.draft_md)
        from .schemas import CaseFrontmatter
        CaseFrontmatter.model_validate(post.metadata)
    except Exception as exc:
        raise HTTPException(400, f"frontmatter validation failed: {exc}")
    target.write_text(payload.draft_md, encoding="utf-8")
    return JSONResponse({"ok": True, "id": slug, "path": str(target.relative_to(ROOT))})


@app.get("/hypothesis/{h_id}", response_class=HTMLResponse)
def hypothesis_page(request: Request, h_id: str) -> Any:
    h = graph_mod.get_hypothesis(h_id)
    if not h:
        raise HTTPException(404)
    h["status_history"] = json.loads(h.get("status_history_json") or "[]")
    h["markers"] = json.loads(h.get("markers_json") or "[]")
    return templates.TemplateResponse(request, "entity.html", {
        "entity": h, "kind": "hypothesis", "title": h["name"],
    })


@app.get("/type/{t_id}", response_class=HTMLResponse)
def type_page(request: Request, t_id: str) -> Any:
    t = graph_mod.get_type(t_id)
    if not t:
        raise HTTPException(404)
    t["markers"] = json.loads(t.get("markers_json") or "[]")
    return templates.TemplateResponse(request, "entity.html", {
        "entity": t, "kind": "type", "title": t["name"],
    })


@app.get("/tension/{t_id}", response_class=HTMLResponse)
def tension_page(request: Request, t_id: str) -> Any:
    t = graph_mod.get_tension(t_id)
    if not t:
        raise HTTPException(404)
    return templates.TemplateResponse(request, "entity.html", {
        "entity": t, "kind": "tension", "title": t["name"],
    })


@app.get("/mode/{m_id}", response_class=HTMLResponse)
def mode_page(request: Request, m_id: str) -> Any:
    m = graph_mod.get_mode(m_id)
    if not m:
        raise HTTPException(404)
    return templates.TemplateResponse(request, "entity.html", {
        "entity": m, "kind": "mode", "title": m["name"],
    })


@app.get("/counter-signal/{cs_id}", response_class=HTMLResponse)
def counter_signal_page(request: Request, cs_id: str) -> Any:
    cs = graph_mod.get_counter_signal(cs_id)
    if not cs:
        raise HTTPException(404)
    return templates.TemplateResponse(request, "entity.html", {
        "entity": cs, "kind": "counter-signal", "title": cs["name"],
    })


@app.get("/map", response_class=HTMLResponse)
def map_page(request: Request, x: str = "agentivity", y: str = "scale_of_change") -> Any:
    try:
        data = proj_mod.projection(x, y)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    axes = proj_mod.list_axes()
    return templates.TemplateResponse(request, "map.html", {
        "data": data, "axes": axes, "x": x, "y": y,
    })


@app.get("/match", response_class=HTMLResponse)
def match_page(request: Request,
               agentivity: int | None = None,
               ai_pattern: str | None = None,
               orchestration: str | None = None,
               pedagogy_transformation: str | None = None,
               transformation_mode: str | None = None,
               scale_of_change: int | None = None,
               radicalness: int | None = None,
               domain_specificity: int | None = None,
               interaction_form: str | None = None) -> Any:
    query: dict[str, Any] = {}
    for k, v in {
        "agentivity": agentivity, "ai_pattern": ai_pattern,
        "orchestration": orchestration,
        "pedagogy_transformation": pedagogy_transformation,
        "transformation_mode": transformation_mode,
        "scale_of_change": scale_of_change, "radicalness": radicalness,
        "domain_specificity": domain_specificity,
        "interaction_form": interaction_form,
    }.items():
        if v is not None and v != "":
            query[k] = v

    results = match_mod.match_to_cases(query, top_n=15) if query else []
    return templates.TemplateResponse(request, "match.html", {
        "results": results, "query": query,
        "axis_defs": _AXIS_DEFS,
        "transformation_modes": sorted(_TRANSFORM_MODE_IDS),
    })


# ---------------------------------------------------------------------------
# JSON эндпоинты
# ---------------------------------------------------------------------------


@app.get("/api/search")
def api_search(
    q: str | None = None,
    country: str | None = None, pattern: str | None = None,
    orchestration: str | None = None, pedagogy: str | None = None, control: str | None = None,
    org_type: str | None = None, lifecycle_stage: str | None = None,
    transformation_mode: str | None = None,
    agentivity_min: int | None = None, agentivity_max: int | None = None,
    verified_only: bool = False, limit: int = 50,
) -> JSONResponse:
    return JSONResponse(search_mod.search_cases(
        q=q, country=country, pattern=pattern,
        orchestration=orchestration, pedagogy=pedagogy, control=control,
        org_type=org_type, lifecycle_stage=lifecycle_stage,
        transformation_mode=transformation_mode,
        agentivity_min=agentivity_min, agentivity_max=agentivity_max,
        verified_only=verified_only, limit=limit,
    ))


@app.get("/api/case/{case_id}")
def api_case(case_id: str) -> JSONResponse:
    case = search_mod.get_case(case_id)
    if not case:
        raise HTTPException(404)
    return JSONResponse(case)


@app.get("/api/hypothesis/{h_id}")
def api_hypothesis(h_id: str) -> JSONResponse:
    h = graph_mod.get_hypothesis(h_id)
    if not h:
        raise HTTPException(404)
    return JSONResponse(h)


@app.get("/api/projection")
def api_projection(x: str, y: str) -> JSONResponse:
    try:
        return JSONResponse(proj_mod.projection(x, y))
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/match")
def api_match(payload: MatchPayload) -> JSONResponse:
    return JSONResponse(match_mod.match_to_cases(payload.axes, top_n=payload.top_n))


@app.get("/api/axes")
def api_axes() -> JSONResponse:
    return JSONResponse(proj_mod.list_axes())


# ===========================================================================
# Feedback acceptor (global widget)
# ===========================================================================


class FeedbackStartPayload(BaseModel):
    text: str
    page_path: str
    page_context: str = ""


class FeedbackReplyPayload(BaseModel):
    text: str


@app.post("/api/feedback/start")
def api_feedback_start(payload: FeedbackStartPayload, request: Request) -> Any:
    # rate-limit как fast-вызов
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    rl = session_mod.check_rate_limit(sid, ip, "fast")
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан. Введи 🔑 код или поддержи проект.")
    from . import feedback as fb_mod
    role = request.cookies.get(session_mod.ROLE_COOKIE)
    try:
        return JSONResponse(fb_mod.start_thread(
            text=payload.text, session_id=sid, user_role=role,
            page_path=payload.page_path, page_context=payload.page_context,
        ))
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/feedback/{thread_id}/reply")
def api_feedback_reply(thread_id: str, payload: FeedbackReplyPayload, request: Request) -> Any:
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    rl = session_mod.check_rate_limit(sid, ip, "fast")
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан.")
    from . import feedback as fb_mod
    try:
        return JSONResponse(fb_mod.reply(thread_id=thread_id, text=payload.text))
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.get("/service/feedback", response_class=HTMLResponse)
def service_feedback_page(request: Request, status: str = "",
                          category: str = "") -> Any:
    from . import feedback as fb_mod
    threads = fb_mod.list_feedback(status=status or None,
                                    category=category or None)
    stats = fb_mod.stats()
    return templates.TemplateResponse(
        request, "service_feedback.html",
        {"threads": threads, "stats": stats,
         "filter_status": status, "filter_category": category},
    )


@app.get("/service/feedback/{thread_id}", response_class=HTMLResponse)
def service_feedback_thread_page(request: Request, thread_id: str) -> Any:
    from . import feedback as fb_mod
    thread = fb_mod.get_thread(thread_id)
    if not thread:
        raise HTTPException(404, "thread not found")
    return templates.TemplateResponse(
        request, "service_feedback_thread.html", {"thread": thread},
    )


@app.get("/service/feedback/clusters")
def service_feedback_clusters(request: Request) -> Any:
    """Кластеризация фидбэка по тегам."""
    from . import feedback as fb_mod
    clusters = fb_mod.cluster_by_tags(min_size=2)
    return JSONResponse({"clusters": clusters})


@app.post("/api/course/{course_id}/reflection")
def api_course_reflection(course_id: str, request: Request) -> Any:
    """F3-G6: построить методологический протокол курса (deep LLM)."""
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    rl = session_mod.check_rate_limit(sid, ip, "deep")
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит deep исчерпан. Введи код или поддержи.")
    from . import litops as litops_mod
    try:
        result = litops_mod.generate_course_reflection(course_id)
    except Exception as exc:
        raise HTTPException(500, f"reflection failed: {exc}")
    if result.get("status") != "ok":
        raise HTTPException(400, result.get("msg") or "reflection failed")
    return JSONResponse(result)


@app.get("/service/feedback.md")
def service_feedback_export() -> Any:
    from fastapi.responses import Response
    from . import feedback as fb_mod
    md = fb_mod.export_markdown()
    return Response(
        content=md, media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="paideia-feedback.md"'},
    )


# ===========================================================================
# Discuss-агент ∇Kaiyona
# ===========================================================================


class DiscussCreatePayload(BaseModel):
    project_id: str | None = None
    course_id: str | None = None
    config: dict[str, Any] | None = None


class DiscussMsgPayload(BaseModel):
    text: str


class DiscussConfigPayload(BaseModel):
    config: dict[str, Any]


@app.get("/discuss", response_class=HTMLResponse)
def discuss_index(request: Request) -> Any:
    """Landing — последние сессии + кнопка новой."""
    from . import discuss as ds_mod
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    sessions = ds_mod.list_sessions(sid)
    return templates.TemplateResponse(
        request, "discuss_index.html",
        {"sessions": sessions,
         "active_course": request.cookies.get(session_mod.COURSE_COOKIE)},
    )


@app.get("/discuss/new", response_class=HTMLResponse)
def discuss_new(request: Request, project_id: str | None = None,
                course_id: str | None = None) -> Any:
    """Создать новую сессию и редирект в неё."""
    from . import discuss as ds_mod
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    course = course_id or request.cookies.get(session_mod.COURSE_COOKIE)
    # если курс активен — стартуем в режиме co-teach
    initial_config = {"goal": "co_teach" if course else "consult"}
    did = ds_mod.create_session(
        session_id=sid, project_id=project_id, course_id=course,
        config=initial_config,
    )
    return RedirectResponse(url=f"/discuss/{did}", status_code=303)


@app.get("/discuss/{discuss_id}", response_class=HTMLResponse)
def discuss_page(request: Request, discuss_id: str) -> Any:
    from . import discuss as ds_mod
    sess = ds_mod.get_session(discuss_id)
    if not sess:
        raise HTTPException(404, "discuss session not found")
    return templates.TemplateResponse(
        request, "discuss.html",
        {
            "session": sess,
            "goals": ds_mod.list_goals(),
            "qmo_presets": ds_mod.list_qmo_presets(),
            "critique_levels": ds_mod.list_critique_levels(),
            "default_axes": ds_mod.DEFAULT_AXES,
        },
    )


@app.post("/api/discuss/{discuss_id}/message")
def api_discuss_message(discuss_id: str, payload: DiscussMsgPayload,
                        request: Request) -> Any:
    from . import discuss as ds_mod
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    # выясним model_role из конфига сессии для rate-limit
    sess = ds_mod.get_session(discuss_id)
    if not sess:
        raise HTTPException(404, "session not found")
    role = (sess["config"] or {}).get("model_role", "fast")
    rl = session_mod.check_rate_limit(sid, ip, role)
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан. Введи 🔑 код или поддержи.")
    try:
        return JSONResponse(ds_mod.send_message(discuss_id, payload.text))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"discuss error: {exc}")


@app.post("/api/discuss/{discuss_id}/config")
def api_discuss_config(discuss_id: str, payload: DiscussConfigPayload) -> Any:
    from . import discuss as ds_mod
    ds_mod.update_config(discuss_id, payload.config)
    return JSONResponse({"ok": True})


# --- Voice: TTS + STT ---


class TTSPayload(BaseModel):
    text: str
    voice_id: str | None = None


@app.post("/api/voice/tts")
def api_voice_tts(payload: TTSPayload, request: Request) -> Any:
    """Текст → mp3 audio. Требует ELEVENLABS_API_KEY."""
    from . import voice as v
    if not v.tts_configured():
        raise HTTPException(503, "TTS не настроен (ELEVENLABS_API_KEY)")
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    # TTS считаем как fast-вызов (не deep)
    rl = session_mod.check_rate_limit(sid, ip, "fast")
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан.")
    try:
        audio = v.synthesize(payload.text, voice_id=payload.voice_id)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"TTS provider error: {exc}")
    except Exception as exc:
        raise HTTPException(500, f"TTS failed: {exc}")
    from fastapi.responses import Response
    return Response(content=audio, media_type="audio/mpeg")


@app.get("/api/voice/quota")
def api_voice_quota() -> Any:
    from . import voice as v
    try:
        return JSONResponse(v.quota_status())
    except Exception as exc:
        raise HTTPException(500, str(exc))


@app.get("/api/voice/voices")
def api_voice_voices() -> Any:
    from . import voice as v
    try:
        return JSONResponse({"voices": v.list_voices()})
    except Exception as exc:
        raise HTTPException(500, str(exc))


@app.post("/api/voice/transcribe")
async def api_voice_transcribe(request: Request) -> Any:
    """Multipart upload audio → транскрипт через whisper."""
    from . import voice as v
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(400, "file field required")
    language = form.get("language", "ru")
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    rl = session_mod.check_rate_limit(sid, ip, "fast")
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан.")
    data = await file.read()
    if len(data) > 50_000_000:
        raise HTTPException(413, "file too big (50 MB max)")
    try:
        result = v.transcribe(data, filename=file.filename or "audio.mp3",
                              language=language)
    except Exception as exc:
        raise HTTPException(500, f"STT failed: {exc}")
    return JSONResponse(result)


@app.post("/api/course/event/{event_id}/transcribe-upload")
async def api_event_transcribe_upload(request: Request, event_id: str) -> Any:
    """Загрузка аудио на событие → транскрипт → запись в body_md → автозапуск litops."""
    from . import voice as v
    from . import litops as litops_mod
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(400, "file field required")
    language = form.get("language", "ru")
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    rl = session_mod.check_rate_limit(sid, ip, "fast")
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан.")
    data = await file.read()
    if len(data) > 50_000_000:
        raise HTTPException(413, "file too big (50 MB max)")
    try:
        result = v.transcribe(data, filename=file.filename or "lecture.mp3",
                              language=language)
    except Exception as exc:
        raise HTTPException(500, f"STT failed: {exc}")
    transcript = result.get("text", "").strip()
    if not transcript:
        raise HTTPException(500, "empty transcript")
    # Пишем в body_md события (append если уже есть)
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT body_md, course_id FROM course_events WHERE id = ?",
            (event_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "event not found")
        existing = (row["body_md"] or "").strip()
        marker = f"\n\n--- транскрипт ({file.filename}, {len(data)/1e6:.1f} MB) ---\n\n"
        new_body = (existing + marker + transcript) if existing else transcript
        conn.execute(
            "UPDATE course_events SET body_md = ? WHERE id = ?",
            (new_body, event_id),
        )
        conn.commit()
        course_id = row["course_id"]
    finally:
        conn.close()
    # Автозапуск litops
    try:
        litops_mod.extract_from_event(event_id)
    except Exception:
        pass
    return RedirectResponse(
        url=f"/course/{course_id}/event/{event_id}", status_code=303)


@app.post("/api/discuss/{discuss_id}/delete")
def api_discuss_delete(discuss_id: str) -> Any:
    from . import discuss as ds_mod
    ds_mod.delete_session(discuss_id)
    return RedirectResponse(url="/discuss", status_code=303)


@app.get("/library/conflicts", response_class=HTMLResponse)
def library_conflicts_page(request: Request, relation: str = "conflicts") -> Any:
    """Просмотр пар concept × concept с найденным отношением."""
    from . import selector as sel_mod
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """SELECT cc.relation, cc.school_a, cc.school_b, cc.rationale,
                      cc.similarity, cc.created_at,
                      a.id AS a_id, a.name AS a_name, a.definition AS a_def,
                      ba.title AS a_book, ba.authors AS a_authors,
                      b.id AS b_id, b.name AS b_name, b.definition AS b_def,
                      bb.title AS b_book, bb.authors AS b_authors
               FROM concept_conflicts cc
               JOIN library_concepts a ON a.id = cc.concept_a_id
               JOIN library_concepts b ON b.id = cc.concept_b_id
               JOIN library_books ba ON ba.id = a.book_id
               JOIN library_books bb ON bb.id = b.book_id
               WHERE cc.relation = ?
               ORDER BY cc.similarity DESC LIMIT 300""",
            (relation,),
        )
    finally:
        conn.close()
    stats = sel_mod.stats()
    return templates.TemplateResponse(
        request, "library_conflicts.html",
        {"pairs": rows, "stats": stats, "filter_relation": relation},
    )


@app.post("/api/selector/rebuild")
def api_selector_rebuild() -> Any:
    """F1: пересобрать конфликты концептов библиотеки.
    embed → find pairs → LLM classify."""
    from . import selector as sel_mod
    try:
        result = sel_mod.rebuild_concept_conflicts()
    except Exception as exc:
        raise HTTPException(500, f"selector rebuild failed: {exc}")
    return JSONResponse(result)


@app.get("/api/selector/stats")
def api_selector_stats() -> Any:
    from . import selector as sel_mod
    return JSONResponse(sel_mod.stats())


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


# ===========================================================================
# F9 · Onboarding + role assignment
# ===========================================================================

ROLES = [
    {"key": "teacher", "label": "Преподаватель",
     "desc": "Проектирую курс или модуль. Нужно: аналоги, ТРИЗ-приёмы, канвас, экспорт РПД.",
     "icon": "🎓", "default_action": "/project/new/wizard"},
    {"key": "methodologist", "label": "Методолог / исследователь",
     "desc": "Изучаю корпус, гипотезы, противоречия. Нужно: карта, фасеты, диффы волн.",
     "icon": "🔬", "default_action": "/map"},
    {"key": "admin", "label": "Декан / администратор",
     "desc": "Ищу аналоги под программу, обстреливаю замысел стейкхолдерами.",
     "icon": "🏛️", "default_action": "/match"},
    {"key": "student", "label": "Студент / участник курса",
     "desc": "Разбираю материалы, задаю вопросы, нужен доступ только к пройденному.",
     "icon": "🎒", "default_action": "/courses"},
]


@app.get("/onboarding", response_class=HTMLResponse)
def onboarding_page(request: Request) -> Any:
    return templates.TemplateResponse(
        request, "onboarding.html", {"roles": ROLES},
    )


# --- Kairon: публикационная модель проекта/курса ---


@app.get("/kairon/{target_kind}/{target_id}", response_class=HTMLResponse)
def kairon_page(request: Request, target_kind: str, target_id: str) -> Any:
    if target_kind not in ("project", "course"):
        raise HTTPException(404)
    from . import kairon
    latest = kairon.latest(target_kind, target_id)
    history = kairon.list_for_target(target_kind, target_id)
    return templates.TemplateResponse(
        request, "kairon.html",
        {"target_kind": target_kind, "target_id": target_id,
         "latest": latest, "history": history},
    )


@app.post("/api/kairon/{target_kind}/{target_id}/analyze")
def api_kairon_analyze(request: Request, target_kind: str, target_id: str,
                       model_role: str = Form("deep")) -> Any:
    if target_kind not in ("project", "course"):
        raise HTTPException(404)
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    ip = request.client.host if request.client else None
    rl = session_mod.check_rate_limit(sid, ip, model_role)
    if not rl["allowed"]:
        raise HTTPException(429, "Лимит исчерпан.")
    from . import kairon
    try:
        result = kairon.analyze(target_kind, target_id, model_role=model_role)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"kairon failed: {exc}")
    return RedirectResponse(url=f"/kairon/{target_kind}/{target_id}", status_code=303)


# --- Код-логин для тестеров ---


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> Any:
    from . import auth_codes as ac
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    identity = ac.get_identity(sid)
    return templates.TemplateResponse(
        request, "login.html",
        {"identity": identity, "msg": request.query_params.get("msg", "")},
    )


@app.post("/api/login/redeem")
def api_login_redeem(request: Request, code: str = Form(...)) -> Any:
    from . import auth_codes as ac
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    if not sid:
        raise HTTPException(400, "no session")
    result = ac.redeem(code, sid)
    if not result["ok"]:
        return RedirectResponse(url=f"/login?msg={result['msg']}", status_code=303)
    return RedirectResponse(url=f"/login?msg=✓ привет, {result['nickname']}", status_code=303)


@app.get("/service/codes", response_class=HTMLResponse)
def service_codes(request: Request) -> Any:
    """Только владелец (admin/owner) видит коды и создаёт их."""
    from . import auth_codes as ac
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    identity = ac.get_identity(sid)
    if not identity.get("is_owner"):
        return templates.TemplateResponse(
            request, "login.html",
            {"identity": identity, "msg": "Эта страница только для admin/owner",
             "want_owner": True},
        )
    codes = ac.list_codes()
    return templates.TemplateResponse(
        request, "codes.html",
        {"codes": codes, "identity": identity},
    )


@app.post("/api/service/codes/generate")
def api_generate_code(
    request: Request,
    nickname: str = Form(...), role: str = Form("tester"),
    ttl_days: int = Form(90), note: str = Form(""),
) -> Any:
    from . import auth_codes as ac
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    identity = ac.get_identity(sid)
    if not identity.get("is_owner"):
        raise HTTPException(403, "Только owner может выдавать коды")
    code = ac.generate_code(nickname=nickname, role=role,
                             created_by=identity.get("nickname"),
                             ttl_days=ttl_days, note=note)
    return RedirectResponse(url=f"/service/codes?new={code}", status_code=303)


# --- BYOK: свой LLM-ключ ---


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> Any:
    from . import byok
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    key = byok.get_key(sid) if sid else None
    if key:
        # маскируем ключ для UI
        k = key["api_key"]
        key["api_key_masked"] = k[:8] + "..." + k[-4:] if len(k) > 12 else "***"
        key["budget"] = byok.check_personal_budget(sid)
    shared = byok.list_shared()
    return templates.TemplateResponse(
        request, "settings.html",
        {"key": key, "shared_keys": shared},
    )


@app.post("/api/settings/save-key")
def api_settings_save_key(
    request: Request,
    api_key: str = Form(...), base_url: str = Form(""),
    nickname: str = Form(""), daily_limit_usd: float = Form(0),
    shared: str = Form(""), share_daily_usd: float = Form(0),
    fast_model: str = Form(""), deep_model: str = Form(""),
    search_model: str = Form(""),
) -> Any:
    from . import byok
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    if not sid:
        raise HTTPException(400, "no session")
    byok.save_key(
        session_id=sid, api_key=api_key, base_url=base_url,
        nickname=nickname, daily_limit_usd=daily_limit_usd,
        shared=bool(shared), share_daily_usd=share_daily_usd,
        fast_model=fast_model, deep_model=deep_model, search_model=search_model,
    )
    from .llm import invalidate_llm_cache
    invalidate_llm_cache(sid)
    return RedirectResponse(url="/settings?saved=1", status_code=303)


@app.post("/api/settings/delete-key")
def api_settings_delete_key(request: Request) -> Any:
    from . import byok
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    if sid:
        byok.delete_key(sid)
        from .llm import invalidate_llm_cache
        invalidate_llm_cache(sid)
    return RedirectResponse(url="/settings?deleted=1", status_code=303)


@app.get("/quickstart", response_class=HTMLResponse)
def quickstart_page(request: Request) -> Any:
    current_role = request.cookies.get(session_mod.ROLE_COOKIE)
    return templates.TemplateResponse(
        request, "quickstart.html", {"current_role": current_role},
    )


@app.post("/api/onboarding/select-role")
def onboarding_select_role(request: Request, role: str = Form(...)) -> Any:
    if role not in {r["key"] for r in ROLES}:
        raise HTTPException(400, "unknown role")
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    if sid:
        session_mod.set_session_role(sid, role)
    default = next(r["default_action"] for r in ROLES if r["key"] == role)
    resp = RedirectResponse(url=default, status_code=303)
    resp.set_cookie(session_mod.ROLE_COOKIE, role, max_age=60 * 60 * 24 * 365,
                    samesite="lax")
    return resp


# ===========================================================================
# F12 · Support / Donations
# ===========================================================================


from . import payments as payments_mod
from .config import get_settings as _settings_for_payments


@app.get("/support", response_class=HTMLResponse)
def support_page(request: Request) -> Any:
    conn = open_db()
    try:
        total_spent_30d = conn.execute(
            "SELECT COALESCE(SUM(cost_usd),0) FROM llm_runs "
            "WHERE date(created_at) >= date('now','-30 days')"
        ).fetchone()[0] or 0.0
        total_donations = conn.execute(
            "SELECT COALESCE(SUM(amount_usd),0) FROM supporters"
        ).fetchone()[0] or 0.0
        recent_supporters = fetch_all(
            conn,
            "SELECT nickname, amount_rub, amount_usd, channel, created_at "
            "FROM supporters ORDER BY created_at DESC LIMIT 10",
        )
    finally:
        conn.close()
    budget = session_mod.daily_budget_status()
    return templates.TemplateResponse(
        request, "support.html",
        {
            "spent_30d_usd": round(total_spent_30d, 4),
            "donations_total_usd": round(total_donations, 2),
            "recent_supporters": recent_supporters,
            "budget": budget,
            "yk_enabled": payments_mod.yk_configured(),
            "sbp_info": payments_mod.sbp_info(),
            "tinkoff_url": _settings_for_payments().tinkoff_donate_url or "",
        },
    )


# --- F12: ЮKassa endpoints ---


class CreatePaymentPayload(BaseModel):
    amount_rub: float
    nickname: str = ""


@app.post("/api/support/create-payment")
def api_support_create_payment(payload: CreatePaymentPayload, request: Request) -> Any:
    if not payments_mod.yk_configured():
        raise HTTPException(503, "ЮKassa не настроена. Задай YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY в .env.")
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    settings = _settings_for_payments()
    return_url = (settings.yookassa_return_url
                  or f"{request.url.scheme}://{request.url.netloc}/support?paid=1")
    try:
        result = payments_mod.create_payment(
            amount_rub=payload.amount_rub,
            description=f"Поддержка Paideia ({payload.nickname or 'аноним'})",
            return_url=return_url,
            session_id=sid,
            nickname=payload.nickname or None,
        )
    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        raise HTTPException(400, f"create_payment failed: {exc}")
    return JSONResponse(result)


@app.post("/api/webhook/yookassa")
async def api_webhook_yookassa(request: Request) -> Any:
    """Webhook от ЮKassa. Проверка по IP + по структуре события."""
    # IP check
    client_ip = request.client.host if request.client else ""
    if request.headers.get("x-forwarded-for"):
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    if not payments_mod.ip_is_trusted(client_ip):
        # Логируем но не падаем (на dev может быть тестовый трафик)
        import logging
        logging.warning("yookassa webhook from untrusted IP: %s", client_ip)
        # В проде — отвергаем
        if request.url.hostname and "mindkampf" in request.url.hostname:
            raise HTTPException(403, "untrusted IP")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(400, "invalid JSON")

    parsed = payments_mod.parse_webhook_event(payload)
    if not parsed:
        # Не payment.succeeded — просто 200 OK (ЮKassa ретраит на не-2xx)
        return {"ok": True, "ignored": True}

    conn = open_db()
    try:
        # Идемпотентность: payment_id уникален
        existed = conn.execute(
            "SELECT id FROM supporters WHERE note LIKE ?",
            (f"%payment_id={parsed['payment_id']}%",),
        ).fetchone()
        if existed:
            return {"ok": True, "duplicate": True}

        conn.execute(
            "INSERT INTO supporters (session_id, nickname, amount_rub, amount_usd, channel, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (parsed["session_id"], parsed["nickname"], parsed["amount_rub"],
             round(parsed["amount_rub"] / 95.0, 2),  # грубая конверсия для UI
             "yookassa", f"payment_id={parsed['payment_id']}"),
        )
        conn.commit()
    finally:
        conn.close()

    if parsed["session_id"]:
        session_mod.mark_supporter(parsed["session_id"])
    return {"ok": True}


@app.post("/api/support/redeem-code")
def api_support_redeem_code(request: Request, code: str = Form(...)) -> Any:
    """F11: код от автора → supporter без оплаты."""
    if not session_mod.check_bypass_code(code):
        raise HTTPException(400, "Код не подошёл. Проверь написание или попроси новый.")
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    if sid:
        session_mod.mark_supporter(sid)
        conn = open_db()
        try:
            conn.execute(
                "INSERT INTO supporters (session_id, nickname, channel, note) "
                "VALUES (?, ?, ?, ?)",
                (sid, "тестер по коду", "code", f"code={code[:20]}"),
            )
            conn.commit()
        finally:
            conn.close()
    return RedirectResponse(url="/support?redeemed=1", status_code=303)


@app.get("/api/support/sbp")
def api_support_sbp() -> Any:
    info = payments_mod.sbp_info()
    if not info:
        raise HTTPException(404, "СБП не настроен")
    return JSONResponse(info)


@app.post("/api/support/record")
def api_support_record(
    request: Request,
    nickname: str = Form(""), amount_rub: float = Form(0),
    amount_usd: float = Form(0), channel: str = Form("manual"),
    note: str = Form(""),
) -> Any:
    """Ручная запись доната (нет webhook от платёжных систем)."""
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    conn = open_db()
    try:
        conn.execute(
            "INSERT INTO supporters (session_id, nickname, amount_rub, amount_usd, channel, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (sid, nickname or None, amount_rub or None, amount_usd or None,
             channel, note or None),
        )
        conn.commit()
    finally:
        conn.close()
    if sid:
        session_mod.mark_supporter(sid)
    return RedirectResponse(url="/support", status_code=303)


# ===========================================================================
# F3 · Course scaffold
# ===========================================================================


@app.get("/courses", response_class=HTMLResponse)
def courses_page(request: Request) -> Any:
    conn = open_db()
    try:
        courses = fetch_all(
            conn,
            """SELECT c.id, c.name, c.description, c.period_start, c.period_end,
                      c.authors, c.updated_at,
                      (SELECT COUNT(*) FROM course_events WHERE course_id=c.id) AS events_count
               FROM courses c ORDER BY c.updated_at DESC""",
        )
    finally:
        conn.close()
    active = request.cookies.get(session_mod.COURSE_COOKIE)
    return templates.TemplateResponse(
        request, "courses.html",
        {"courses": courses, "active_course": active},
    )


@app.get("/course/new", response_class=HTMLResponse)
def course_new_page(request: Request) -> Any:
    return templates.TemplateResponse(request, "course_new.html", {})


@app.post("/api/course/create")
def api_course_create(
    request: Request,
    name: str = Form(...), description: str = Form(""),
    period_start: str = Form(""), period_end: str = Form(""),
    authors: str = Form(""), target_audience: str = Form(""),
) -> Any:
    import secrets
    cid = "crs-" + secrets.token_urlsafe(8)
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO courses
               (id, name, description, period_start, period_end, authors, target_audience)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cid, name, description, period_start or None, period_end or None,
             authors or None, target_audience or None),
        )
        # автоматический binding автора
        sid = request.cookies.get(session_mod.COOKIE_NAME)
        if sid:
            conn.execute(
                "INSERT OR IGNORE INTO course_role_bindings (course_id, session_id, role) "
                "VALUES (?, ?, 'author')",
                (cid, sid),
            )
        conn.commit()
    finally:
        conn.close()
    resp = RedirectResponse(url=f"/course/{cid}", status_code=303)
    resp.set_cookie(session_mod.COURSE_COOKIE, cid, max_age=60 * 60 * 24 * 365,
                    samesite="lax")
    return resp


@app.get("/course/{course_id}", response_class=HTMLResponse)
def course_page(request: Request, course_id: str) -> Any:
    conn = open_db()
    try:
        c = conn.execute(
            "SELECT * FROM courses WHERE id = ?", (course_id,)
        ).fetchone()
        if not c:
            raise HTTPException(404, f"course '{course_id}' not found")
        course = dict(c)
        events = fetch_all(
            conn,
            "SELECT id, kind, title, happened_at, duration_min, body_md "
            "FROM course_events WHERE course_id = ? ORDER BY happened_at DESC, created_at DESC",
            (course_id,),
        )
        # G3: подгрузить litops-extracts для всех событий за один проход
        extracts_by_event: dict[str, list[dict]] = {}
        if events:
            ids = [e["id"] for e in events]
            placeholders = ",".join("?" * len(ids))
            rows = fetch_all(
                conn,
                f"""SELECT id, event_id, kind, content, speaker, quote, confidence
                    FROM litops_extracts WHERE event_id IN ({placeholders})
                    ORDER BY confidence DESC, id""",
                ids,
            )
            for r in rows:
                extracts_by_event.setdefault(r["event_id"], []).append(r)
        for e in events:
            e["litops"] = extracts_by_event.get(e["id"], [])
        my_roles = []
        sid = request.cookies.get(session_mod.COOKIE_NAME)
        if sid:
            my_roles = [r["role"] for r in fetch_all(
                conn,
                "SELECT role FROM course_role_bindings WHERE course_id=? AND session_id=?",
                (course_id, sid),
            )]
    finally:
        conn.close()
    return templates.TemplateResponse(
        request, "course.html",
        {"course": course, "events": events, "my_roles": my_roles},
    )


EVENT_KINDS = [
    ("lecture", "🎤 Лекция"),
    ("seminar", "💬 Семинар"),
    ("homework_release", "📝 Выдача д/з"),
    ("homework_submission", "📥 Сдача д/з"),
    ("chat_burst", "💭 Чат-обсуждение"),
    ("reading", "📖 Чтение"),
    ("exam", "🎯 Экзамен/контроль"),
    ("reflection", "🪞 Рефлексия"),
]


# --- Event detail page + artifact packs ---


@app.get("/course/{course_id}/event/{event_id}", response_class=HTMLResponse)
def course_event_page(request: Request, course_id: str, event_id: str) -> Any:
    from . import course_packs as cp
    conn = open_db()
    try:
        course = fetch_one(conn, "SELECT * FROM courses WHERE id = ?", (course_id,))
        event = fetch_one(conn, "SELECT * FROM course_events WHERE id = ?", (event_id,))
        if not course or not event:
            raise HTTPException(404, "course or event not found")
        # моя роль в этом курсе
        sid = request.cookies.get(session_mod.COOKIE_NAME)
        my_role = None
        if sid:
            row = conn.execute(
                "SELECT role FROM course_role_bindings WHERE course_id=? AND session_id=?",
                (course_id, sid),
            ).fetchone()
            my_role = row[0] if row else None
        # все события для навигации
        all_events = fetch_all(
            conn,
            "SELECT id, kind, title, happened_at FROM course_events "
            "WHERE course_id = ? ORDER BY happened_at",
            (course_id,),
        )
        # litops
        litops = fetch_all(
            conn,
            "SELECT kind, content, speaker, quote, confidence FROM litops_extracts "
            "WHERE event_id = ? ORDER BY confidence DESC",
            (event_id,),
        )
    finally:
        conn.close()
    artifacts = cp.visible_artifacts_for_role(event_id, role=my_role, session_id=sid)
    chat_msgs = cp.list_chat_messages(event_id)
    by_pkg = {"author": [], "student": [], "course_meta": []}
    for a in artifacts:
        by_pkg.setdefault(a["package"], []).append(a)
    # цепочки homework
    homework_threads = []
    for a in by_pkg["author"]:
        if a["kind"] == "homework_brief":
            homework_threads.append(cp.get_homework_thread(a["id"]))
    return templates.TemplateResponse(
        request, "course_event.html",
        {"course": dict(course), "event": dict(event),
         "by_pkg": by_pkg, "litops": litops,
         "chat_msgs": chat_msgs, "all_events": all_events,
         "my_role": my_role, "homework_threads": homework_threads,
         "kind_options": list(cp.VALID_KINDS)},
    )


@app.post("/api/course/event/{event_id}/artifact")
def api_event_add_artifact(
    request: Request, event_id: str,
    package: str = Form(...), kind: str = Form(...),
    title: str = Form(""), body_md: str = Form(""),
    author_nickname: str = Form(""),
    in_response_to: str = Form(""),
) -> Any:
    from . import course_packs as cp
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    try:
        cp.add_artifact(event_id=event_id, package=package, kind=kind,
                        title=title, body_md=body_md,
                        author_nickname=author_nickname,
                        author_session_id=sid,
                        in_response_to=in_response_to or None)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    conn = open_db()
    try:
        row = conn.execute("SELECT course_id FROM course_events WHERE id=?", (event_id,)).fetchone()
    finally:
        conn.close()
    return RedirectResponse(url=f"/course/{row['course_id']}/event/{event_id}",
                             status_code=303)


@app.post("/api/course/event/artifact/{artifact_id}/delete")
def api_artifact_delete(artifact_id: str, request: Request) -> Any:
    # destructive: только owner может удалять
    from . import auth_codes as ac
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    identity = ac.get_identity(sid)
    if not identity.get("is_owner"):
        raise HTTPException(403, "Только owner может удалять артефакты. Войди по коду owner-роли.")
    from . import course_packs as cp
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT e.course_id, a.event_id FROM course_event_artifacts a "
            "JOIN course_events e ON e.id = a.event_id WHERE a.id = ?",
            (artifact_id,),
        ).fetchone()
    finally:
        conn.close()
    cp.delete_artifact(artifact_id)
    if row:
        return RedirectResponse(
            url=f"/course/{row['course_id']}/event/{row['event_id']}",
            status_code=303)
    return RedirectResponse(url="/courses", status_code=303)


@app.post("/api/course/event/{event_id}/chat-messages")
def api_event_chat_messages(event_id: str,
                             payload: dict[str, Any] = Body(...)) -> Any:
    """Принимает {messages: [{speaker, content, role_at_time?, sent_at?}, ...]}"""
    from . import course_packs as cp
    msgs = payload.get("messages") or []
    if not isinstance(msgs, list):
        raise HTTPException(400, "messages must be a list")
    n = cp.add_chat_messages(event_id, msgs)
    return JSONResponse({"added": n})


@app.get("/course/{course_id}/dynamics")
def course_dynamics(request: Request, course_id: str,
                    project_id: str | None = None) -> Any:
    from . import course_packs as cp
    if not project_id:
        return JSONResponse({"error": "project_id required"})
    timeline = cp.project_dynamics_across_course(course_id, project_id)
    return JSONResponse(timeline)


@app.get("/course/{course_id}/dynamics-view", response_class=HTMLResponse)
def course_dynamics_view(request: Request, course_id: str,
                         project_id: str) -> Any:
    """HTML-таймлайн «событие курса × состояние проекта по git-истории»."""
    from . import course_packs as cp
    timeline = cp.project_dynamics_across_course(course_id, project_id)
    conn = open_db()
    try:
        course = fetch_one(conn, "SELECT * FROM courses WHERE id = ?", (course_id,))
    finally:
        conn.close()
    proj_path = ROOT / "content" / "projects" / f"{project_id}.md"
    return templates.TemplateResponse(
        request, "course_dynamics.html",
        {"course": dict(course) if course else {"id": course_id, "name": course_id},
         "project_id": project_id, "timeline": timeline,
         "has_git": proj_path.exists()},
    )


@app.get("/course/{course_id}/members", response_class=HTMLResponse)
def course_members_page(request: Request, course_id: str) -> Any:
    """Список участников курса с их сданными работами."""
    conn = open_db()
    try:
        course = fetch_one(conn, "SELECT * FROM courses WHERE id = ?", (course_id,))
        if not course:
            raise HTTPException(404, "course not found")
        # все role-binding'и
        bindings = fetch_all(
            conn,
            """SELECT session_id, role, created_at FROM course_role_bindings
               WHERE course_id = ? ORDER BY role, created_at""",
            (course_id,),
        )
        # все student-артефакты курса
        student_arts = fetch_all(
            conn,
            """SELECT a.id, a.kind, a.title, a.body_md, a.author_nickname,
                      a.author_session_id, a.in_response_to, a.created_at,
                      a.event_id, e.title AS event_title, e.kind AS event_kind,
                      e.happened_at
               FROM course_event_artifacts a
               JOIN course_events e ON e.id = a.event_id
               WHERE e.course_id = ? AND a.package = 'student'
               ORDER BY a.author_nickname, e.happened_at""",
            (course_id,),
        )
    finally:
        conn.close()
    # группируем по nickname
    by_nick: dict[str, list[dict]] = {}
    for a in student_arts:
        key = a.get("author_nickname") or "(аноним)"
        by_nick.setdefault(key, []).append(a)
    return templates.TemplateResponse(
        request, "course_members.html",
        {"course": dict(course), "bindings": bindings,
         "by_nick": by_nick,
         "total_artifacts": len(student_arts)},
    )


# --- Корпус-конвейер ---


@app.get("/service/corpus-candidates", response_class=HTMLResponse)
def service_corpus_candidates(request: Request, status: str = "pending",
                               kind: str | None = None) -> Any:
    from . import corpus_conveyor as cc
    return templates.TemplateResponse(
        request, "corpus_candidates.html",
        {"candidates": cc.list_candidates(status=status, kind=kind),
         "stats": cc.stats(),
         "filter_status": status, "filter_kind": kind or ""},
    )


@app.post("/api/corpus-candidates/{cid}/decide")
def api_candidate_decide(cid: str, request: Request,
                          decision: str = Form(...)) -> Any:
    from . import corpus_conveyor as cc
    sid = request.cookies.get(session_mod.COOKIE_NAME)
    try:
        cc.decide(cid, decision, decided_by=sid)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return RedirectResponse(url="/service/corpus-candidates", status_code=303)


@app.post("/api/course/event/{event_id}/harvest")
def api_event_harvest(event_id: str) -> Any:
    """Извлечь кандидатов в корпус из событий курса."""
    from . import corpus_conveyor as cc
    conn = open_db()
    try:
        row = conn.execute("SELECT course_id FROM course_events WHERE id = ?",
                            (event_id,)).fetchone()
    finally:
        conn.close()
    try:
        result = cc.harvest_from_event(event_id)
    except Exception as exc:
        raise HTTPException(500, f"harvest failed: {exc}")
    if not row:
        return JSONResponse(result)
    return RedirectResponse(
        url=f"/course/{row['course_id']}/event/{event_id}", status_code=303)


@app.post("/api/course/event/{event_id}/extract-litops")
def api_event_extract_litops(event_id: str) -> Any:
    """G3: запустить litops digestor по событию."""
    from . import litops as litops_mod
    try:
        result = litops_mod.extract_from_event(event_id)
    except Exception as exc:
        raise HTTPException(500, f"litops failed: {exc}")
    if result.get("status") != "ok":
        raise HTTPException(400, result.get("msg") or "extract failed")
    # узнаем course_id для редиректа
    conn = open_db()
    try:
        row = conn.execute("SELECT course_id FROM course_events WHERE id = ?",
                           (event_id,)).fetchone()
    finally:
        conn.close()
    if row:
        return RedirectResponse(url=f"/course/{row['course_id']}#event-{event_id}", status_code=303)
    return JSONResponse(result)


@app.post("/api/course/{course_id}/event")
def api_course_add_event(
    course_id: str,
    kind: str = Form(...), title: str = Form(""),
    happened_at: str = Form(""), duration_min: int = Form(0),
    body_md: str = Form(""),
) -> Any:
    if kind not in {k for k, _ in EVENT_KINDS}:
        raise HTTPException(400, f"unknown kind '{kind}'")
    import secrets
    eid = "evt-" + secrets.token_urlsafe(8)
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO course_events
               (id, course_id, kind, title, happened_at, duration_min, body_md)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (eid, course_id, kind, title or None,
             happened_at or None, duration_min or None, body_md or None),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(url=f"/course/{course_id}", status_code=303)


@app.post("/api/course/{course_id}/activate")
def api_course_activate(course_id: str) -> Any:
    resp = RedirectResponse(url=f"/course/{course_id}", status_code=303)
    resp.set_cookie(session_mod.COURSE_COOKIE, course_id, max_age=60 * 60 * 24 * 365,
                    samesite="lax")
    return resp


@app.post("/api/course/deactivate")
def api_course_deactivate() -> Any:
    resp = RedirectResponse(url="/courses", status_code=303)
    resp.delete_cookie(session_mod.COURSE_COOKIE)
    return resp
