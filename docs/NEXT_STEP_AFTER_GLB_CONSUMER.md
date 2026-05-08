# Next Step After This Bundle

1. Include `/static/avatar_glb_motion_consumer.js` after `/static/avatar_motion_runtime.js`.
2. In the existing Manny/Sheila GLB loader, call `PubcastGLBMotionConsumer.registerAvatar()` after each GLB scene loads.
3. Start PubCast and hit `/api/avatar-motion/tick` or use the browser console smoke test from the handoff.
4. If bones do not move, inspect `debugStatus().mappedBones` and add custom aliases for the exact rig names.
5. Once visible movement works, replace semantic fallback bone accents with real clip playback while keeping the command contract.
