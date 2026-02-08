from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from pose_engine.estimators.base import BasePoseEstimator, PoseResult


@dataclass
class FrameAnalysis:
    pose: PoseResult | None
    messages: list[str]
    timestamp_ms: int


class PosePipeline:
    """Minimal pipeline skeleton for frame-by-frame processing."""

    def __init__(self, estimator: BasePoseEstimator, config: dict[str, Any]):
        self.estimator = estimator
        self.config = config
        self.started = False

    def start(self) -> None:
        self.estimator.initialize(self.config.get("estimator", {}))
        self.started = True

    def process_frame(self, frame: np.ndarray, timestamp_ms: int) -> FrameAnalysis:
        if not self.started:
            raise RuntimeError("Pipeline not started")
        pose = self.estimator.estimate(frame)
        if pose is None:
            return FrameAnalysis(
                pose=None,
                messages=["포즈를 감지할 수 없습니다. 카메라 앞에 서주세요."],
                timestamp_ms=timestamp_ms,
            )
        return FrameAnalysis(pose=pose, messages=[], timestamp_ms=timestamp_ms)

    def stop(self) -> None:
        self.estimator.release()
        self.started = False
