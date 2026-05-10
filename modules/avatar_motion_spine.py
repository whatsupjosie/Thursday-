"""PubCast Avatar Motion Spine.

Dependency-light authority layer for Manny/Sheila GLB motion. It does not
render; it turns mocap/script/behavior/idle inputs into one safe pose packet.
Priority: safety > mocap > scripted > behavior > idle.

Project rule: sprites are banned until the project owner explicitly reverses
that rule. Fallback motion may freeze or idle the GLB skeleton, but it must not
replace Manny/Sheila with 2D sprite/canvas/image puppets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple
import time

Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]
SPRITES_BANNED = True
FORBIDDEN_SPRITE_TERMS = ("sprite", "spritesheet", "billboard_avatar", "canvas_puppet", "image_avatar")


class MotionSource(str, Enum):
    SAFETY = "safety"
    MOCAP = "mocap"
    SCRIPTED = "scripted"
    BEHAVIOR = "behavior"
    IDLE = "idle"


class EmotionTag(str, Enum):
    NEUTRAL = "neutral"
    CONFIDENT = "confident"
    PLAYFUL = "playful"
    CURIOUS = "curious"
    STARTLED = "startled"
    TIRED = "tired"
    THINKING = "thinking"
    WARM = "warm"


@dataclass(frozen=True)
class BoneTransform:
    position: Vec3 = (0.0, 0.0, 0.0)
    rotation: Quat = (0.0, 0.0, 0.0, 1.0)
    scale: Vec3 = (1.0, 1.0, 1.0)

    def to_dict(self) -> Dict[str, list[float]]:
        return {"position": list(self.position), "rotation": list(self.rotation), "scale": list(self.scale)}


@dataclass(frozen=True)
class AnimationDefinition:
    name: str
    duration: float
    loop: bool
    bones: Mapping[str, BoneTransform]
    category: str = "idle"
    emotion: EmotionTag = EmotionTag.NEUTRAL
    glow: float = 1.0
    mocap_override_allowed: bool = True
    cooldown_seconds: float = 0.0


@dataclass(frozen=True)
class AvatarContext:
    avatar_id: str
    skeleton_id: str = "pubcast_authoritative_humanoid_v1"
    active_emotion: EmotionTag = EmotionTag.NEUTRAL
    is_speaking: bool = False
    is_listening: bool = False
    is_walking: bool = False
    scene_context: str = "studio"


@dataclass(frozen=True)
class MotionIntent:
    source: MotionSource
    priority: int
    animation_name: Optional[str] = None
    bones: Mapping[str, BoneTransform] = field(default_factory=dict)
    root_motion: Vec3 = (0.0, 0.0, 0.0)
    foot_contacts: Mapping[str, bool] = field(default_factory=dict)
    confidence: float = 1.0
    reason: str = ""


@dataclass(frozen=True)
class PosePacket:
    avatar_id: str
    skeleton_id: str
    timestamp: float
    source: MotionSource
    animation_name: str
    bones: Mapping[str, BoneTransform]
    root_motion: Vec3 = (0.0, 0.0, 0.0)
    foot_contacts: Mapping[str, bool] = field(default_factory=dict)
    gesture_layer: Optional[str] = None
    emotion_layer: EmotionTag = EmotionTag.NEUTRAL
    glow_intensity_modifier: float = 1.0
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "avatar_id": self.avatar_id,
            "skeleton_id": self.skeleton_id,
            "timestamp": self.timestamp,
            "source": self.source.value,
            "animation_name": self.animation_name,
            "bones": {k: v.to_dict() for k, v in self.bones.items()},
            "root_motion": list(self.root_motion),
            "foot_contacts": dict(self.foot_contacts),
            "gesture_layer": self.gesture_layer,
            "emotion_layer": self.emotion_layer.value,
            "glow_intensity_modifier": self.glow_intensity_modifier,
            "confidence": max(0.0, min(1.0, self.confidence)),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DoctorResult:
    ok: bool
    checks: Mapping[str, bool]
    warnings: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()


class AvatarAnimationLibrary:
    def __init__(self) -> None:
        self.animations: Dict[str, AnimationDefinition] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        self.add(AnimationDefinition("idle_breathing", 4.0, True, {"chest": BoneTransform(rotation=(0.03, 0, 0, 0.9995))}, "idle", EmotionTag.WARM, 1.08))
        self.add(AnimationDefinition("walk_basic", 2.0, True, {
            "thigh_l": BoneTransform(rotation=(0.4, 0, 0, 0.92)),
            "thigh_r": BoneTransform(rotation=(-0.4, 0, 0, 0.92)),
            "upperarm_l": BoneTransform(rotation=(-0.3, 0, 0, 0.95)),
            "upperarm_r": BoneTransform(rotation=(0.3, 0, 0, 0.95)),
        }, "locomotion", EmotionTag.CONFIDENT, 1.0))
        self.add(AnimationDefinition("wave_hello", 2.0, False, {
            "upperarm_r": BoneTransform(rotation=(0, 0, -0.7, 0.72)),
            "lowerarm_r": BoneTransform(rotation=(0, 0.4, 0, 0.92)),
        }, "gesture", EmotionTag.WARM, 1.25, True, 1.0))
        self.add(AnimationDefinition("thinking_pose", 3.0, True, {
            "head": BoneTransform(rotation=(0.07, -0.08, 0, 0.994)),
            "hand_r": BoneTransform(position=(0.25, 1.2, 0.2)),
        }, "emotional", EmotionTag.THINKING, 1.05))
        self.add(AnimationDefinition("startled_recover", 1.25, False, {
            "spine": BoneTransform(rotation=(-0.12, 0, 0, 0.993)),
            "head": BoneTransform(rotation=(-0.1, 0, 0, 0.995)),
        }, "react", EmotionTag.STARTLED, 1.4, False, 2.0))
        self.add(AnimationDefinition("ethereal_drift", 8.0, True, {"root": BoneTransform(position=(0, 0.18, 0))}, "ethereal", EmotionTag.WARM, 1.4))
        self.add(AnimationDefinition("safe_freeze_midshot", 1.0, True, {"root": BoneTransform()}, "safety", EmotionTag.NEUTRAL, 0.8, False))

    def add(self, animation: AnimationDefinition) -> None:
        if animation.duration < 0:
            raise ValueError(f"animation duration cannot be negative: {animation.name}")
        if SPRITES_BANNED:
            lowered = f"{animation.name} {animation.category}".lower()
            if any(term in lowered for term in FORBIDDEN_SPRITE_TERMS):
                raise ValueError(f"sprite-style avatar fallback is banned: {animation.name}")
        self.animations[animation.name] = animation

    def get(self, name: str) -> Optional[AnimationDefinition]:
        return self.animations.get(name)

    def choose_for_context(self, context: AvatarContext) -> AnimationDefinition:
        if context.is_walking:
            return self.animations["walk_basic"]
        if context.active_emotion == EmotionTag.THINKING or context.is_listening:
            return self.animations["thinking_pose"]
        if context.active_emotion == EmotionTag.STARTLED:
            return self.animations["startled_recover"]
        if context.is_speaking and context.active_emotion == EmotionTag.PLAYFUL:
            return self.animations["wave_hello"]
        if context.scene_context in {"waiting_room", "dressing_room", "green_room"}:
            return self.animations["ethereal_drift"]
        return self.animations["idle_breathing"]


class AvatarMotionRouter:
    def __init__(self, library: Optional[AvatarAnimationLibrary] = None) -> None:
        self.library = library or AvatarAnimationLibrary()

    def select(self, context: AvatarContext, intents: Iterable[MotionIntent]) -> MotionIntent:
        valid = [i for i in intents if i.confidence > 0]
        if valid:
            return sorted(valid, key=lambda i: i.priority, reverse=True)[0]
        fallback = self.library.choose_for_context(context)
        source = MotionSource.IDLE if fallback.category == "idle" else MotionSource.BEHAVIOR
        return MotionIntent(source, 10, fallback.name, confidence=0.8, reason="context fallback")

    def route(self, context: AvatarContext, intents: Iterable[MotionIntent], now: Optional[float] = None) -> PosePacket:
        now = time.time() if now is None else now
        selected = self.select(context, intents)
        animation_name = selected.animation_name or "direct_pose"
        if selected.source == MotionSource.MOCAP and selected.bones:
            bones = selected.bones
            glow = 1.0
            gesture = None
        else:
            animation = self.library.get(animation_name) or self.library.get("idle_breathing")
            assert animation is not None
            animation_name = animation.name
            bones = animation.bones
            glow = animation.glow
            gesture = animation.category if animation.category in {"gesture", "react"} else None
        return PosePacket(
            avatar_id=context.avatar_id,
            skeleton_id=context.skeleton_id,
            timestamp=now,
            source=selected.source,
            animation_name=animation_name,
            bones=bones,
            root_motion=selected.root_motion,
            foot_contacts=selected.foot_contacts,
            gesture_layer=gesture,
            emotion_layer=context.active_emotion,
            glow_intensity_modifier=glow,
            confidence=selected.confidence,
            metadata={"reason": selected.reason, "priority": selected.priority, "sprites_banned": SPRITES_BANNED},
        )


class AvatarRuntimeDoctor:
    def __init__(self, repo_root: Path | str) -> None:
        self.repo_root = Path(repo_root)

    def run(self) -> DoctorResult:
        forbidden_hits = self._find_forbidden_sprite_hits()
        checks = {
            "repo_root_exists": self.repo_root.exists(),
            "sprites_banned": SPRITES_BANNED,
            "no_forbidden_sprite_fallbacks": not forbidden_hits,
            "manny_glb_known_path": any((self.repo_root / p).exists() for p in ("assets/avatars/Manny.glb", "assets/avatar/manny.glb")),
            "sheila_glb_known_path": any((self.repo_root / p).exists() for p in ("assets/avatars/Sheila.glb", "assets/avatar/sheila.glb")),
            "manifest_present": any((self.repo_root / p).exists() for p in ("data/avatars/manifest.json", "assets/avatars/manifest.json")),
            "static_presets_present": (self.repo_root / "static" / "pubcast_animation_presets.js").exists(),
        }
        errors = [] if checks["repo_root_exists"] else [f"repo root does not exist: {self.repo_root}"]
        if forbidden_hits:
            errors.extend(f"forbidden sprite fallback reference: {hit}" for hit in forbidden_hits[:20])
        warnings = []
        if not checks["manny_glb_known_path"]:
            warnings.append("Manny GLB not found at known seed/full-app paths.")
        if not checks["sheila_glb_known_path"]:
            warnings.append("Sheila GLB not found at known seed/full-app paths.")
        if not checks["manifest_present"]:
            warnings.append("Avatar manifest not found; full app should forbid sprite replacement there.")
        return DoctorResult(ok=not errors, checks=checks, warnings=tuple(warnings), errors=tuple(errors))

    def _find_forbidden_sprite_hits(self) -> Tuple[str, ...]:
        if not self.repo_root.exists() or not SPRITES_BANNED:
            return ()
        allowed_files = {
            "reviewed_input/UPLOADED_ANIMATION_INPUTS.md",
            "docs/AVATAR_ASSET_POLICY.md",
        }
        hits: list[str] = []
        for path in self.repo_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".js", ".mjs", ".rs", ".md", ".json"}:
                continue
            rel = path.relative_to(self.repo_root).as_posix()
            if rel in allowed_files or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            if any(term in text for term in FORBIDDEN_SPRITE_TERMS):
                hits.append(rel)
        return tuple(hits)


def build_safety_freeze_intent(reason: str = "runtime safety fallback") -> MotionIntent:
    return MotionIntent(MotionSource.SAFETY, 1000, "safe_freeze_midshot", confidence=1.0, reason=reason)


def build_mocap_intent(bones: Mapping[str, BoneTransform], confidence: float = 1.0, reason: str = "live mocap") -> MotionIntent:
    return MotionIntent(MotionSource.MOCAP, 900, bones=bones, confidence=confidence, reason=reason)
