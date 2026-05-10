"""PubCast avatar motion bridge.

Turns AvatarMotionRouter output into transport-safe events for a browser GLB
consumer. This is intentionally transport-agnostic: FastAPI/WebSocket, local
IPC, or a test harness can all call `build_motion_event` and send the result.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Optional
import json
import time

from .avatar_motion_spine import AvatarContext, AvatarMotionRouter, MotionIntent, PosePacket


BRIDGE_PROTOCOL = "pubcast.avatar.motion.v1"


@dataclass(frozen=True)
class AvatarMotionEvent:
    """Wire-format event for browser/runtime consumers."""

    protocol: str
    event_type: str
    avatar_id: str
    timestamp: float
    pose: Mapping[str, Any]
    transport_metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol": self.protocol,
            "event_type": self.event_type,
            "avatar_id": self.avatar_id,
            "timestamp": self.timestamp,
            "pose": dict(self.pose),
            "transport_metadata": dict(self.transport_metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)


class AvatarMotionBridge:
    """Small adapter between motion authority and renderer transport."""

    def __init__(self, router: Optional[AvatarMotionRouter] = None) -> None:
        self.router = router or AvatarMotionRouter()

    def build_motion_event(
        self,
        context: AvatarContext,
        intents: Iterable[MotionIntent],
        *,
        now: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> AvatarMotionEvent:
        pose_packet: PosePacket = self.router.route(context, intents, now=now)
        event_time = time.time() if now is None else now
        return AvatarMotionEvent(
            protocol=BRIDGE_PROTOCOL,
            event_type="avatar_pose",
            avatar_id=context.avatar_id,
            timestamp=event_time,
            pose=pose_packet.to_dict(),
            transport_metadata=metadata or {},
        )

    def build_motion_json(
        self,
        context: AvatarContext,
        intents: Iterable[MotionIntent],
        *,
        now: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return self.build_motion_event(context, intents, now=now, metadata=metadata).to_json()


def build_ws_payload(context: AvatarContext, intents: Iterable[MotionIntent], *, now: Optional[float] = None) -> str:
    """Convenience function for WebSocket routes and smoke tests."""

    return AvatarMotionBridge().build_motion_json(context, intents, now=now, metadata={"transport": "websocket"})
