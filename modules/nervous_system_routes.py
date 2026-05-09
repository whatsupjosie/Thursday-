"""
FastAPI route installer for the PubCast Nervous System Authority.

Usage in main.py, after `app`, `hub`, and `DATA_DIR` exist:

    from modules.nervous_system_routes import install_nervous_system_routes
    nervous_system = install_nervous_system_routes(app, hub, DATA_DIR)

This keeps the integration reversible and avoids rewriting the main app.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi.responses import JSONResponse

try:
    from modules.nervous_system_authority import NervousSystemAuthority
except Exception:  # pragma: no cover
    from nervous_system_authority import NervousSystemAuthority


def install_nervous_system_routes(app: Any, hub: Any, data_dir: Path | str, *, default_room: str = "studio") -> NervousSystemAuthority:
    authority = NervousSystemAuthority(str(data_dir), default_room=default_room)

    async def _broadcast(event: Dict[str, Any]) -> None:
        if hub is None:
            return
        try:
            await hub.broadcast_system_event(event)
        except TypeError:
            try:
                await hub.broadcast(event)
            except Exception:
                pass
        except Exception:
            pass

    @app.get("/api/nervous-system/status")
    async def nervous_status():
        return authority.status()

    @app.get("/api/avatar-motion/status")
    async def avatar_motion_status():
        return authority.status()

    @app.post("/api/nervous-system/frame")
    async def nervous_frame(payload: Dict[str, Any]):
        try:
            event = authority.ingest(payload or {})
            await _broadcast(event)
            return {"ok": True, "event": event, "payload": event.get("payload", {})}
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    @app.post("/api/avatar-motion/frame")
    async def avatar_motion_frame(payload: Dict[str, Any]):
        return await nervous_frame(payload)

    @app.post("/api/avatar-motion/tick")
    async def avatar_motion_tick(payload: Dict[str, Any]):
        return await nervous_frame(payload)

    @app.post("/api/nervous-system/{avatar_id}/emotion")
    async def nervous_emotion(avatar_id: str, payload: Dict[str, Any]):
        try:
            event = authority.push_emotion(
                avatar_id,
                str((payload or {}).get("emotion") or (payload or {}).get("label") or "neutral"),
                float((payload or {}).get("intensity", 0.6)),
                room=(payload or {}).get("room"),
            )
            await _broadcast(event)
            return {"ok": True, "event": event, "payload": event.get("payload", {})}
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    @app.post("/api/avatar-motion/{avatar_id}/emotion")
    async def avatar_motion_emotion(avatar_id: str, payload: Dict[str, Any]):
        return await nervous_emotion(avatar_id, payload)

    @app.put("/api/avatar-motion/profiles/{avatar_id}")
    async def avatar_motion_profile(avatar_id: str, payload: Dict[str, Any]):
        try:
            result = authority.behavior.update_profile(avatar_id, payload or {})
            authority.ensure_performer(avatar_id, room=(payload or {}).get("room"))
            return {"ok": True, "profile": result}
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    return authority
