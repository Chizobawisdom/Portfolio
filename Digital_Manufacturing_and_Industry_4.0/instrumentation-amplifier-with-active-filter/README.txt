 # LT Spice Circuit Simulation
Description:
This circuit implements a multi-stage signal conditioning system combining differential amplification and active filtering. The design features:

Input Stage: Differential amplifier using dual op-amps (U1, U2) with matched 10K/150K feedback networks for high common-mode rejection

Intermediate Stage: Universal op-amp (U5) configured for signal processing

Output Stage: Second-order active filter (U6) with 47K/2.2K resistors and 22nF/440nF capacitors for frequency shaping

Power Supply: ±14V dual rail configuration

Test Signal: 50mV pulse input with 50Ω source impedance

Applications: Sensor signal conditioning, biomedical instrumentation, audio processing

Simulation: Transient analysis over 10ms