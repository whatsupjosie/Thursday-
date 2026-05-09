# PubCast Nervous System Full Install Overlay

This overlay is built from the verified nervous-system package and the uploaded `main.py.bak` / `static__control.html.bak` files.

## What is included

- `modules/*.py` nervous-system, behavior, mocap, animation, and GLB retargeting modules
- `static/*.js` browser runtime, behavior pipeline, GLB motion consumer, and debug probe
- `main.py.patched` — uploaded `main.py.bak` with nervous-system routes installed during startup and `/api/motion/frame` routed through the authority
- `static__control.html.patched` — uploaded control template with the required motion-runtime scripts included
- `tests/` — verified tests from the bundle

## Install steps

From a clean backup of your PubCast workspace:

1. Copy `modules/*` into your workspace `modules/` folder.
2. Copy `static/*` into your workspace `static/` folder.
3. Replace your current `main.py` with `main.py.patched` only after backing up the old file.
4. Replace your current `static/control.html` with `static__control.html.patched` only after backing up the old file.
5. Start the server:

```bash
python -m compileall modules
uvicorn main:app --reload --port 8000
```

6. Check routes:

```bash
curl http://localhost:8000/api/nervous-system/status
curl http://localhost:8000/api/avatar-motion/status
```

7. Send a test frame:

```bash
curl -X POST http://localhost:8000/api/avatar-motion/frame ^
  -H "Content-Type: application/json" ^
  -d "{\"avatar_id\":\"manny\",\"emotion\":\"curious\",\"intent\":\"listening\",\"force\":true}"
```

## Live proof target

The next debugging pass should prove this chain:

`/api/avatar-motion/frame` -> nervous-system authority -> websocket `avatar_motion_commands` -> browser GLB consumer -> Manny/Sheila bone movement.
