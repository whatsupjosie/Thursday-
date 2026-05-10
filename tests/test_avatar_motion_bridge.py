import json

from modules.avatar_motion_bridge import BRIDGE_PROTOCOL, AvatarMotionBridge, build_ws_payload
from modules.avatar_motion_spine import AvatarContext, BoneTransform, MotionSource, build_mocap_intent


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
