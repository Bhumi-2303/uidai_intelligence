import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# -------------------------------------------------
# Load processed data (pipeline output only)
# -------------------------------------------------
df = pd.read_csv("../outputs/final_master_table.csv")

# Normalize state text (safety)
df["state"] = df["state"].str.upper().str.strip()

# Get list of states
states = sorted(df["state"].unique())
states.insert(0, "ALL")

# -------------------------------------------------
# App
# -------------------------------------------------
app = Dash(__name__)

app.layout = html.Div([

    # ---------------- SIDEBAR ----------------
    html.Div([
        html.H3("Filters"),

        html.Label("Select State"),
        dcc.Dropdown(
            id="state-dropdown",
            options=[{"label": s.title(), "value": s} for s in states],
            value="ALL",
            clearable=False
        ),
    ], style={
        "width": "20%",
        "display": "inline-block",
        "verticalAlign": "top",
        "padding": "20px",
        "backgroundColor": "#f4f4f4"
    }),

    # ---------------- MAIN PANEL ----------------
    html.Div([
        html.H1("UIDAI District Intelligence Dashboard"),

        html.H3(id="district-count"),

        dcc.Graph(id="enrol-trend"),
        dcc.Graph(id="risk-chart"),
    ], style={
        "width": "78%",
        "display": "inline-block",
        "padding": "20px"
    })
])

# -------------------------------------------------
# CALLBACK
# -------------------------------------------------
@app.callback(
    Output("district-count", "children"),
    Output("enrol-trend", "figure"),
    Output("risk-chart", "figure"),
    Input("state-dropdown", "value")
)
def update_dashboard(selected_state):

    if selected_state == "ALL":
        dff = df.copy()
        title_suffix = "All States"
    else:
        dff = df[df["state"] == selected_state]
        title_suffix = selected_state.title()

    # ---- Correct district count (STATE-WISE) ----
    district_count = dff["district_clean"].nunique()

    # ---- Enrolment trend ----
    enrol_fig = px.line(
        dff,
        x="month",
        y="enrol_total",
        color="district_clean",
        title=f"District-wise Enrolment Trend ({title_suffix})"
    )

    # ---- Risk districts ----
    risk_df = dff[dff["risk_flag"]]

    if risk_df.empty:
        risk_fig = px.bar(title="No High Risk Districts")
    else:
        risk_fig = px.bar(
            risk_df,
            x="district_clean",
            y="update_pressure",
            title=f"High Risk Districts ({title_suffix})"
        )

    return (
        f"Total Official Districts: {district_count}",
        enrol_fig,
        risk_fig
    )


# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
