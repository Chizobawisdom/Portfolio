"""
Streaming feature computation for the edge service.

Mirrors the rolling features built with pandas in the notebook:
mean and standard deviation (ddof=1, like pandas) of four sensors over the
last 3, 12 and 24 hourly readings -> 24 features per machine and hour.

Usage:
    buf = MachineBuffer()
    feats = buf.update({"volt": 170.1, "rotate": 440.2, "pressure": 99.8, "vibration": 41.0})
    # feats is None until 24 readings have arrived, then a dict of 24 features
"""
from collections import deque

import numpy as np

SENSORS = ["volt", "rotate", "pressure", "vibration"]
WINDOWS = [3, 12, 24]
MAX_WINDOW = max(WINDOWS)


class MachineBuffer:
    """Ring buffer holding the last 24 hourly readings of ONE machine."""

    def __init__(self):
        self.buf = deque(maxlen=MAX_WINDOW)

    def update(self, reading):
        """Add one hourly reading (dict with the four sensor values).

        Returns a dict {feature_name: value}, or None while fewer than
        24 readings are available (the notebook drops these rows too).
        """
        self.buf.append([reading[s] for s in SENSORS])
        if len(self.buf) < MAX_WINDOW:
            return None
        arr = np.asarray(self.buf, dtype=np.float64)
        feats = {}
        for w in WINDOWS:
            window = arr[-w:]
            mean = window.mean(axis=0)
            std = window.std(axis=0, ddof=1)
            for i, sensor in enumerate(SENSORS):
                feats[f"{sensor}_mean_{w}"] = mean[i]
                feats[f"{sensor}_std_{w}"] = std[i]
        return feats


def to_vector(feats, feature_names):
    """Order the feature dict exactly like the training columns (ONNX needs this order)."""
    return np.array([[feats[name] for name in feature_names]], dtype=np.float32)