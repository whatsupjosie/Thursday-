# PubCast Nervous System Hardened

Seed repo for the PubCast avatar nervous-system / motion-authority layer.

This repository contains the source files from `pubcast_nervous_system_hardened_implemented.zip`, cleaned for GitHub import:

- `modules/` — Python runtime authority, behavior engine, mocap/motion pipeline, GLB retargeter, and routes
- `static/` — browser-side animation presets, behavior pipeline, GLB motion consumer, and debug probe
- `tests/` — Python and Node smoke tests
- `docs/` — integration and handoff notes
- `patches/` — patch notes for integrating into an existing PubCast app
- `reviewed_input/` — source files inspected from the uploaded hardened bundle

Generated/temporary files such as `__pycache__`, `.pytest_cache`, and compiled artifacts were intentionally excluded.

## Immediate test commands

```bash
python -m compileall modules tests
python -m pytest tests -v
node --check static/avatar_glb_motion_consumer.js
node tests/test_avatar_glb_motion_consumer_node.js
```

## Integration target

The intended next milestone is visible runtime proof:

> mocap / emotional cue / behavior command → nervous-system authority → GLB motion consumer → Manny or Sheila visibly moves.
