"""
Quick verification script for the OpenPLC Modbus TCP address map.

Run this AFTER:
  1. The Modbus_OEE server is enabled (port 502) on the Runtime
  2. The %QW buffer size has been set to 0 (so %MW starts at holding register 0)
  3. The PLC program is uploaded and RUNNING

What it does:
  - Writes True to coil 0 (Machine_Running), reads it back to confirm
  - Writes False back to leave things clean
  - Reads holding registers 0-2 (Cycle_Count, Good_Count, Reject_Count)

Install pymodbus first:
  pip install pymodbus --break-system-packages   (if on a managed/system Python)
  pip install pymodbus                            (otherwise)
"""

from pymodbus.client import ModbusTcpClient

PLC_HOST = "localhost"
PLC_PORT = 502

# Coil address map (from %QX byte.bit -> coil = byte*8 + bit)
COILS = {
    "Machine_Running": 0,
    "Machine_Faulted": 1,
    "Reject_Gate": 2,
    "Conveyor_Motor": 3,
    "Fill_Actuator": 4,
    "Fault_Lamp": 5,
    "Start_PB": 8,
    "Stop_PB": 9,
    "EStop_OK": 10,
    "Jam_Sensor": 11,
    "Part_Present": 12,
    "Reject_Sensor": 13,
    "Reset_PB": 14,
}

# Holding register map (%MW0-2, after setting %QW buffer to 0)
HOLDING_REGISTERS = {
    "Cycle_Count": 0,
    "Good_Count": 1,
    "Reject_Count": 2,
}


def main():
    client = ModbusTcpClient(PLC_HOST, port=PLC_PORT)

    if not client.connect():
        print(f"FAILED to connect to {PLC_HOST}:{PLC_PORT}")
        print("Check: is the Modbus server enabled? Is the PLC running?")
        return

    print(f"Connected to {PLC_HOST}:{PLC_PORT}\n")

    # --- Test 1: read all coils as-is ---
    print("--- Current coil states ---")
    for name, addr in COILS.items():
        result = client.read_coils(address=addr, count=1)
        if result.isError():
            print(f"  {name:<16} (coil {addr:>2}): ERROR reading - {result}")
        else:
            print(f"  {name:<16} (coil {addr:>2}): {result.bits[0]}")

    # --- Test 2: read holding registers as-is ---
    print("\n--- Current holding register values ---")
    for name, addr in HOLDING_REGISTERS.items():
        result = client.read_holding_registers(address=addr, count=1)
        if result.isError():
            print(f"  {name:<16} (reg {addr}): ERROR reading - {result}")
        else:
            print(f"  {name:<16} (reg {addr}): {result.registers[0]}")

    # --- Test 3: write/read round-trip on Machine_Running (coil 0) ---
    print("\n--- Write/read round-trip test on 'Machine_Running' (coil 0) ---")
    write_result = client.write_coil(address=0, value=True)
    if write_result.isError():
        print(f"  WRITE FAILED: {write_result}")
    else:
        print("  Wrote True to coil 0")

    read_back = client.read_coils(address=0, count=1)
    if read_back.isError():
        print(f"  READ-BACK FAILED: {read_back}")
    else:
        value = read_back.bits[0]
        status = "PASS" if value is True else "FAIL (expected True)"
        print(f"  Read back: {value}  -> {status}")

    # Clean up: set it back to False so you're not left with a running machine
    client.write_coil(address=0, value=False)
    print("  Reset coil 0 back to False")

    client.close()
    print("\nDone. If the round-trip test PASSED, your address map is confirmed correct.")
    print("Cross-check: open the Debugger panel in OpenPLC Editor and confirm")
    print("'main.Machine_Running' visibly toggled True then False during this run.")


if __name__ == "__main__":
    main()
