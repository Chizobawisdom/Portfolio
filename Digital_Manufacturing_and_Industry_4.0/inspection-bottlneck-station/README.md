================================================================================
INDUSTRIAL QUALITY GATE CAPACITY OPTIMIZATION STUDY
================================================================================
Simulation Environment: AnyLogic 8.9 (Process Modeling Library)
Programming Language:   Java
Core Paradigm:          Discrete Event Simulation (DES)
================================================================================

1. PROJECT OVERVIEW
--------------------------------------------------------------------------------
In high-volume manufacturing environments (such as quality gates at industrial 
suppliers like ZF or Mubea), manual inspection stations frequently experience 
severe bottlenecking. This occurs due to the intersection of stochastic part 
arrivals and inherent variability in manual testing cycle times. 

This study leverages an operational discrete event simulation model to evaluate, 
stress-test, and quantify two contrasting capital/operational strategies against 
a baseline configuration:

  * Baseline Case: Maintain the current single-inspector arrangement.
  * Scenario A (Add Headcount): Staff a second inspector in parallel.
  * Scenario B (Add Capability): Upgrade advanced testing apparatus to reduce 
    raw inspection times by approximately 20%.


2. SYSTEM DEFINITION & BOUNDARIES
--------------------------------------------------------------------------------
* Inside Model:  Stochastic part arrivals, physical queueing/buffering, manual 
                 testing processes, and binary pass/scrap entity routing.
* Outside Model: Upstream fabrication/machining dynamics, material handling 
                 transit times, and downstream packaging/logistics networks.
* Shift Horizon: 8-Hour operational shift (480 minutes).
* Base Unit:     Minutes.
* Spatial Scope: Non-spatial. Logic-driven process flow topology.


3. INPUT PARAMETERS & STOCHASTIC DISTRIBUTIONS
--------------------------------------------------------------------------------
* Part Interarrival Time: Exponential distribution with a mean of 5.0 minutes 
                          (Arrival Rate lambda = 0.2 parts/minute).
* Baseline Inspection:    Triangular(Min = 2.0, Mode = 4.0, Max = 7.0) minutes.
* Scenario B Inspection:  Triangular(Min = 1.6, Mode = 3.2, Max = 5.6) minutes 
                          (Scaled down uniformly by 20%).
* Defect Generation:      Bernoulli distribution with a true defect 
                          probability of p = 0.08 (8% constant defect rate).


4. PROCESS FLOW TOPOLOGY
--------------------------------------------------------------------------------
The process architecture is mapped linearly inside AnyLogic as follows:

Source -> TimeMeasureStart -> Queue -> Service (Seize/Release ResourcePool)
       -> SelectOutput -> [Two TimeMeasureEnd Blocks] -> Sinks (Pass / Scrap)


5. EXPERIMENTAL FRAMEWORK & STATISTICAL PLAN
--------------------------------------------------------------------------------
To mitigate initialization bias and evaluate stochastic variations, experiments 
were managed through an AnyLogic Parameter Variation layout:
* Multi-Run Setup:   10 Independent replications executed per scenario configuration.
* Random Seed Sets:  Unique, randomized seed vectors utilized for each run.
* Data Aggregation: Automated callback statistics collected into custom datasets 
                     to calculate the Sample Mean +/- 95% Confidence Interval (CI).


6. KEY RESULTS & PERFORMANCE DATA
--------------------------------------------------------------------------------
All metrics below indicate the [Sample Mean] +/- [95% Confidence Interval]:
N/B: Due to random seed, metrics are relevantly randomized when running the model

| Metric                  | Baseline             | Scenario A           | Scenario B           |
|-------------------------|----------------------|----------------------|----------------------|
| Inspector Utilization   | 0.814 +/- 0.048      | 0.408 +/- 0.041      | 0.756 +/- 0.047      |
| Cycle Time (minutes)    | 16.02 +/- 7.84       | 4.65 +/- 0.17        | 9.73 +/- 2.25        |
| Throughput (parts/hr)   | 11.31 +/- 0.63       | 11.35 +/- 1.02       | 11.13 +/- 0.71       |
| Scrap Rate              | 0.067 +/- 0.015      | 0.081 +/- 0.019      | 0.086 +/- 0.023      |

Key Quantitative Insights:
1. Volatility near Saturation: The Baseline operates at ~81.4% resource utilization. 
   Operating close to this threshold