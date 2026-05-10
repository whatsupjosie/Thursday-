"""PubCast avatar performance cue catalog.

Broad GLB/skeleton-only animation cue library for Manny/Sheila and future
avatars: dance, props, studio work, social gestures, etiquette, background
small talk, environment traversal, driving, carrying, pushing, and pulling.

Each cue emits a PosePacket directly so it can travel through
AvatarMotionBridge without bloating the core router. This file contains no
2D/avatar replacement fallback behavior.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple
import time

from .avatar_motion_spine import BoneTransform, EmotionTag, MotionSource, PosePacket, SPRITES_BANNED

Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]


class CueFamily(str, Enum):
    DANCE = "dance"
    ITEM = "item"
    STUDIO_WORK = "studio_work"
    SOCIAL = "social"
    ETIQUETTE = "etiquette"
    SMALL_TALK = "small_talk"
    ENVIRONMENT = "environment"
    VEHICLE = "vehicle"
    LOAD_WORK = "load_work"


@dataclass(frozen=True)
class PropAttachment:
    item_id: str
    display_name: str
    attach_bone: str
    local_position: Vec3 = (0.0, 0.0, 0.0)
    local_rotation: Quat = (0.0, 0.0, 0.0, 1.0)
    target_anchor: Optional[str] = None
    weight_class: str = "none"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "display_name": self.display_name,
            "attach_bone": self.attach_bone,
            "local_position": list(self.local_position),
            "local_rotation": list(self.local_rotation),
            "target_anchor": self.target_anchor,
            "weight_class": self.weight_class,
        }


@dataclass(frozen=True)
class PerformanceCue:
    name: str
    family: CueFamily
    bones: Mapping[str, BoneTransform]
    duration: float
    loop: bool = False
    emotion: EmotionTag = EmotionTag.NEUTRAL
    priority: int = 700
    glow: float = 1.0
    prop: Optional[PropAttachment] = None
    foot_contacts: Mapping[str, bool] = field(default_factory=dict)
    notes: str = ""

    def to_packet(self, avatar_id: str = "manny", *, skeleton_id: str = "pubcast_authoritative_humanoid_v1", now: Optional[float] = None) -> PosePacket:
        return PosePacket(
            avatar_id=avatar_id,
            skeleton_id=skeleton_id,
            timestamp=time.time() if now is None else now,
            source=MotionSource.SCRIPTED,
            animation_name=self.name,
            bones=self.bones,
            foot_contacts=self.foot_contacts,
            gesture_layer=self.family.value,
            emotion_layer=self.emotion,
            glow_intensity_modifier=self.glow,
            confidence=1.0,
            metadata={
                "cue_family": self.family.value,
                "duration": self.duration,
                "loop": self.loop,
                "priority": self.priority,
                "notes": self.notes,
                "prop": self.prop.to_dict() if self.prop else None,
                "sprites_banned": SPRITES_BANNED,
            },
        )


def bt(position: Vec3 = (0.0, 0.0, 0.0), rotation: Quat = (0.0, 0.0, 0.0, 1.0)) -> BoneTransform:
    return BoneTransform(position=position, rotation=rotation)


PERFORMANCE_CUES: Dict[str, PerformanceCue] = {
    # Dance / looking alive
    "dance_curtsey_pop": PerformanceCue("dance_curtsey_pop", CueFamily.DANCE, {"root": bt((0,-0.08,0)), "spine": bt(rotation=(0.04,0,0.08,0.995)), "hip": bt(rotation=(0,0.12,0,0.993)), "upperarm_l": bt(rotation=(-0.18,0.1,0.2,0.96)), "upperarm_r": bt(rotation=(-0.18,-0.1,-0.2,0.96)), "thigh_l": bt(rotation=(0.18,0,0.08,0.98)), "thigh_r": bt(rotation=(-0.08,0,-0.04,0.99))}, 2.4, True, EmotionTag.PLAYFUL, 760, 1.25, notes="Playful stage dance with theatrical dip."),
    "dance_neon_sway": PerformanceCue("dance_neon_sway", CueFamily.DANCE, {"root": bt((0,0.02,0)), "spine": bt(rotation=(0.02,0,0.10,0.994)), "head": bt(rotation=(0,-0.04,0.04,0.998)), "upperarm_l": bt(rotation=(-0.12,0.08,0.18,0.974)), "upperarm_r": bt(rotation=(-0.12,-0.08,-0.18,0.974))}, 4.0, True, EmotionTag.WARM, 720, 1.35, notes="Soft attractive hologram sway."),
    "dance_stage_spin": PerformanceCue("dance_stage_spin", CueFamily.DANCE, {"root": bt(rotation=(0,0.35,0,0.937)), "spine": bt(rotation=(0,0.15,0,0.989)), "upperarm_l": bt(rotation=(-0.2,0,0.55,0.81)), "upperarm_r": bt(rotation=(-0.2,0,-0.55,0.81))}, 1.8, False, EmotionTag.CONFIDENT, 780, 1.45, notes="Confident stage turn/open-arm finish."),

    # Desk, items, scripts
    "type_at_desk_loop": PerformanceCue("type_at_desk_loop", CueFamily.ITEM, {"root": bt((0,-0.55,0)), "spine": bt(rotation=(0.12,0,0,0.993)), "head": bt(rotation=(0.10,0,0,0.995)), "upperarm_l": bt(rotation=(-0.45,0.05,0.22,0.86)), "upperarm_r": bt(rotation=(-0.45,-0.05,-0.22,0.86)), "lowerarm_l": bt(rotation=(-0.7,0,0.1,0.71)), "lowerarm_r": bt(rotation=(-0.7,0,-0.1,0.71)), "hand_l": bt((-0.16,0.74,0.32)), "hand_r": bt((0.16,0.74,0.32))}, 3.0, True, EmotionTag.THINKING, 765, 1.05, PropAttachment("keyboard", "Desk Keyboard", "desk", target_anchor="desk"), notes="Seated typing loop at desk."),
    "open_script_binder": PerformanceCue("open_script_binder", CueFamily.ITEM, {"spine": bt(rotation=(0.08,0,0,0.997)), "head": bt(rotation=(0.14,0,0,0.99)), "upperarm_l": bt(rotation=(-0.28,0.18,0.08,0.94)), "upperarm_r": bt(rotation=(-0.28,-0.18,-0.08,0.94)), "hand_l": bt((-0.22,1.0,0.25)), "hand_r": bt((0.22,1.0,0.25))}, 1.6, False, EmotionTag.CURIOUS, 735, 1.05, PropAttachment("script_binder", "Script Binder", "hand_l", target_anchor="both_hands"), notes="Open/close a book, script, or binder."),
    "hold_note_card": PerformanceCue("hold_note_card", CueFamily.ITEM, {"upperarm_r": bt(rotation=(-0.22,-0.12,-0.18,0.95)), "lowerarm_r": bt(rotation=(-0.45,0,-0.10,0.885)), "hand_r": bt((0.28,1.15,0.18)), "head": bt(rotation=(0.06,-0.04,0,0.997))}, 2.0, True, EmotionTag.THINKING, 720, 1.0, PropAttachment("note_card", "Note Card", "hand_r"), notes="Holding or glancing at a card."),

    # Studio work
    "operate_video_console": PerformanceCue("operate_video_console", CueFamily.STUDIO_WORK, {"root": bt((0,-0.45,0)), "spine": bt(rotation=(0.10,0,0.03,0.994)), "head": bt(rotation=(0.06,0.10,0,0.993)), "hand_l": bt((-0.22,0.82,0.36)), "hand_r": bt((0.22,0.82,0.36)), "lowerarm_l": bt(rotation=(-0.55,0,0.18,0.81)), "lowerarm_r": bt(rotation=(-0.55,0,-0.18,0.81))}, 3.2, True, EmotionTag.THINKING, 760, 1.1, PropAttachment("video_console", "Video Console", "desk", target_anchor="console"), notes="Hands working switches/sliders at video console."),
    "operate_camera_rig": PerformanceCue("operate_camera_rig", CueFamily.STUDIO_WORK, {"spine": bt(rotation=(0.08,-0.10,0,0.992)), "head": bt(rotation=(0.02,-0.18,0,0.984)), "upperarm_l": bt(rotation=(-0.30,0.16,0.08,0.94)), "upperarm_r": bt(rotation=(-0.30,-0.16,-0.08,0.94)), "hand_l": bt((-0.25,1.05,0.28)), "hand_r": bt((0.25,1.05,0.28))}, 2.4, True, EmotionTag.CONFIDENT, 770, 1.1, PropAttachment("camera_rig", "Camera Rig", "hand_r", target_anchor="camera_handle"), notes="Operating or aiming a camera."),
    "talkback_mic": PerformanceCue("talkback_mic", CueFamily.STUDIO_WORK, {"head": bt(rotation=(0.02,0.05,0,0.998)), "spine": bt(rotation=(0.04,0.02,0,0.999)), "upperarm_r": bt(rotation=(-0.18,-0.22,-0.18,0.94)), "lowerarm_r": bt(rotation=(-0.75,0,-0.18,0.64)), "hand_r": bt((0.18,1.45,0.12))}, 1.8, True, EmotionTag.CONFIDENT, 760, 1.08, PropAttachment("talkback_mic", "Talkback Mic", "hand_r"), notes="Speaking into mic/headset/talkback."),

    # Social and etiquette
    "clap_applause": PerformanceCue("clap_applause", CueFamily.SOCIAL, {"spine": bt(rotation=(0.02,0,0,0.999)), "upperarm_l": bt(rotation=(-0.30,0.16,0.22,0.91)), "upperarm_r": bt(rotation=(-0.30,-0.16,-0.22,0.91)), "hand_l": bt((-0.10,1.20,0.18)), "hand_r": bt((0.10,1.20,0.18))}, 1.2, True, EmotionTag.WARM, 750, 1.2, notes="Looping applause/clapping."),
    "handshake_offer": PerformanceCue("handshake_offer", CueFamily.SOCIAL, {"spine": bt(rotation=(0.04,0,0,0.999)), "upperarm_r": bt(rotation=(-0.15,-0.08,-0.24,0.96)), "lowerarm_r": bt(rotation=(-0.18,0,-0.10,0.98)), "hand_r": bt((0.45,1.05,0.25))}, 1.5, False, EmotionTag.WARM, 755, 1.1, notes="Offer right hand for handshake; paired avatar can mirror."),
    "bow_formal": PerformanceCue("bow_formal", CueFamily.ETIQUETTE, {"root": bt((0,-0.03,0)), "spine": bt(rotation=(0.35,0,0,0.937)), "head": bt(rotation=(0.20,0,0,0.98)), "upperarm_l": bt(rotation=(0.08,0,0.08,0.99)), "upperarm_r": bt(rotation=(0.08,0,-0.08,0.99))}, 1.8, False, EmotionTag.CONFIDENT, 740, 1.0, notes="Formal bow."),
    "curtsey_casual": PerformanceCue("curtsey_casual", CueFamily.ETIQUETTE, {"root": bt((0,-0.12,0)), "spine": bt(rotation=(0.10,0,0.04,0.994)), "head": bt(rotation=(0.08,0,0.02,0.997)), "thigh_l": bt(rotation=(0.16,0,0.12,0.98)), "thigh_r": bt(rotation=(-0.05,0,-0.08,0.995)), "upperarm_l": bt(rotation=(-0.12,0.12,0.25,0.96)), "upperarm_r": bt(rotation=(-0.12,-0.12,-0.25,0.96))}, 1.7, False, EmotionTag.WARM, 745, 1.1, notes="Small polite curtsey."),
    "curtsey_deep": PerformanceCue("curtsey_deep", CueFamily.ETIQUETTE, {"root": bt((0,-0.28,0)), "spine": bt(rotation=(0.18,0,0.05,0.982)), "head": bt(rotation=(0.12,0,0.02,0.993)), "thigh_l": bt(rotation=(0.35,0,0.18,0.92)), "thigh_r": bt(rotation=(-0.18,0,-0.12,0.97)), "upperarm_l": bt(rotation=(-0.20,0.16,0.36,0.90)), "upperarm_r": bt(rotation=(-0.20,-0.16,-0.36,0.90))}, 2.4, False, EmotionTag.WARM, 748, 1.18, notes="Deeper theatrical curtsey."),

    # Small talk/background life
    "small_talk_standing_loop": PerformanceCue("small_talk_standing_loop", CueFamily.SMALL_TALK, {"spine": bt(rotation=(0.02,0.04,0,0.998)), "head": bt(rotation=(0,0.10,0.02,0.995)), "upperarm_r": bt(rotation=(-0.10,-0.05,-0.12,0.987)), "hand_r": bt((0.20,1.05,0.10))}, 5.0, True, EmotionTag.WARM, 690, 1.0, notes="Standing next to another avatar talking/listening."),
    "small_talk_table_loop": PerformanceCue("small_talk_table_loop", CueFamily.SMALL_TALK, {"root": bt((0,-0.55,0)), "spine": bt(rotation=(0.08,0.03,0,0.996)), "head": bt(rotation=(0.04,0.10,0,0.994)), "hand_l": bt((-0.18,0.86,0.20)), "hand_r": bt((0.18,0.88,0.22))}, 6.0, True, EmotionTag.WARM, 690, 1.0, notes="Sitting across a table in conversation."),
    "background_kid_fidget": PerformanceCue("background_kid_fidget", CueFamily.SMALL_TALK, {"root": bt((0,0.02,0)), "spine": bt(rotation=(0.03,-0.04,0.08,0.995)), "head": bt(rotation=(0.02,-0.12,0.03,0.992)), "hand_l": bt((-0.12,0.9,0.12)), "hand_r": bt((0.14,0.92,0.10))}, 3.0, True, EmotionTag.PLAYFUL, 660, 1.05, notes="Background child/extra fidget loop."),

    # Environment and vehicle
    "walk_stairs_up": PerformanceCue("walk_stairs_up", CueFamily.ENVIRONMENT, {"root": bt((0,0.18,0.18)), "spine": bt(rotation=(0.08,0,0,0.997)), "thigh_l": bt(rotation=(0.45,0,0,0.89)), "thigh_r": bt(rotation=(-0.20,0,0,0.98))}, 1.2, True, EmotionTag.NEUTRAL, 735, 1.0, foot_contacts={"left": True, "right": False}, notes="Ascending stairs."),
    "walk_stairs_down": PerformanceCue("walk_stairs_down", CueFamily.ENVIRONMENT, {"root": bt((0,-0.12,0.18)), "spine": bt(rotation=(-0.04,0,0,0.999)), "thigh_l": bt(rotation=(-0.25,0,0,0.97)), "thigh_r": bt(rotation=(0.35,0,0,0.94))}, 1.2, True, EmotionTag.NEUTRAL, 735, 1.0, foot_contacts={"left": False, "right": True}, notes="Descending stairs."),
    "use_ladder_climb": PerformanceCue("use_ladder_climb", CueFamily.ENVIRONMENT, {"root": bt((0,0.25,0)), "spine": bt(rotation=(0.10,0,0,0.995)), "hand_l": bt((-0.28,1.35,0.25)), "hand_r": bt((0.28,1.10,0.25)), "thigh_l": bt(rotation=(0.40,0,0,0.91))}, 1.6, True, EmotionTag.THINKING, 730, 1.0, notes="Climbing a ladder with alternating hands/feet."),
    "open_door": PerformanceCue("open_door", CueFamily.ENVIRONMENT, {"spine": bt(rotation=(0.04,-0.10,0,0.994)), "upperarm_r": bt(rotation=(-0.18,-0.18,-0.22,0.94)), "lowerarm_r": bt(rotation=(-0.30,0,-0.12,0.945)), "hand_r": bt((0.46,1.05,0.24))}, 1.5, False, EmotionTag.NEUTRAL, 720, 1.0, PropAttachment("door_handle", "Door Handle", "hand_r", target_anchor="door"), notes="Open or close door handle."),
    "drive_hands_on_wheel": PerformanceCue("drive_hands_on_wheel", CueFamily.VEHICLE, {"root": bt((0,-0.55,0)), "spine": bt(rotation=(0.05,0,0,0.999)), "head": bt(rotation=(0.02,0,0,0.999)), "hand_l": bt((-0.24,1.05,0.35)), "hand_r": bt((0.24,1.05,0.35)), "lowerarm_l": bt(rotation=(-0.55,0,0.16,0.82)), "lowerarm_r": bt(rotation=(-0.55,0,-0.16,0.82))}, 4.0, True, EmotionTag.THINKING, 720, 1.0, PropAttachment("steering_wheel", "Steering Wheel", "vehicle", target_anchor="vehicle_cockpit"), notes="Driving loop, hands on wheel."),
    "drive_check_mirror": PerformanceCue("drive_check_mirror", CueFamily.VEHICLE, {"root": bt((0,-0.55,0)), "spine": bt(rotation=(0.04,-0.10,0,0.994)), "head": bt(rotation=(0.02,-0.28,0,0.96)), "hand_l": bt((-0.24,1.05,0.35)), "hand_r": bt((0.24,1.05,0.35))}, 1.4, False, EmotionTag.THINKING, 730, 1.0, notes="Driver looks to mirror/over shoulder."),

    # Carrying, pushing, pulling / load work
    "carry_light_one_hand": PerformanceCue("carry_light_one_hand", CueFamily.LOAD_WORK, {"spine": bt(rotation=(0.02,0,0.03,0.999)), "upperarm_r": bt(rotation=(-0.08,-0.04,-0.16,0.984)), "lowerarm_r": bt(rotation=(-0.28,0,-0.08,0.956)), "hand_r": bt((0.30,0.90,0.10))}, 3.0, True, EmotionTag.NEUTRAL, 725, 1.0, PropAttachment("light_item", "Light Item", "hand_r", weight_class="light"), notes="Casual one-handed carry for light objects."),
    "carry_medium_two_hand": PerformanceCue("carry_medium_two_hand", CueFamily.LOAD_WORK, {"spine": bt(rotation=(0.10,0,0,0.995)), "upperarm_l": bt(rotation=(-0.30,0.12,0.08,0.94)), "upperarm_r": bt(rotation=(-0.30,-0.12,-0.08,0.94)), "lowerarm_l": bt(rotation=(-0.55,0,0.12,0.82)), "lowerarm_r": bt(rotation=(-0.55,0,-0.12,0.82)), "hand_l": bt((-0.22,0.82,0.24)), "hand_r": bt((0.22,0.82,0.24))}, 3.0, True, EmotionTag.THINKING, 735, 1.0, PropAttachment("medium_box", "Medium Object", "both_hands", target_anchor="both_hands", weight_class="medium"), notes="Two-handed medium carry."),
    "carry_heavy_strain": PerformanceCue("carry_heavy_strain", CueFamily.LOAD_WORK, {"root": bt((0,-0.08,0)), "spine": bt(rotation=(0.22,0,0,0.975)), "head": bt(rotation=(0.10,0,0,0.995)), "upperarm_l": bt(rotation=(-0.42,0.18,0.08,0.88)), "upperarm_r": bt(rotation=(-0.42,-0.18,-0.08,0.88)), "lowerarm_l": bt(rotation=(-0.72,0,0.10,0.69)), "lowerarm_r": bt(rotation=(-0.72,0,-0.10,0.69)), "thigh_l": bt(rotation=(0.18,0,0,0.984)), "thigh_r": bt(rotation=(0.12,0,0,0.992))}, 3.5, True, EmotionTag.TIRED, 745, 0.95, PropAttachment("heavy_object", "Heavy Object", "both_hands", target_anchor="both_hands", weight_class="heavy"), notes="Extremely heavy carry with body strain."),
    "push_cart_light": PerformanceCue("push_cart_light", CueFamily.LOAD_WORK, {"spine": bt(rotation=(0.12,0,0,0.993)), "upperarm_l": bt(rotation=(-0.25,0.10,0.10,0.96)), "upperarm_r": bt(rotation=(-0.25,-0.10,-0.10,0.96)), "hand_l": bt((-0.28,1.0,0.38)), "hand_r": bt((0.28,1.0,0.38)), "thigh_l": bt(rotation=(0.25,0,0,0.968)), "thigh_r": bt(rotation=(-0.20,0,0,0.98))}, 2.0, True, EmotionTag.NEUTRAL, 735, 1.0, PropAttachment("push_cart", "Push Cart", "both_hands", target_anchor="cart_handle", weight_class="light"), foot_contacts={"left": True, "right": False}, notes="Pushing a light/normal rolling cart."),
    "push_heavy_object": PerformanceCue("push_heavy_object", CueFamily.LOAD_WORK, {"root": bt((0,-0.04,0)), "spine": bt(rotation=(0.32,0,0,0.947)), "head": bt(rotation=(0.12,0,0,0.993)), "upperarm_l": bt(rotation=(-0.18,0.12,0.16,0.965)), "upperarm_r": bt(rotation=(-0.18,-0.12,-0.16,0.965)), "hand_l": bt((-0.30,1.05,0.45)), "hand_r": bt((0.30,1.05,0.45)), "thigh_l": bt(rotation=(0.38,0,0,0.925)), "thigh_r": bt(rotation=(-0.18,0,0,0.984))}, 2.4, True, EmotionTag.TIRED, 750, 0.92, PropAttachment("heavy_push_target", "Heavy Push Target", "both_hands", target_anchor="push_surface", weight_class="heavy"), foot_contacts={"left": True, "right": True}, notes="Leaning hard into a heavy push."),
    "pull_object_rope": PerformanceCue("pull_object_rope", CueFamily.LOAD_WORK, {"root": bt((0,-0.04,0)), "spine": bt(rotation=(-0.18,0,0,0.984)), "head": bt(rotation=(0.04,0,0,0.999)), "upperarm_l": bt(rotation=(-0.48,0.10,0.04,0.87)), "upperarm_r": bt(rotation=(-0.48,-0.10,-0.04,0.87)), "lowerarm_l": bt(rotation=(-0.65,0,0.08,0.75)), "lowerarm_r": bt(rotation=(-0.65,0,-0.08,0.75)), "hand_l": bt((-0.18,1.05,0.28)), "hand_r": bt((0.18,1.05,0.28)), "thigh_l": bt(rotation=(-0.20,0,0,0.98)), "thigh_r": bt(rotation=(0.30,0,0,0.955))}, 2.5, True, EmotionTag.TIRED, 748, 0.95, PropAttachment("pull_target", "Pull Target", "both_hands", target_anchor="rope_or_handle", weight_class="heavy"), foot_contacts={"left": True, "right": True}, notes="Pulling an object by rope/handle with backward lean."),
}


def get_performance_cue(name: str) -> PerformanceCue:
    try:
        return PERFORMANCE_CUES[name]
    except KeyError as exc:
        known = ", ".join(sorted(PERFORMANCE_CUES))
        raise ValueError(f"unknown PubCast performance cue '{name}'. Known cues: {known}") from exc


def build_performance_packet(name: str, avatar_id: str = "manny", *, now: Optional[float] = None) -> PosePacket:
    return get_performance_cue(name).to_packet(avatar_id=avatar_id, now=now)


def list_performance_cues(family: Optional[CueFamily] = None) -> Tuple[PerformanceCue, ...]:
    cues = PERFORMANCE_CUES.values()
    if family is not None:
        cues = [cue for cue in cues if cue.family == family]
    return tuple(sorted(cues, key=lambda cue: cue.name))
