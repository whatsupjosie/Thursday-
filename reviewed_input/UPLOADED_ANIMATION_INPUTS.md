# Uploaded Animation Inputs Reviewed

## Used directly as design/input

- `pubcast_animation_hardened.zip`
  - contained Python avatar/mocap/hub/choreography modules, Rust animation/backend files, and tests
  - Python files were syntax-compiled successfully in the sandbox
  - Rust files could not be `cargo check`ed here because the sandbox does not have Cargo/Rust installed
- `animation_presets.js`
  - contained walk/sit/wave/type/idle skeletal tracks
  - distilled into `static/pubcast_animation_presets.js`
- `enhanced_animation_system.py.pdf`
  - contained useful concepts: glow settings, energy patterns, animation types, dialogue clips, ethereal avatar presets
  - treated as reference only because PDF extraction introduces broken Python formatting
- `avatar loook hoplogram.zip`
  - contained hologram avatar specs, shader, generator, and contact glow reference files
  - treated as future visual/rendering reference, not runtime spine code

## Not used as PubCast runtime input

- `Animation.js`
  - identified as Svelte compiler AST code for the `animate:` directive, not PubCast avatar runtime logic
- `Assembling the complete program from uploaded files`
  - contained only a Claude share URL

## Integration policy

This pass avoids replacing Manny/Sheila with sprites or new generated assets. It adds a motion authority layer that can drive existing GLB avatars once connected to the renderer.
