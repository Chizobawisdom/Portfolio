# Simulating a 3 station Quality Control Line with a Digital Twin
# Each station has a different processing time and a different probability of failure
import random
import time
import statistics
import csv
import simpy


# GLOBAL SIMULATION PARAMETERS
SHIFT_MIN = 8 * 60          # total simulated minutes (8h shift)
WARMUP_MIN = 30             # ignore initial transients
INTER_ARRIVAL = 1.0         # part arrival rate (1 part/min)

REWORK_LIMIT = 1            # maximum rework cycles allowed

# Define the processing times and failure probabilities for each station
# STATION CONFIGURATION
# Each station has: CT mean, CT std, MTBF, MTTR, capaci

STATIONS = {
    "Cutting": {
        "ct_mean": 0.8, "ct_sd": 0.1,
        "mtbf": 200, "mttr": 5,
        "capacity": 1
    },
    "Assembly": {
        "ct_mean": 1.2, "ct_sd": 0.15,
        "mtbf": 150, "mttr": 8,
        "capacity": 1
    },
    "Inspection": {
        "ct_mean": 0.6, "ct_sd": 0.05,
        "mtbf": 9999, "mttr": 0,   # No breakdown for inspection
        "capacity": 1
 
    }
}    

# QUALITY / INSPECTION CONFIG
TRUE_MEAN = 10.0           # process centering
PROC_SIGMA = 0.05          # natural process variation
GAUGE_SIGMA = 0.01         # measurement noise
LSL, USL = 9.9, 10.1       # spec limits

# DATA COLLECTION STRUCTURES
RESOURCES = {}
DOWN = {}                  # machine DOWN state
UTIL_TIME = {}             # busy time per station
QUEUES = {}                # queue length samples

inspection_log = []        # CSV save
cycle_times = []           # final CTs
good_parts = 0
scrap_parts = 0
rework_parts = 0
part_counter = 0           # incremental ID

# SUPPORTING FUNCTIONS
def breakdown_process(env, station_name):
    """
    Simulates random breakdowns for each machine
    using exponential time distribution (MTBF / MTTR).
    Runs continuously throughout the simulation.
    """
    mtbf = STATIONS[station_name]["mtbf"]
    mttr = STATIONS[station_name]["mttr"]

    if mtbf >= 9999:
        return  # Station never breaks down

    while True:
        # Wait until next failure
        time_to_failure = random.expovariate(1.0 / mtbf)
        yield env.timeout(time_to_failure)

        DOWN[station_name] = True
        # Repair time
        yield env.timeout(mttr)
        DOWN[station_name] = False



def process_at_station(env, part, station_name):
    """
    Handles queueing, waiting, processing, and downtime interruptions.
    """
    resource = RESOURCES[station_name]
    ct_mean = STATIONS[station_name]["ct_mean"]
    ct_sd = STATIONS[station_name]["ct_sd"]

    # Record queue length for bottleneck detection
    QUEUES[station_name].append(len(resource.queue))

    # Request the machine
    with resource.request() as req:
        yield req

        # Wait if machine is DOWN
        while DOWN[station_name]:
            yield env.timeout(0.1)

        # Begin processing
        start = env.now
        ct = max(0.01, random.gauss(ct_mean, ct_sd))
        remaining = ct

        # If breakdown occurs mid-process → pause
        while remaining > 0:
            if DOWN[station_name]:
                yield env.timeout(0.1)
            else:
                step = min(0.1, remaining)
                yield env.timeout(step)
                remaining -= step

        end = env.now

        # Track utilization
        UTIL_TIME[station_name] += (end - start)

        # Save timestamps
        part["history"].append((station_name, start, end))

def inspect_and_classify(part):
    """
    Performs a noisy measurement and classifies the outcome:
    PASS, REWORK, or SCRAP.
    """
    global good_parts, scrap_parts, rework_parts

    true_value = random.gauss(TRUE_MEAN, PROC_SIGMA)
    measured = random.gauss(true_value, GAUGE_SIGMA)

    # Log measurement
    inspection_log.append({
        "part_id": part["id"],
        "time": part["birth"],
        "measurement": measured
    })

    # Classification
    if measured < LSL - 0.02 or measured > USL + 0.02:
        scrap_parts += 1
        return "SCRAP"

    if measured < LSL or measured > USL:
        rework_parts += 1
        return "REWORK"

    good_parts += 1
    return "PASS"

#                           PART FLOW LOGIC
def part_flow(env):
    """
    Handles arrivals + routing parts through Cutting → Assembly → Inspection.
    Includes REWORK loop.
    """
    global part_counter

    while True:
        # Generate new part arrival
        part_counter += 1
        part = {
            "id": part_counter,
            "birth": env.now,
            "reworks": 0,
            "history": []
        }

        # Cutting
        yield from process_at_station(env, part, "Cutting")

        # Assembly
        yield from process_at_station(env, part, "Assembly")

        # Inspection + QC loop
        while True:
            yield from process_at_station(env, part, "Inspection")
            outcome = inspect_and_classify(part)

            if outcome == "PASS":
                # record cycle time
                if env.now >= WARMUP_MIN:
                    cycle_times.append(env.now - part["birth"])
                break

            elif outcome == "SCRAP":
                break

            elif outcome == "REWORK":
                if part["reworks"] >= REWORK_LIMIT:
                    scrap_parts += 1
                    break
                part["reworks"] += 1
                # Re-enter Assembly
                yield from process_at_station(env, part, "Assembly")

        # Inter-arrival time before next part
        ia = random.expovariate(1.0 / INTER_ARRIVAL)
        yield env.timeout(ia)

#                           SIMULATION RUNNER
def run_simulation():
    """
    Main function:
    - Initializes environment
    - Creates resources
    - Starts breakdown processes
    - Starts part flow
    - Runs simulation
    - Prints KPIs
    - Saves CSV output
    """
    global RESOURCES, DOWN, UTIL_TIME, QUEUES
    env = simpy.Environment()

    # Initialize stations
    for station in STATIONS:
        RESOURCES[station] = simpy.Resource(env, capacity=STATIONS[station]["capacity"])
        DOWN[station] = False
        UTIL_TIME[station] = 0
        QUEUES[station] = []

        # Start breakdown process
        env.process(breakdown_process(env, station))

    # Start part arrival / processing
    env.process(part_flow(env))

    # Run simulation
    env.run(until=SHIFT_MIN)

    # KPI CALCULATIONS
    total = good_parts + scrap_parts
    throughput = good_parts / ((SHIFT_MIN - WARMUP_MIN) / 60)
    fpy = good_parts / total if total else 0
    scrap_rate = scrap_parts / total if total else 0

    util = {s: UTIL_TIME[s] / (SHIFT_MIN - WARMUP_MIN) for s in STATIONS}
    bottleneck = max(util, key=util.get)

    # OEE approximation
    oee = {}
    for s in STATIONS:
        mtbf = STATIONS[s]["mtbf"]
        mttr = STATIONS[s]["mttr"]
        if mtbf >= 9999:
            availability = 1.0
        else:
            availability = mtbf / (mtbf + mttr)

        ideal_ct = STATIONS[s]["ct_mean"] * 0.95
        performance = STATIONS[s]["ct_mean"] / ideal_ct
        quality = good_parts / total if total else 0

        oee[s] = availability * performance * quality

    # Print KPI Summary
    print("\n============== SIMULATION SUMMARY ==============")
    print(f"Good parts: {good_parts}")
    print(f"Scrap parts: {scrap_parts}")
    print(f"Rework attempts: {rework_parts}")
    print(f"Total processed: {total}")
    print(f"Throughput (good/hr): {throughput:.2f}")
    print(f"FPY: {fpy:.3f}  |  Scrap rate: {scrap_rate:.3f}")
    print("Utilization by station:")
    for s in STATIONS:
        print(f" - {s}: {util[s]*100:.1f}%  |  OEE: {oee[s]*100:.1f}%")
    print(f"Bottleneck station: {bottleneck}")

    # Save inspection CSV
    with open("inspection_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["part_id", "time", "measurement"])
        writer.writeheader()
        writer.writerows(inspection_log)

    print("Saved inspection data → inspection_data.csv")
    print("================================================\n")

#                           RUN MAIN PROGRAM
if __name__ == "__main__":
    run_simulation()