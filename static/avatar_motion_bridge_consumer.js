// PubCast avatar motion bridge consumer
// Receives `pubcast.avatar.motion.v1` pose events and applies them to a GLB-like
// skeleton adapter. This file does not create sprites, canvases, or replacement
// avatars. It only moves named bones that already exist on the GLB skeleton.

export const PUBCAST_AVATAR_MOTION_PROTOCOL = "pubcast.avatar.motion.v1";

function normalizeQuaternion(rotation) {
  if (!Array.isArray(rotation) || rotation.length !== 4) return [0, 0, 0, 1];
  const [x, y, z, w] = rotation.map(Number);
  const length = Math.hypot(x, y, z, w) || 1;
  return [x / length, y / length, z / length, w / length];
}

function normalizeVec3(value, fallback = [0, 0, 0]) {
  if (!Array.isArray(value) || value.length !== 3) return fallback.slice();
  return value.map(Number);
}

export class PubCastAvatarMotionConsumer {
  constructor({ skeletonAdapter = null, logger = console } = {}) {
    this.skeletonAdapter = skeletonAdapter;
    this.logger = logger;
    this.lastPoseByAvatar = new Map();
    this.appliedPoseCount = 0;
  }

  setSkeletonAdapter(adapter) {
    this.skeletonAdapter = adapter;
  }

  consume(rawEvent) {
    const event = typeof rawEvent === "string" ? JSON.parse(rawEvent) : rawEvent;
    this.validateEvent(event);
    const pose = event.pose;
    const appliedBones = this.applyPose(pose);
    this.lastPoseByAvatar.set(event.avatar_id, pose);
    this.appliedPoseCount += 1;
    return {
      avatarId: event.avatar_id,
      animationName: pose.animation_name,
      source: pose.source,
      appliedBones,
      confidence: pose.confidence
    };
  }

  validateEvent(event) {
    if (!event || typeof event !== "object") throw new Error("Avatar motion event must be an object");
    if (event.protocol !== PUBCAST_AVATAR_MOTION_PROTOCOL) {
      throw new Error(`Unsupported avatar motion protocol: ${event.protocol}`);
    }
    if (event.event_type !== "avatar_pose") throw new Error(`Unsupported event type: ${event.event_type}`);
    if (!event.pose || typeof event.pose !== "object") throw new Error("Avatar motion event is missing pose");
    if (!event.pose.bones || typeof event.pose.bones !== "object") throw new Error("Pose is missing bones");
  }

  applyPose(pose) {
    if (!this.skeletonAdapter) throw new Error("No skeleton adapter attached to PubCastAvatarMotionConsumer");
    let applied = 0;
    for (const [boneName, transform] of Object.entries(pose.bones)) {
      const bone = this.resolveBone(boneName);
      if (!bone) {
        this.logger?.warn?.(`PubCast motion consumer: missing GLB bone '${boneName}'`);
        continue;
      }
      this.applyBoneTransform(bone, transform);
      applied += 1;
    }
    this.skeletonAdapter.updateMatrixWorld?.(true);
    return applied;
  }

  resolveBone(boneName) {
    if (typeof this.skeletonAdapter.getBone === "function") return this.skeletonAdapter.getBone(boneName);
    if (typeof this.skeletonAdapter.getObjectByName === "function") return this.skeletonAdapter.getObjectByName(boneName);
    if (this.skeletonAdapter.bones && Object.prototype.hasOwnProperty.call(this.skeletonAdapter.bones, boneName)) {
      return this.skeletonAdapter.bones[boneName];
    }
    return null;
  }

  applyBoneTransform(bone, transform) {
    const position = normalizeVec3(transform.position, [0, 0, 0]);
    const rotation = normalizeQuaternion(transform.rotation);
    const scale = normalizeVec3(transform.scale, [1, 1, 1]);

    if (bone.position?.set) bone.position.set(position[0], position[1], position[2]);
    else bone.position = position;

    if (bone.quaternion?.set) bone.quaternion.set(rotation[0], rotation[1], rotation[2], rotation[3]);
    else bone.quaternion = rotation;

    if (bone.scale?.set) bone.scale.set(scale[0], scale[1], scale[2]);
    else bone.scale = scale;
  }
}

export function createPubCastMotionWebSocket({ url, consumer, onStatus = () => {} }) {
  const socket = new WebSocket(url);
  socket.addEventListener("open", () => onStatus({ state: "open" }));
  socket.addEventListener("close", () => onStatus({ state: "closed" }));
  socket.addEventListener("error", (error) => onStatus({ state: "error", error }));
  socket.addEventListener("message", (message) => {
    try {
      const result = consumer.consume(message.data);
      onStatus({ state: "pose_applied", result });
    } catch (error) {
      onStatus({ state: "pose_error", error });
    }
  });
  return socket;
}
