import assert from 'node:assert/strict';
import { PubCastAvatarMotionConsumer, PUBCAST_AVATAR_MOTION_PROTOCOL } from '../static/avatar_motion_bridge_consumer.js';

function makeBone() {
  return {
    position: { value: null, set(x, y, z) { this.value = [x, y, z]; } },
    quaternion: { value: null, set(x, y, z, w) { this.value = [x, y, z, w]; } },
    scale: { value: null, set(x, y, z) { this.value = [x, y, z]; } }
  };
}

const head = makeBone();
const chest = makeBone();
const skeletonAdapter = {
  bones: { head, chest },
  updateCalled: false,
  updateMatrixWorld(force) { this.updateCalled = force; }
};

const consumer = new PubCastAvatarMotionConsumer({ skeletonAdapter, logger: { warn() {} } });
const result = consumer.consume({
  protocol: PUBCAST_AVATAR_MOTION_PROTOCOL,
  event_type: 'avatar_pose',
  avatar_id: 'manny',
  timestamp: 100,
  pose: {
    avatar_id: 'manny',
    skeleton_id: 'pubcast_authoritative_humanoid_v1',
    timestamp: 100,
    source: 'mocap',
    animation_name: 'direct_pose',
    bones: {
      head: { position: [0, 1, 0], rotation: [0.1, 0, 0, 0.995], scale: [1, 1, 1] },
      chest: { position: [0, 0, 0], rotation: [0, 0, 0, 1], scale: [1, 1, 1] }
    },
    confidence: 0.9
  }
});

assert.equal(result.avatarId, 'manny');
assert.equal(result.appliedBones, 2);
assert.deepEqual(head.position.value, [0, 1, 0]);
assert.equal(Math.round(head.quaternion.value[3] * 1000) / 1000, 0.995);
assert.equal(skeletonAdapter.updateCalled, true);
assert.equal(consumer.appliedPoseCount, 1);
console.log('avatar motion bridge consumer test passed');
