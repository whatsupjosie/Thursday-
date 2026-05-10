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
- `modules/avatar_motion_bridge.py`
  - wraps `PosePacket` output into a transport-safe `pubcast.avatar.motion.v1` event
  - provides `build_ws_payload(...)` for WebSocket or local bridge routes
- `static/pubcast_animation_presets.js`
  - browser-side animation preset metadata derived from the uploaded `animation_presets.js`
- `static/avatar_motion_bridge_consumer.js`
  - receives motion events and applies bone transforms to an existing GLB/skeleton adapter
  - does not create sprites, canvases, or replacement avatars
- `static/package.json`
  - marks static runtime bridge files as ES modules for Node smoke tests
- `tests/test_avatar_motion_spine.py`
  - verifies behavior fallback, mocap priority, safety priority, pose serialization, and seed-repo doctor behavior
- `tests/test_avatar_motion_bridge.py`
  - verifies the Python event bridge emits the protocol envelope and serializes mocap bone transforms
- `tests/test_avatar_motion_bridge_consumer_node.mjs`
  - verifies the browser consumer applies pose bones to a mock GLB skeleton adapter
- `reviewed_input/UPLOADED_ANIMATION_INPUTS.md`
  - manifest of the user-provided materials and how they were used

## Priority model

The router follows this authority order:

```text
safety/system > mocap > scripted direction > behavior/emotion > idle fallback
```

This is deliberate. The avatar should not care whether motion came from webcam mocap, a scripted scene, emotional behavior selection, or a safety fallback. The renderer receives one clean pose packet.

## Wired runtime path

```text
mocap / emotional cue / behavior command
→ AvatarMotionRouter.route(...)
→ PosePacket.to_dict()
→ AvatarMotionBridge.build_motion_event(...)
→ pubcast.avatar.motion.v1 JSON event
→ PubCastAvatarMotionConsumer.consume(...)
→ existing GLB skeleton adapter bones update
→ Manny/Sheila visible movement once connected to the app renderer
```

## Current proof

The Python spine and bridge are dependency-light and can be checked without a running renderer:

```bash
python -m compileall modules tests
python -m pytest tests -v
```

The JavaScript runtime files can be syntax-checked with Node:

```bash
node --check static/pubcast_animation_presets.js
node --check static/avatar_motion_bridge_consumer.js
node tests/test_avatar_motion_bridge_consumer_node.mjs
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

Attach the consumer to the actual stage/GLB loader. The consumer expects a skeleton adapter with one of these shapes:

```js
{
  getBone(name) { ... },
  updateMatrixWorld(force) { ... }
}
```

or:

```js
{
  getObjectByName(name) { ... },
  updateMatrixWorld(force) { ... }
}
```

or:

```js
{
  bones: { head, chest, thigh_l, thigh_r },
  updateMatrixWorld(force) { ... }
}
```

That keeps the bridge independent from Three.js, Babylon, Unity export glue, or a custom GLB wrapper.
