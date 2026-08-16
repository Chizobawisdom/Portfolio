"""
OEE Dashboard for the OpenPLC project.

A self-contained Plotly Dash app - no extra software needed beyond
the Python packages below. Reads directly from the SQLite database
that logger.py writes to, and auto-refreshes every few seconds, so
it can be left open while simulator.py and logger.py are running
for a live demo.

Reuses the OEE math from oee_calculate.py rather than duplicating it.

Install:
  pip install dash plotly pandas --break-system-packages

Run:
  python3 dashboard.py

Then open http://127.0.0.1:8050 in a browser.
"""

import sqlite3

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from oee_calculate import load_readings, compute_oee

DB_PATH = "oee_data.db"
IDEAL_CYCLE_TIME_SECONDS = 2.0
REFRESH_INTERVAL_MS = 3000


def load_dataframe(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM readings ORDER BY timestamp ASC", conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def find_fault_episodes(df):
    """Return a list of (start, end) timestamp pairs for each
    Machine_Faulted episode, for shading the timeline chart."""
    episodes = []
    fault_start = None

    for _, row in df.iterrows():
        if row["Machine_Faulted"] and fault_start is None:
            fault_start = row["timestamp"]
        elif not row["Machine_Faulted"] and fault_start is not None:
            episodes.append((fault_start, row["timestamp"]))
            fault_start = None

    if fault_start is not None:
        episodes.append((fault_start, df["timestamp"].iloc[-1]))

    return episodes


def build_kpi_card(label, value_pct):
    return html.Div(
        [
            html.Div(label, className="kpi-label"),
            html.Div(f"{value_pct:.1f}%", className="kpi-value"),
        ],
        className="kpi-card",
    )


def build_timeline_figure(df, fault_episodes):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["Cycle_Count"],
        name="Cycle Count", mode="lines", line=dict(color="#2563eb"),
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["Good_Count"],
        name="Good Count", mode="lines", line=dict(color="#16a34a"),
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["Reject_Count"],
        name="Reject Count", mode="lines", line=dict(color="#dc2626"),
    ))

    for start, end in fault_episodes:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="red", opacity=0.15, line_width=0,
            annotation_text="fault", annotation_position="top left",
        )

    fig.update_layout(
        title="Production Counts Over Time (red bands = downtime)",
        xaxis_title="Time", yaxis_title="Count",
        template="plotly_white", height=400,
        legend=dict(orientation="h", y=1.1),
    )
    return fig


def build_quality_figure(good_count, reject_count):
    fig = go.Figure(data=[go.Pie(
        labels=["Good", "Reject"],
        values=[good_count, reject_count],
        marker=dict(colors=["#16a34a", "#dc2626"]),
        hole=0.5,
    )])
    fig.update_layout(title="Good vs. Reject Parts", template="plotly_white", height=350)
    return fig


app = Dash(__name__)
app.title = "PLC-to-Cloud OEE Monitor"

app.layout = html.Div([
    html.H1("PLC-to-Cloud OEE Monitor", style={"marginBottom": "0"}),
    html.P("Live view of a simulated production line, driven over Modbus from an OpenPLC runtime.",
           style={"color": "#666", "marginTop": "4px"}),

    html.Div(id="kpi-row", className="kpi-row"),

    html.Div([
        dcc.Graph(id="timeline-graph"),
    ]),

    html.Div([
        dcc.Graph(id="quality-graph"),
    ], style={"maxWidth": "500px"}),

    html.Div(id="status-line", style={"color": "#888", "fontSize": "13px", "marginTop": "10px"}),

    dcc.Interval(id="refresh-interval", interval=REFRESH_INTERVAL_MS, n_intervals=0),
])

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { font-family: -apple-system, sans-serif; margin: 24px; background: #fafafa; }
            .kpi-row { display: flex; gap: 16px; margin: 20px 0; flex-wrap: wrap; }
            .kpi-card {
                background: white; border-radius: 12px; padding: 16px 24px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 140px;
            }
            .kpi-label { color: #888; font-size: 13px; text-transform: uppercase; }
            .kpi-value { font-size: 32px; font-weight: 600; margin-top: 4px; }
        </style>
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
"""


@app.callback(
    Output("kpi-row", "children"),
    Output("timeline-graph", "figure"),
    Output("quality-graph", "figure"),
    Output("status-line", "children"),
    Input("refresh-interval", "n_intervals"),
)
def refresh(_n_intervals):
    try:
        readings = load_readings(DB_PATH)
        df = load_dataframe(DB_PATH)
    except (ValueError, pd.errors.DatabaseError):
        empty_fig = go.Figure()
        empty_fig.update_layout(template="plotly_white", height=400)
        return (
            [html.Div("No data yet - start logger.py and simulator.py", className="kpi-card")],
            empty_fig, empty_fig,
            "Waiting for data...",
        )

    result = compute_oee(readings, IDEAL_CYCLE_TIME_SECONDS)
    fault_episodes = find_fault_episodes(df)

    kpi_cards = [
        build_kpi_card("Availability", result["availability"] * 100),
        build_kpi_card("Performance", result["performance"] * 100),
        build_kpi_card("Quality", result["quality"] * 100),
        build_kpi_card("OEE", result["oee"] * 100),
    ]

    timeline_fig = build_timeline_figure(df, fault_episodes)
    quality_fig = build_quality_figure(result["good_count"], result["reject_count"])

    status = (f"{len(df)} readings | {result['cycle_count']} total parts | "
              f"last updated {df['timestamp'].iloc[-1].strftime('%H:%M:%S')} UTC")

    return kpi_cards, timeline_fig, quality_fig, status


if __name__ == "__main__":
    app.run(debug=False, port=8050)
