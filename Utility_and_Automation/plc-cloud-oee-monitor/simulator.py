"""
Process simulator for the OpenPLC OEE project.

Stands in for the physical machine's sensors and pushbuttons.
Drives the "input-style" coils over Modbus so the PLC has
something realistic to react to, since there's no real hardware.

Behavior:
  - Confirms e-stop healthy, clears the initial fault, starts the machine
  - Feeds parts through at a random interval, occasionally rejected
  - Occasionally simulates a jam, holds it, then clears and resets
  - Runs until Ctrl+C, then stops the machine cleanly

Run this in one terminal, and logger.py in another.
"""

import random
import time

from pymodbus.client import ModbusTcpClient

from address_map import PLC_HOST, PLC_PORT, COILS

# --- tunables ---
PART_INTERVAL_RANGE = (2, 5)      # seconds between parts
REJECT_PROBABILITY = 0.15         # 15% of parts are rejected
JAM_PROBABILITY = 0.05            # 5% chance of a jam after any given part
JAM_DURATION_RANGE = (4, 10)      # seconds a jam lasts before clearing


def write_coil(client, name, value):
    client.write_coil(address=COILS[name], value=value)


def pulse_coil(client, name, hold_seconds=0.2):
    """Set a coil True, wait briefly, then set it False - used for
    momentary pushbuttons and edge-triggered signals."""
    write_coil(client, name, True)
    time.sleep(hold_seconds)
    write_coil(client, name, False)


def handle_jam(client):
    print("  [simulator] JAM triggered")
    write_coil(client, "Jam_Sensor", True)
    time.sleep(random.uniform(*JAM_DURATION_RANGE))
    write_coil(client, "Jam_Sensor", False)
    print("  [simulator] jam cleared, resetting fault")
    time.sleep(0.3)
    pulse_coil(client, "Reset_PB")


def run_part_cycle(client):
    is_reject = random.random() < REJECT_PROBABILITY
    write_coil(client, "Reject_Sensor", is_reject)
    pulse_coil(client, "Part_Present")
    outcome = "REJECT" if is_reject else "good"
    print(f"  [simulator] part processed -> {outcome}")

    if random.random() < JAM_PROBABILITY:
        handle_jam(client)


def main():
    client = ModbusTcpClient(PLC_HOST, port=PLC_PORT)

    if not client.connect():
        print(f"FAILED to connect to {PLC_HOST}:{PLC_PORT}")
        return

    print("Connected. Starting simulator...\n")

    # Startup sequence: confirm e-stop healthy, clear the initial
    # fault, then start the machine.
    write_coil(client, "EStop_OK", True)
    time.sleep(0.3)
    pulse_coil(client, "Reset_PB")
    time.sleep(0.3)
    pulse_coil(client, "Start_PB")
    print("Machine started.\n")

    try:
        while True:
            time.sleep(random.uniform(*PART_INTERVAL_RANGE))
            run_part_cycle(client)

    except KeyboardInterrupt:
        print("\nStopping simulator...")
        pulse_coil(client, "Stop_PB")
        client.close()
        print("Simulator stopped, connection closed.")


if __name__ == "__main__":
    main()
