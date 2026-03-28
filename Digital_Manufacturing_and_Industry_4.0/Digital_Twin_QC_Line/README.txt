AnyLogic Case Study Dataset (Synthetic, 1 Year) — Resequencing Warehouse between Body Shop and Paint Shop
Period: 2024-01-01 to 2024-12-30  (timezone reference: Europe/Berlin)
Total vehicles: 181,606

COST PARAMETERS (as given in task)
- Parking space cost: €15,000 per space (capex)
- Body shop unplanned downtime cost (due to warehouse full): €400,000 per hour

FILES
1) 01_production_orders_planned.csv
   Planned/customer build sequence + attributes + convenience sequences.
   Columns:
   - VIN
   - planned_date, planned_sequence_in_day, planned_global_sequence
   - model, color, priority
   - actual_body_sequence (by body_exit_time)
   - actual_paint_sequence (by paint_start_time; baseline FIFO by body exit)

2) 02_bodyshop_output_actual.csv
   Body shop completions (arrival stream to the warehouse).
   Columns:
   - VIN
   - body_exit_time (timestamp)
   - body_cycle_min (baseline)
   - body_extra_delay_min (rare large delays that create resequencing need)
   - actual_body_sequence

3) 03_paintshop_input_actual.csv
   Paint shop processing (baseline without resequencing warehouse).
   Columns:
   - VIN
   - paint_start_time, paint_end_time
   - paint_proc_min
   - paint_changeover_min (penalty when color changes vs previous painted unit)
   - paint_quality_hold_min (rare longer holds)
   - actual_paint_sequence

4) 04_downtime_events.csv
   Random unplanned downtime incidents (both shops), provided as exogenous events.
   Columns:
   - shop, downtime_start, downtime_end, duration_min, reason

INTENDED SIMULATION USE
- Use body_exit_time as arrivals into a warehouse buffer with capacity X.
- Implement a resequencing policy that releases bodies to paint aiming to restore planned_global_sequence.
- If warehouse is full when a body exits, body shop must halt → accumulate downtime cost.
- Evaluate total cost (capex + downtime) across X and choose optimum.
