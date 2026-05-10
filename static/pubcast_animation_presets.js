// PubCast canonical animation presets
// Derived from the uploaded walk/sit/wave/type/idle preset file, expanded with
// emotional tags and runtime metadata so the Python/Rust motion spine can reason
// about intent before a GLB consumer renders the bones.

export const PUBCAST_ANIMATION_PRESETS = {
  idle_breathing: {
    duration: 4.0,
    loop: true,
    category: "idle",
    emotionTags: ["neutral", "warm"],
    bodyIntensity: 0.2,
    mocapOverrideAllowed: true,
    tracks: {
      chest: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 2, value: [0.03, 0, 0] }, { time: 4, value: [0, 0, 0] }] }
    }
  },
  walk_basic: {
    duration: 2.0,
    loop: true,
    category: "locomotion",
    emotionTags: ["neutral", "confident"],
    bodyIntensity: 0.65,
    mocapOverrideAllowed: true,
    requiresFootContact: true,
    tracks: {
      root: { position: [{ time: 0, value: [0, 0, 0] }, { time: 2, value: [0, 0, -2] }] },
      thigh_l: { rotation: [{ time: 0, value: [0.4, 0, 0] }, { time: 1, value: [-0.4, 0, 0] }, { time: 2, value: [0.4, 0, 0] }] },
      thigh_r: { rotation: [{ time: 0, value: [-0.4, 0, 0] }, { time: 1, value: [0.4, 0, 0] }, { time: 2, value: [-0.4, 0, 0] }] },
      upperarm_l: { rotation: [{ time: 0, value: [-0.3, 0, 0] }, { time: 1, value: [0.3, 0, 0] }, { time: 2, value: [-0.3, 0, 0] }] },
      upperarm_r: { rotation: [{ time: 0, value: [0.3, 0, 0] }, { time: 1, value: [-0.3, 0, 0] }, { time: 2, value: [0.3, 0, 0] }] }
    }
  },
  sit: {
    duration: 3.0,
    loop: false,
    category: "locomotion",
    emotionTags: ["neutral", "tired"],
    bodyIntensity: 0.35,
    mocapOverrideAllowed: true,
    tracks: {
      root: { position: [{ time: 0, value: [0, 0, 0] }, { time: 3, value: [0, -0.6, 0] }] },
      thigh_l: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 3, value: [1.57, 0, 0] }] },
      thigh_r: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 3, value: [1.57, 0, 0] }] },
      calf_l: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 3, value: [-1.57, 0, 0] }] },
      calf_r: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 3, value: [-1.57, 0, 0] }] }
    }
  },
  wave_hello: {
    duration: 2.0,
    loop: false,
    category: "gesture",
    emotionTags: ["warm", "playful"],
    bodyIntensity: 0.45,
    mocapOverrideAllowed: true,
    cooldownSeconds: 1.0,
    tracks: {
      upperarm_r: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 0.5, value: [0, 0, -1.57] }] },
      lowerarm_r: { rotation: [{ time: 0.5, value: [0, 0, 0] }, { time: 0.7, value: [0, 0.6, 0] }, { time: 0.9, value: [0, -0.6, 0] }, { time: 1.1, value: [0, 0.6, 0] }] }
    }
  },
  thinking_pose: {
    duration: 3.0,
    loop: true,
    category: "emotional",
    emotionTags: ["thinking", "curious"],
    bodyIntensity: 0.25,
    mocapOverrideAllowed: true,
    tracks: {
      head: { rotation: [{ time: 0, value: [0, 0, 0] }, { time: 1.5, value: [0.07, -0.08, 0] }, { time: 3, value: [0.07, -0.08, 0] }] },
      hand_r: { position: [{ time: 0, value: [0, 0, 0] }, { time: 1.5, value: [0.25, 1.2, 0.2] }] }
    }
  },
  safe_freeze_midshot: {
    duration: 1.0,
    loop: true,
    category: "safety",
    emotionTags: ["neutral"],
    bodyIntensity: 0.0,
    mocapOverrideAllowed: false,
    tracks: { root: { position: [{ time: 0, value: [0, 0, 0] }] } }
  }
};

export function getPubCastAnimationPreset(name) {
  return PUBCAST_ANIMATION_PRESETS[name] || null;
}
