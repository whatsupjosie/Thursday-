# PubCast Avatar Motion Spine — Upload Integration Pass

This branch integrates the uploaded animation work into a small canonical runtime spine instead of dumping every experimental file into the root.

## What landed

- `modules/avatar_motion_spine.py`
  - animation library
  - animation selector
  - motion source router
  - renderer-safe pose packet contract
  - avatar runtime doctor/preflight
  - safety freeze and mocap intent helpers
- `static/pubcast_animation_presets.js`
  - browser-side animation preset metadata derived from the uploaded `animation_presets.js`
- `tests/test_avatar_motion_spine.py`
  - verifies behavior fallback, mocap priority, safety priority, pose serialization, and seed-repo doctor behavior
- `reviewed_input/UPLOADED_ANIMATION_INPUTS.md`
  - manifest of the user-provided materials and how they were used

## Priority model

The router follows this authority order:

```text
safety/system > mocap > scripted direction > behavior/emotion > idle fallback
```

This is deliberate. The avatar should not care whether motion came from webcam mocap, a scripted scene, emotional behavior selection, or a safety fallback. The renderer receives one clean pose packet.

## Current proof

The Python spine is dependency-light and can be checked without a running renderer:

```bash
python -m compileall modules tests
python -m pytest tests -v
```

The JavaScript preset file can be syntax-checked with Node:

```bash
node --check static/pubcast_animation_presets.js
```

## Not integrated yet

The uploaded hardened Rust bundle should be preserved as the next deeper backend layer, but it is larger and should be merged with a Rust toolchain available:

```bash
cd rust_src
cargo check
cargo test
```

The PDF-based enhanced animation system contains useful appearance/glow/dialogue ideas, but it should not be pasted in as code until converted from PDF text back into valid Python.

## Next step

Wire the pose packet into the existing GLB consumer:

```text
mocap / emotional cue / behavior command
→ AvatarMotionRouter.route(...)
→ PosePacket.to_dict()
→ WebSocket or local bridge
→ GLB motion consumer
→ Manny/Sheila visible movement
```
