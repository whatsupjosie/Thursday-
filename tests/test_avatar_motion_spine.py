from pathlib import Path

from modules.avatar_motion_spine import (
    AvatarContext,
    AvatarMotionRouter,
    AvatarRuntimeDoctor,
    BoneTransform,
    EmotionTag,
    MotionSource,
    build_mocap_intent,
    build_safety_freeze_intent,
)


def test_context_fallback_selects_walk_for_walking_avatar():
    router = AvatarMotionRouter()
    packet = router.route(AvatarContext(avatar_id="manny", is_walking=True), [], now=100.0)
    assert packet.animation_name == "walk_basic"
    assert packet.source == MotionSource.BEHAVIOR
    assert "thigh_l" in packet.bones


def test_mocap_intent_wins_over_behavior_context():
    router = AvatarMotionRouter()
    mocap = build_mocap_intent({"head": BoneTransform(rotation=(0.1, 0.0, 0.0, 0.995))}, confidence=0.91)
    packet = router.route(AvatarContext(avatar_id="sheila", is_walking=True), [mocap], now=100.0)
    assert packet.source == MotionSource.MOCAP
    assert packet.animation_name == "direct_pose"
    assert packet.bones["head"].rotation == (0.1, 0.0, 0.0, 0.995)
    assert packet.confidence == 0.91


def test_safety_freeze_wins_over_mocap():
    router = AvatarMotionRouter()
    mocap = build_mocap_intent({"head": BoneTransform(rotation=(0.1, 0.0, 0.0, 0.995))})
    packet = router.route(AvatarContext(avatar_id="manny"), [mocap, build_safety_freeze_intent()], now=100.0)
    assert packet.source == MotionSource.SAFETY
    assert packet.animation_name == "safe_freeze_midshot"


def test_pose_packet_serializes_renderer_contract():
    router = AvatarMotionRouter()
    packet = router.route(AvatarContext(avatar_id="manny", active_emotion=EmotionTag.THINKING), [], now=100.0)
    data = packet.to_dict()
    assert data["avatar_id"] == "manny"
    assert data["skeleton_id"] == "pubcast_authoritative_humanoid_v1"
    assert data["emotion_layer"] == "thinking"
    assert isinstance(data["bones"], dict)


def test_doctor_allows_seed_repo_without_assets(tmp_path: Path):
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "pubcast_animation_presets.js").write_text("export {};", encoding="utf-8")
    result = AvatarRuntimeDoctor(tmp_path).run()
    assert result.ok
    assert result.checks["repo_root_exists"]
    assert result.checks["static_presets_present"]
    assert result.warnings
