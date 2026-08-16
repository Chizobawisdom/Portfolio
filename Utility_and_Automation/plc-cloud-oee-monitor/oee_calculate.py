"""
OEE calculation for the OpenPLC OEE project.

Reads the readings table logged by logger.py and computes:
  - Availability : (run time) / (total elapsed time)
  - Performance   : (actual cycles) / (ideal cycles possible in run time)
  - Quality       : good parts / total parts
  - OEE           : Availability x Performance x Quality

Downtime is derived here, not in the PLC (see project notes) - it's
found by scanning Machine_Faulted for 0->1 / 1->0 transitions in the
timestamped log and summing the durations between them.

Usage:
  python3 oee_calculate.py
  python3 oee_calculate.py --db oee_data.db --ideal-cycle-time 2.0
"""

import argparse
import sqlite3
from datetime import datetime


def parse_ts(ts_string):
    return datetime.fromisoformat(ts_string)


def load_readings(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT timestamp, Machine_Faulted, Cycle_Count, Good_Count, Reject_Count "
        "FROM readings ORDER BY timestamp ASC"
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No readings found in {db_path}. Run logger.py first.")

    return [
        {
            "timestamp": parse_ts(ts),
            "faulted": bool(faulted),
            "cycle_count": cycle_count,
            "good_count": good_count,
            "reject_count": reject_count,
        }
        for ts, faulted, cycle_count, good_count, reject_count in rows
    ]


def compute_downtime_seconds(readings):
    """Scan for Machine_Faulted 0->1 / 1->0 transitions and sum the
    duration of each fault episode. If the log ends mid-fault, that
    open episode is closed at the last timestamp."""
    total_downtime = 0.0
    fault_start = None

    for reading in readings:
        if reading["faulted"] and fault_start is None:
            fault_start = reading["timestamp"]
        elif not reading["faulted"] and fault_start is not None:
            total_downtime += (reading["timestamp"] - fault_start).total_seconds()
            fault_start = None

    # Log ended while still faulted - close out the open episode.
    if fault_start is not None:
        total_downtime += (readings[-1]["timestamp"] - fault_start).total_seconds()

    return total_downtime


def compute_oee(readings, ideal_cycle_time_seconds):
    first_ts = readings[0]["timestamp"]
    last_ts = readings[-1]["timestamp"]
    total_elapsed = (last_ts - first_ts).total_seconds()

    downtime = compute_downtime_seconds(readings)
    run_time = total_elapsed - downtime

    # Counters only ever increase, so the final reading holds the totals.
    final = readings[-1]
    cycle_count = final["cycle_count"]
    good_count = final["good_count"]
    reject_count = final["reject_count"]

    availability = (run_time / total_elapsed) if total_elapsed > 0 else 0.0

    ideal_cycles_possible = (run_time / ideal_cycle_time_seconds) if run_time > 0 else 0.0
    performance = (cycle_count / ideal_cycles_possible) if ideal_cycles_possible > 0 else 0.0

    quality = (good_count / cycle_count) if cycle_count > 0 else 0.0

    oee = availability * performance * quality

    return {
        "total_elapsed_s": total_elapsed,
        "downtime_s": downtime,
        "run_time_s": run_time,
        "cycle_count": cycle_count,
        "good_count": good_count,
        "reject_count": reject_count,
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": oee,
    }


def print_report(result, ideal_cycle_time_seconds):
    print("=" * 50)
    print("OEE REPORT")
    print("=" * 50)
    print(f"  Total elapsed time : {result['total_elapsed_s']:.1f} s")
    print(f"  Downtime           : {result['downtime_s']:.1f} s")
    print(f"  Run time           : {result['run_time_s']:.1f} s")
    print(f"  Ideal cycle time   : {ideal_cycle_time_seconds:.1f} s/part (assumed)")
    print()
    print(f"  Total parts        : {result['cycle_count']}")
    print(f"  Good parts         : {result['good_count']}")
    print(f"  Reject parts       : {result['reject_count']}")
    print("-" * 50)
    print(f"  Availability       : {result['availability']*100:5.1f}%")
    print(f"  Performance        : {result['performance']*100:5.1f}%")
    print(f"  Quality            : {result['quality']*100:5.1f}%")
    print("-" * 50)
    print(f"  OEE                : {result['oee']*100:5.1f}%")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Compute OEE from logged PLC data.")
    parser.add_argument("--db", default="oee_data.db", help="Path to the SQLite database")
    parser.add_argument(
        "--ideal-cycle-time",
        type=float,
        default=2.0,
        help="Assumed ideal seconds per part, used for Performance (default: 2.0)",
    )
    args = parser.parse_args()

    readings = load_readings(args.db)
    result = compute_oee(readings, args.ideal_cycle_time)
    print_report(result, args.ideal_cycle_time)


if __name__ == "__main__":
    main()
