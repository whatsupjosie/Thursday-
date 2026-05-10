from modules.avatar_motion_spine import MotionSource
from modules.avatar_performance_cues import (
    CueFamily,
    build_performance_packet,
    get_performance_cue,
    list_performance_cues,
)


def test_dance_packet_is_scripted_pose_packet():
    packet = build_performance_packet("dance_neon_sway", avatar_id="manny", now=100.0)
    data = packet.to_dict()
    assert data["avatar_id"] == "manny"
    assert data["source"] == MotionSource.SCRIPTED.value
    assert data["animation_name"] == "dance_neon_sway"
    assert data["metadata"]["cue_family"] == CueFamily.DANCE.value
    assert data["metadata"]["sprites_banned"] is True
    assert "spine" in data["bones"]


def test_desk_typing_carries_keyboard_prop_metadata():
    packet = build_performance_packet("type_at_desk_loop", avatar_id="manny", now=100.0)
    metadata = packet.to_dict()["metadata"]
    assert metadata["cue_family"] == CueFamily.ITEM.value
    assert metadata["prop"]["item_id"] == "keyboard"
    assert metadata["prop"]["target_anchor"] == "desk"


def test_social_and_etiquette_cues_exist():
    assert get_performance_cue("clap_applause").family == CueFamily.SOCIAL
    assert get_performance_cue("handshake_offer").family == CueFamily.SOCIAL
    assert get_performance_cue("bow_formal").family == CueFamily.ETIQUETTE
    assert get_performance_cue("curtsey_casual").family == CueFamily.ETIQUETTE
    assert get_performance_cue("curtsey_deep").family == CueFamily.ETIQUETTE


def test_environment_and_vehicle_cues_exist():
    for cue_name in ["walk_stairs_up", "walk_stairs_down", "use_ladder_climb", "open_door", "open_script_binder", "drive_hands_on_wheel", "drive_check_mirror"]:
        packet = build_performance_packet(cue_name, avatar_id="manny", now=100.0)
        assert packet.source == MotionSource.SCRIPTED
        assert packet.bones


def test_load_work_weight_classes_are_declared():
    expected = {
        "carry_light_one_hand": "light",
        "carry_medium_two_hand": "medium",
        "carry_heavy_strain": "heavy",
        "push_cart_light": "light",
        "push_heavy_object": "heavy",
        "pull_object_rope": "heavy",
    }
    for cue_name, weight_class in expected.items():
        packet = build_performance_packet(cue_name, avatar_id="manny", now=100.0)
        prop = packet.to_dict()["metadata"]["prop"]
        assert packet.to_dict()["metadata"]["cue_family"] == CueFamily.LOAD_WORK.value
        assert prop["weight_class"] == weight_class
        assert packet.bones


def test_list_performance_cues_filters_by_family():
    load_cues = list_performance_cues(CueFamily.LOAD_WORK)
    assert len(load_cues) >= 6
    assert all(cue.family == CueFamily.LOAD_WORK for cue in load_cues)
