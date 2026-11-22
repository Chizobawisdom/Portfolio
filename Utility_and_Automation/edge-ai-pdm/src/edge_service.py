"""
Edge monitoring service (replay mode).

Replays hourly machine telemetry reading by reading, as a live system would:

    reading -> per-machine ring buffer -> 24 rolling features -> ONNX model
            -> probability of failure within 48 h -> threshold + cooldown -> event

Events are appended to a JSON-lines file. Later, the emit step can be replaced
by an SAP notification client without touching the detection logic.

Run from the project root (edge-ai-pdm/):
    python -m src.edge_service --start 2015-09-01 --threshold 0.3
"""
import argparse
import json
import time
from pathlib import Path

import onnxruntime as ort
import pandas as pd

from src.features import MAX_WINDOW, SENSORS, MachineBuffer, to_vector

COOLDOWN_HOURS = 48  # after an alert, the same machine stays quiet for 48 h


class Detector:
    """Holds the model, one ring buffer per machine and the cooldown state."""

    def __init__(self, model_path, feature_names, threshold, cooldown_hours=COOLDOWN_HOURS):
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.feature_names = feature_names
        self.threshold = threshold
        self.cooldown = pd.Timedelta(hours=cooldown_hours)
        self.buffers = {}      # machineID -> MachineBuffer
        self.last_alert = {}   # machineID -> timestamp of the last alert

    def process(self, machine_id, timestamp, reading):
        """Handle one hourly reading. Returns an event dict if an alert fires, else None."""
        buffer = self.buffers.setdefault(machine_id, MachineBuffer())
        feats = buffer.update(reading)
        if feats is None:  # fewer than 24 readings so far
            return None
        x = to_vector(feats, self.feature_names)
        probability = float(self.session.run(None, {self.input_name: x})[1][0, 1])
        last = self.last_alert.get(machine_id)
        in_cooldown = last is not None and (timestamp - last) < self.cooldown
        if probability > self.threshold and not in_cooldown:
            self.last_alert[machine_id] = timestamp
            return {
                "machineID": int(machine_id),
                "timestamp": str(timestamp),
                "failure_probability": round(probability, 4),
                "threshold": self.threshold,
                "horizon_hours": 48,
            }
        return None


def replay(args):
    feature_names = json.loads(Path(args.features).read_text())
    detector = Detector(args.model, feature_names, args.threshold)

    tel = pd.read_csv(args.telemetry, parse_dates=["datetime"])
    start = pd.Timestamp(args.start)
    # Feed the 23 hours before `start` too, so the first features at `start` are available
    tel = tel[tel["datetime"] >= start - pd.Timedelta(hours=MAX_WINDOW - 1)]
    tel = tel.sort_values(["datetime", "machineID"])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_readings, n_events, total_seconds = 0, 0, 0.0
    with out_path.open("w") as out:
        for row in tel.itertuples(index=False):
            reading = {s: getattr(row, s) for s in SENSORS}
            t0 = time.perf_counter()
            event = detector.process(row.machineID, row.datetime, reading)
            total_seconds += time.perf_counter() - t0
            n_readings += 1
            # Events before `start` are only warm-up and are not reported
            if event is not None and row.datetime >= start:
                out.write(json.dumps(event) + "\n")
                n_events += 1

    print(f"readings processed: {n_readings}")
    print(f"alert events written to {out_path}: {n_events}")
    print(f"mean time per reading (features + model + logic): {1000 * total_seconds / n_readings:.3f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edge monitoring service (replay mode)")
    parser.add_argument("--telemetry", default="data/PdM_telemetry.csv")
    parser.add_argument("--model", default="models/pdm_logreg.onnx")
    parser.add_argument("--features", default="models/feature_names.json")
    parser.add_argument("--threshold", type=float, default=0.3)
    parser.add_argument("--start", default="2015-09-01", help="first timestamp to report events for")
    parser.add_argument("--out", default="output/events.jsonl")
    replay(parser.parse_args())