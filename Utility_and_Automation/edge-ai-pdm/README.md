# Edge AI for Predictive Maintenance

This project estimates the risk that an industrial machine will fail within 48 hours. It trains a model on historical sensor readings and failure records, then runs that model locally on a CPU. The monitoring service replays recorded telemetry one reading at a time and saves alerts to a file.

## How it works

1. **Prepare the training data.** The notebook uses 876,100 hourly readings from 100 machines. It labels a reading positive if the same machine has a recorded failure between the time of the reading and 48 hours later, inclusive. The model uses voltage, rotation speed, pressure, and vibration. The dataset also contains maintenance records, error codes, and machine metadata for further analysis. [Training notebook](notebooks/explore.ipynb)
2. **Summarize recent sensor behavior.** The feature code keeps the last 24 readings for each machine. It calculates the mean and standard deviation of each sensor over the last 3, 12, and 24 hourly readings, producing 24 features. Scoring begins once a machine has 24 readings. [Feature code](src/features.py)
3. **Train and export the model.** The notebook standardizes the features and fits a logistic regression model. It evaluates the model on a later period starting September 1, 2015, with a 48-hour gap between training and test to keep training labels from looking into the test period. It exports the fitted pipeline to ONNX and saves the expected feature order. [Model](models/pdm_logreg.onnx) · [Feature order](models/feature_names.json)
4. **Generate alerts.** The replay service scores each reading after warm-up and writes an alert when the estimated probability exceeds the threshold. After an alert, that machine has a 48-hour cooldown. The replay uses up to 23 hours of earlier readings to initialize the feature buffers before the requested start time. [Replay service](src/edge_service.py)

## Run the replay

Use Python 3.13, the version used by the notebook. Open a terminal in the folder containing this README. The trained model and sample data are included.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install numpy pandas onnxruntime
.\.venv\Scripts\python.exe -m src.edge_service --out output/replay.jsonl
```

**macOS or Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install numpy pandas onnxruntime
.venv/bin/python -m src.edge_service --out output/replay.jsonl
```

The commands use the default start date of `2015-09-01` and threshold of `0.3`. Add `--start YYYY-MM-DD` to change the first date to report or `--threshold 0.5` to require a higher model score. The service prints the number of readings processed, the number of alerts written, and the mean processing time per reading.

Each run replaces its output file. The examples write to `output/replay.jsonl` so you can compare it with the included log. If you omit `--out`, the service writes to `output/events.jsonl`.

The output is JSON Lines, with one alert per line. In this example, machine 3 exceeded the alert threshold with an estimated 71.17% chance of failure within the model’s 48-hour window.

```json
{"machineID":3,"timestamp":"2015-09-01 00:00:00","failure_probability":0.7117,"threshold":0.3,"horizon_hours":48}
```

To reproduce training and evaluation, install `jupyter`, `matplotlib`, `scikit-learn`, and `skl2onnx` in the same environment. Start Jupyter from the `notebooks/` directory and run `explore.ipynb` from top to bottom. The final cells regenerate the model and feature order in `models/`.

## Verified replay results

The full replay on Windows with Python 3.12.14 and ONNX Runtime 1.32.0 used the default start date (`2015-09-01`) and alert threshold (`0.3`). It processed **295,800 readings**, including warm-up, and reproduced **all 644 alerts**. The generated file matched the saved log **byte for byte**, including the alert order, timestamps, and reported failure probabilities. [Saved alert log](output/events.jsonl)

On this run, feature calculation, model inference, and alert logic averaged **0.243 ms per reading**.

## What the results mean

The notebook measured alert performance on the held-out test period at the default threshold of `0.3`. It also measured average precision across thresholds.

| Metric | Result | How to read it |
| --- | ---: | --- |
| Failure events caught | 81% | About 4 in 5 recorded failure events had at least one alert from 48 hours before failure through the time of failure. The evaluation matches each alert to the machine’s next failure and counts simultaneous component failures on one machine as a single event. |
| False alerts per machine per week | 0.27 | About one alert outside a failure window per machine every four weeks. |
| Average precision | 0.326 | Measures how well the model ranks readings near a failure across thresholds. The baseline was 0.037 because about 3.7% of test readings were positive. |

Changing the threshold trades warning coverage for alert volume. In validation, lowering it from `0.3` to `0.2` increased the share of failures caught from 77% to 91% and the false-alert rate from 0.25 to 0.37 per machine per week. At `0.3`, the median warning time among caught validation failures was 26 hours.

These figures describe a historical evaluation. The 81% includes alerts at the time of failure, so advance warning varies by event. The service currently runs against a CSV replay and saves alerts locally. Live sensor input and a maintenance notification system would be separate integrations.
