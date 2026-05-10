import json

from modules.avatar_motion_bridge import (
    BRIDGE_PROTOCOL,
    AvatarMotionBridge,
    build_ws_payload,
    build_ws_payload_from_packet,
)
from modules.avatar_motion_spine import AvatarContext, BoneTransform, MotionSource, build_mocap_intent
from modules.avatar_performance_cues import build_performance_packet


def test_bridge_builds_protocol_event():
    bridge = AvatarMotionBridge()
    event = bridge.build_motion_event(AvatarContext(avatar_id="manny"), [], now=123.0, metadata={"room": "studio"})
    data = event.to_dict()
    assert data["protocol"] == BRIDGE_PROTOCOL
    assert data["event_type"] == "avatar_pose"
    assert data["avatar_id"] == "manny"
    assert data["pose"]["avatar_id"] == "manny"
    assert data["transport_metadata"]["room"] == "studio"


def test_bridge_serializes_mocap_pose_payload():
    payload = build_ws_payload(
        AvatarContext(avatar_id="sheila"),
        [build_mocap_intent({"head": BoneTransform(rotation=(0.1, 0.0, 0.0, 0.995))})],
        now=456.0,
    )
    data = json.loads(payload)
    assert data["protocol"] == BRIDGE_PROTOCOL
    assert data["pose"]["source"] == MotionSource.MOCAP.value
    assert data["pose"]["bones"]["head"]["rotation"] == [0.1, 0.0, 0.0, 0.995]


def test_bridge_wraps_direct_performance_packet():
    packet = build_performance_packet("dance_neon_sway", avatar_id="manny", now=789.0)
    payload = build_ws_payload_from_packet(packet, now=789.0)
    data = json.loads(payload)
    assert data["protocol"] == BRIDGE_PROTOCOL
    assert data["event_type"] == "avatar_pose"
    assert data["avatar_id"] == "manny"
    assert data["pose"]["animation_name"] == "dance_neon_sway"
    assert data["pose"]["metadata"]["cue_family"] == "dance"
    assert data["pose"]["metadata"]["sprites_banned"] is True
    assert "spine" in data["pose"]["bones"]
