# Project: Digital Twin Simulation

Created a digital twin of a 3-station production process using simulation tools for quality control.

---

The Simulation Algorithm utilised here is as follows:
 - A raw part arrives and queues waiting availability at the cutting station (beginning of process)
 - The part gets processed at the cutting station. The part could:
     - wait in line if machine is busy
     - be cut once machine is free
     - wait due to machine breakdown
     - move to buffer before assembly once cut
  - The cut part waits in the buffer before Assembly
  - The part gets processed in assembly
     - The part enters queue for assembly
     - machine works on part unless machine is broken
     - if machine is broken, process pauses till its repaired
     - processed part moves to buffer before inspection
  - The part waits in buffer befor inspection
  - The part is inspected using quality checks
     - Inspection simulates real quality checks:
        - A true dimension is generated (process variation).
        - Measurement noise is added (gauge variation).
        - The final measurement is compared against specification limits.
            - Based on the measurement, the part is classified into one of three categories:
                a. PASS — the part is within specification.
                The part is accepted as good and leaves the system.
                b. REWORK — the part is slightly outside the specification.
                The part must go back to Assembly for rework.
                  It is placed again in the Assembly queue.
                  If it has been reworked too many times (rework limit), it becomes scrap instead.
                c. SCRAP — the part is far out of specification.
                The part is discarded and removed from the system.
 - Reworked parts loop through last 2 stations till either passes or rework limit
 - System is run till simlation ends

---

Relevant Manufacturing Metrics
  - Throughput: How many good parts leave the system per hour.
  - Yield: FPY (First Pass Yield) — passed inspection first time & RTY (Rolled Throughput Yield) — combined yield across stations
  - Scrap rate: How many parts end up scrapped.
  - Rework load: How many parts required additional Assembly cycles.
  - Bottleneck station: The station with the highest utilization.
  - OEE per station: Availability (based on MTBF/MTTR) , Performance (actual vs ideal cycle time) & Quality (good vs total parts)

---

