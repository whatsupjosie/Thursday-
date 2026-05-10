# PubCast Avatar Asset Policy

## Hard rule

Sprites are banned until the project owner explicitly says otherwise.

Manny and Sheila are GLB avatars driven through an authoritative skeleton. Runtime fallback may freeze, idle, or simplify GLB skeletal motion. Runtime fallback must not replace the avatar with:

- 2D sprite avatars
- spritesheets
- canvas puppet avatars
- billboard impostor avatars
- image-based Manny/Sheila stand-ins

## Allowed fallback behavior

Allowed:

```text
GLB skeleton → safe freeze
GLB skeleton → idle breathing
GLB skeleton → reduced bone subset
GLB skeleton → lower update frequency
GLB skeleton → hidden/not loaded with explicit error
```

Not allowed:

```text
GLB missing → draw Manny as a sprite
GLB expensive → replace Sheila with canvas image puppet
Renderer slow → use billboard avatar impostor
Asset missing → silently generate replacement avatar art
```

## Why

PubCast avatar identity depends on Manny/Sheila remaining real GLB-backed characters with a shared skeleton contract. Sprite fallback creates false proof and hides broken avatar loading instead of fixing it.

## Implementation hooks

- `modules/avatar_motion_spine.py` exposes `SPRITES_BANNED = True`.
- `AvatarAnimationLibrary.add(...)` rejects animation definitions that advertise forbidden sprite-style avatar fallback.
- `AvatarRuntimeDoctor.run()` reports `no_forbidden_sprite_fallbacks`.
- Runtime pose packets include `metadata.sprites_banned`.

The only acceptable way to change this rule is an explicit future project decision from the owner.
