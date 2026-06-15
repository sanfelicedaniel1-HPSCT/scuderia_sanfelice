import streamlit as st
import pandas as pd
from openf1_client import (
    get_sessions, get_drivers, get_laps,
    get_stints, get_weather, get_position
)

# ── Page config ──────────────────────────────────────────────────────────────
# This must be the FIRST Streamlit command in the file.
# set_page_config controls the browser tab title, icon, and layout.
# layout="wide" uses the full browser width instead of a narrow centered column.
st.set_page_config(
    page_title="Scuderia San Felice",
    page_icon="🏎️",
    layout="wide"
)

# ── Title ─────────────────────────────────────────────────────────────────────
# st.title() renders a large H1 heading on the page.
st.title("🏎️ Scuderia San Felice — F1 Dashboard")

# ── Sidebar controls ──────────────────────────────────────────────────────────
# st.sidebar is a panel on the left. Any Streamlit widget placed inside it
# appears there instead of in the main area.
# We use it for filters so the main area stays clean.
st.sidebar.header("Filters")

# st.selectbox() creates a dropdown menu.
# The first argument is the label shown above the dropdown.
# The second argument is the list of options.
year = st.sidebar.selectbox("Season", [2026, 2025, 2024, 2023])

# ── Fetch sessions for chosen year ───────────────────────────────────────────
# st.spinner() shows a loading message while the indented block runs.
# This is important because API calls take a moment.
with st.spinner("Loading sessions..."):
    sessions = get_sessions(year=year)

# Build a human-readable label for each session, e.g. "Bahrain — Race"
# We'll use this in the next dropdown.
session_labels = [
    f"{s['country_name']} — {s['session_name']}" for s in sessions
]

selected_label = st.sidebar.selectbox("Session", session_labels)

# Find the full session dict that matches the label the user chose.
# next() walks through the list and returns the first match.
selected_session = next(
    s for s in sessions
    if f"{s['country_name']} — {s['session_name']}" == selected_label
)

# Pull out the session_key — a unique integer the API uses to identify sessions.
session_key = selected_session["session_key"]

# ── Tabs ──────────────────────────────────────────────────────────────────────
# st.tabs() creates a tabbed interface. Each tab is its own section.
# The list of strings becomes the tab labels.
# We unpack them directly into variables so we can use them as context managers.
tab_drivers, tab_laps, tab_stints, tab_weather = st.tabs(
    ["Drivers", "Lap Times", "Stints", "Weather"]
)

# ── Tab 1: Drivers ────────────────────────────────────────────────────────────
with tab_drivers:
    st.subheader("Drivers in this session")

    with st.spinner("Fetching drivers..."):
        drivers = get_drivers(session_key=session_key)

    if drivers:
        # pd.DataFrame() converts a list of dicts into a table.
        # Each dict key becomes a column header.
        df = pd.DataFrame(drivers)

        # Pick only the columns we care about, and rename them to be readable.
        df = df[["driver_number", "name_acronym", "full_name", "team_name"]].rename(columns={
            "driver_number": "#",
            "name_acronym": "Code",
            "full_name": "Name",
            "team_name": "Team"
        })

        # st.dataframe() renders an interactive scrollable table.
        # use_container_width=True makes it fill the available width.
        st.dataframe(df, use_container_width=True)
    else:
        # st.info() shows a blue info box — friendlier than plain text for empty states.
        st.info("No driver data available for this session.")

# ── Tab 2: Lap Times ──────────────────────────────────────────────────────────
with tab_laps:
    st.subheader("Lap Times")

    with st.spinner("Fetching laps..."):
        laps = get_laps(session_key=session_key)

    if laps:
        df = pd.DataFrame(laps)

        # Keep only the columns that are useful for a lap time view.
        cols = ["driver_number", "lap_number", "lap_duration",
                "duration_sector_1", "duration_sector_2", "duration_sector_3"]

        # Some sessions (like races) may not have all columns, so we filter
        # to only include columns that actually exist in the data.
        cols = [c for c in cols if c in df.columns]
        df = df[cols]

        # Driver filter — let the user narrow to one driver.
        # sorted() puts the numbers in order. "All" lets them see everyone.
        driver_nums = ["All"] + sorted(df["driver_number"].unique().tolist())
        chosen_driver = st.selectbox("Filter by driver number", driver_nums)

        if chosen_driver != "All":
            # Boolean indexing: keeps only rows where driver_number matches.
            df = df[df["driver_number"] == chosen_driver]

        st.dataframe(df, use_container_width=True)

        # st.line_chart() draws a line chart from a DataFrame.
        # It uses the DataFrame index as the x-axis and each column as a line.
        if "lap_duration" in df.columns and not df.empty:
            st.subheader("Lap duration over time")
            chart_df = df[["lap_number", "lap_duration"]].set_index("lap_number")
            st.line_chart(chart_df)
    else:
        st.info("No lap data available for this session.")

# ── Tab 3: Stints ─────────────────────────────────────────────────────────────
with tab_stints:
    st.subheader("Tyre Stints")

    with st.spinner("Fetching stints..."):
        stints = get_stints(session_key=session_key)

    if stints:
        df = pd.DataFrame(stints)
        cols = ["driver_number", "stint_number", "compound",
                "lap_start", "lap_end", "tyre_age_at_start"]
        cols = [c for c in cols if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)

        # Show a breakdown of how many stints used each compound.
        if "compound" in df.columns:
            st.subheader("Compound usage")
            # value_counts() counts how many times each compound appears.
            # st.bar_chart() turns a Series into a bar chart automatically.
            st.bar_chart(df["compound"].value_counts())
    else:
        st.info("No stint data available for this session.")

# ── Tab 4: Weather ────────────────────────────────────────────────────────────
with tab_weather:
    st.subheader("Track Weather")

    with st.spinner("Fetching weather..."):
        weather = get_weather(session_key=session_key)

    if weather:
        df = pd.DataFrame(weather)

        # Show the most recent reading as a set of metric cards at the top.
        latest = df.iloc[-1]  # iloc[-1] gets the last row

        # st.columns() divides the page into equal-width columns.
        # We unpack them into four variables.
        col1, col2, col3, col4 = st.columns(4)

        # st.metric() shows a bold number with a label above it.
        col1.metric("Air Temp", f"{latest['air_temperature']}°C")
        col2.metric("Track Temp", f"{latest['track_temperature']}°C")
        col3.metric("Humidity", f"{latest['humidity']}%")
        col4.metric("Rainfall", "Yes" if latest["rainfall"] else "No")

        # Parse the date column so Streamlit can use it as a time axis.
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        st.subheader("Temperature over session")
        st.line_chart(df[["air_temperature", "track_temperature"]])
    else:
        st.info("No weather data available for this session.")