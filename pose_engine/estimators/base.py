from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PoseResult:
    """Single-frame pose estimation result."""

    landmarks_3d: np.ndarray
    landmarks_2d: np.ndarray
    timestamp_ms: int
    estimator_name: str
    avg_confidence: float
    raw_output: dict[str, Any] | None = None


class BasePoseEstimator(ABC):
    """Interface every pose estimator must implement."""

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def estimate(self, frame: np.ndarray) -> PoseResult | None:
        ...

    @abstractmethod
    def estimate_batch(self, frames: list[np.ndarray]) -> list[PoseResult | None]:
        ...

    @abstractmethod
    def release(self) -> None:
        ...

    @property
    @abstractmethod
    def joint_names(self) -> list[str]:
        ...

    @property
    @abstractmethod
    def num_joints(self) -> int:
        ...
