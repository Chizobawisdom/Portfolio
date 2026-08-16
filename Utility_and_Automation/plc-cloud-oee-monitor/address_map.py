"""
Shared Modbus TCP address map for the OpenPLC OEE project.
Imported by both simulator.py and logger.py so the two scripts
can never drift out of sync with each other.

Verified against the running PLC via modbus_verify.py.
"""

PLC_HOST = "localhost"
PLC_PORT = 502

# Coils (%QX byte.bit -> coil = byte*8 + bit)
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

# Holding registers (%MW0-2, after setting the %QW buffer to 0)
HOLDING_REGISTERS = {
    "Cycle_Count": 0,
    "Good_Count": 1,
    "Reject_Count": 2,
}

# Convenience: which coils the simulator is allowed to drive
# (the "world" side) vs. which ones are PLC-owned outputs the
# simulator should only ever read.
SIMULATOR_WRITABLE = [
    "Start_PB",
    "Stop_PB",
    "EStop_OK",
    "Jam_Sensor",
    "Part_Present",
    "Reject_Sensor",
    "Reset_PB",
]

PLC_OWNED = [
    "Machine_Running",
    "Machine_Faulted",
    "Reject_Gate",
    "Conveyor_Motor",
    "Fill_Actuator",
    "Fault_Lamp",
]
