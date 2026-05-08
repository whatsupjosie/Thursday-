#!/usr/bin/env python3
"""Install PubCast nervous-system files into a real workspace, safely.

Run from the root of your PubCast project:
    python install_nervous_system.py

It backs up touched files, copies modules/static assets, and applies a tiny
main.py hook if it can find the expected lines. It refuses to overwrite without
creating timestamped .bak files.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import time

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
STAMP = time.strftime('%Y%m%d_%H%M%S')

MODULES = [
    'animation_presets_complete.py', 'animation_presets_expanded.py',
    'behavior_animation_engine.py', 'behavior_motion_pipeline.py',
    'avatar_behavior_runtime.py', 'glb_motion_retargeter.py',
    'nervous_system_authority.py', 'nervous_system_routes.py',
]
STATIC = [
    'animation_presets_complete.js', 'animation_presets_expanded.js',
    'behavior_animation_engine.js', 'behavior_motion_pipeline.js',
    'avatar_motion_runtime.js', 'avatar_motion_debug_probe.js',
    'avatar_glb_motion_consumer.js',
]

def backup(path: Path) -> None:
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + f'.bak_{STAMP}'))


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    backup(dst)
    shutil.copy2(src, dst)
    print(f'✓ {dst.relative_to(ROOT)}')

for name in MODULES:
    copy_file(HERE / 'modules' / name, ROOT / 'modules' / name)
for name in STATIC:
    copy_file(HERE / 'static' / name, ROOT / 'static' / name)

main = ROOT / 'main.py'
if main.exists():
    txt = main.read_text(encoding='utf-8')
    changed = False
    if 'install_nervous_system_routes' not in txt:
        marker = 'from modules.avatar'
        lines = txt.splitlines()
        insert_at = None
        for i, line in enumerate(lines):
            if line.startswith(marker):
                insert_at = i + 1
        if insert_at is not None:
            lines.insert(insert_at, 'from modules.nervous_system_routes import install_nervous_system_routes')
            txt = '\n'.join(lines) + '\n'
            changed = True
        hook = 'nervous_system = install_nervous_system_routes(app, hub, DATA_DIR, default_room="studio")'
        if hook not in txt:
            target = 'recording: RecordingService = create_recording_service(DATA_DIR / "media", cameras)'
            if target in txt:
                txt = txt.replace(target, target + '\n' + hook)
                changed = True
            else:
                print('⚠ Could not find recording singleton line; add this manually after app/hub/DATA_DIR exist:')
                print('  from modules.nervous_system_routes import install_nervous_system_routes')
                print('  nervous_system = install_nervous_system_routes(app, hub, DATA_DIR, default_room="studio")')
    if changed:
        backup(main)
        main.write_text(txt, encoding='utf-8')
        print('✓ patched main.py')
    else:
        print('· main.py already has nervous-system hook, or needs manual hook')
else:
    print('⚠ main.py not found; copied files only')

print('\nDone. Smoke test:')
print('  python -m compileall modules')
print('  uvicorn main:app --reload')
print('  curl http://localhost:8000/api/nervous-system/status')
