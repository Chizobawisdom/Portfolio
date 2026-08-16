"""
Data logger for the OpenPLC OEE project.

Polls every coil and holding register on an interval, timestamps
each reading, and stores it in SQLite. This is the "historian"
side of the pipeline - it only ever reads, never writes.

Downtime is deliberately NOT computed inside the PLC (see project
notes) - it's derived here instead, from Machine_Faulted transitions
in the logged data. This script just logs raw state; the OEE
calculation happens as a separate analysis step on top of this table.

Run this in one terminal, and simulator.py in another.
"""

import sqlite3
import time
from datetime import datetime, timezone

from pymodbus.client import ModbusTcpClient

from address_map import PLC_HOST, PLC_PORT, COILS, HOLDING_REGISTERS

DB_PATH = "oee_data.db"
POLL_INTERVAL_SECONDS = 1.0

# Build the column list once: every coil + every holding register,
# in a stable order, used for both table creation and inserts.
COLUMNS = list(COILS.keys()) + list(HOLDING_REGISTERS.keys())


def init_db(conn):
    columns_sql = ", ".join(f'"{name}" INTEGER' for name in COLUMNS)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS readings (
            timestamp TEXT NOT NULL,
            {columns_sql}
        )
    """)
    conn.commit()


def poll_plc(client):
    """Read every coil and holding register. Returns a dict of
    name -> int value (0/1 for coils, raw value for registers),
    or None if the read failed."""
    values = {}

    for name, addr in COILS.items():
        result = client.read_coils(address=addr, count=1)
        if result.isError():
            print(f"  [logger] ERROR reading coil '{name}': {result}")
            return None
        values[name] = int(result.bits[0])

    for name, addr in HOLDING_REGISTERS.items():
        result = client.read_holding_registers(address=addr, count=1)
        if result.isError():
            print(f"  [logger] ERROR reading register '{name}': {result}")
            return None
        values[name] = result.registers[0]

    return values


def insert_reading(conn, values):
    timestamp = datetime.now(timezone.utc).isoformat()
    placeholders = ", ".join("?" for _ in COLUMNS)
    columns_sql = ", ".join(f'"{name}"' for name in COLUMNS)
    row = [values[name] for name in COLUMNS]

    conn.execute(
        f'INSERT INTO readings (timestamp, {columns_sql}) VALUES (?, {placeholders})',
        [timestamp] + row,
    )
    conn.commit()


def main():
    client = ModbusTcpClient(PLC_HOST, port=PLC_PORT)

    if not client.connect():
        print(f"FAILED to connect to {PLC_HOST}:{PLC_PORT}")
        return

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    print(f"Connected. Logging to {DB_PATH} every {POLL_INTERVAL_SECONDS}s...\n")
    print("Press Ctrl+C to stop.\n")

    row_count = 0
    try:
        while True:
            values = poll_plc(client)
            if values is not None:
                insert_reading(conn, values)
                row_count += 1
                if row_count % 10 == 0:
                    print(f"  [logger] {row_count} readings logged "
                          f"(Machine_Running={values['Machine_Running']}, "
                          f"Machine_Faulted={values['Machine_Faulted']}, "
                          f"Cycle_Count={values['Cycle_Count']})")

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print(f"\nStopping logger. {row_count} total readings logged.")
        client.close()
        conn.close()


if __name__ == "__main__":
    main()
