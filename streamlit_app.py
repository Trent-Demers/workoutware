"""
WorkoutWare Streamlit Dashboard
===============================

This module provides a lightweight analytics dashboard built with Streamlit.
It connects directly to the WorkoutWare MySQL database and visualizes key
performance metrics for demonstration, debugging, and analytics use cases.

This dashboard is typically run locally by developers or project evaluators
to quickly inspect:

    • User workout volume trends
    • Best historical lifts
    • Exercise usage frequency
    • Daily/weekly training patterns
    • PR summaries

The dashboard reads directly from the existing Django database using SQL
queries. It is intentionally separated from the Django views because its
purpose is internal analytics rather than production UI.

Run command:
    streamlit run streamlit_app.py
"""

"""
WorkoutWare Streamlit Dashboard
===============================

Fully working analytics dashboard for the WorkoutWare fitness system.
Automatically connects to your MySQL database (workoutware_db) and visualizes:

    • User workout trends
    • PR history
    • Training volume by exercise
    • Progress charts
    • Recent validation flags

Run using:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# ----------------------------------------------------------------------
# DATABASE CONNECTION
# ----------------------------------------------------------------------

def get_connection():
    """Connect to your real MySQL DB: workoutware_db."""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Rutgers123",
        database="workoutware_db",
        port=3306,
    )

# ----------------------------------------------------------------------
# DATA LOADERS
# ----------------------------------------------------------------------

def load_users():
    """
    Load users from Django's auth_user table instead of user_info.
    """

    conn = get_connection()
    query = """
        SELECT id AS user_id,
               first_name,
               last_name,
               email,
               username
        FROM auth_user
        ORDER BY date_joined DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df



def load_user_progress(user_id):
    """Load progress table for selected user."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT p.date, p.exercise_id, e.name AS exercise_name,
               p.max_weight, p.total_volume, p.period_type
        FROM progress p
        JOIN exercise e ON p.exercise_id = e.exercise_id
        WHERE p.user_id = %s
        ORDER BY p.date ASC;
    """, conn, params=[user_id])
    conn.close()
    return df


def load_prs(user_id):
    """Load PRs (user_pb table)."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT e.name AS exercise_name,
               pb.pb_weight,
               pb.pb_date,
               pb.previous_pr
        FROM user_pb pb
        JOIN exercise e ON pb.exercise_id = e.exercise_id
        WHERE pb.user_id = %s
        ORDER BY pb.pb_date DESC;
    """, conn, params=[user_id])
    conn.close()
    return df


def load_top_volume_exercises(user_id):
    """Compute volume = weight × reps grouped by exercise."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT e.name AS exercise_name,
               SUM(s.weight * s.reps) AS volume
        FROM sets s
        JOIN session_exercises se ON s.session_exercise_id = se.session_exercise_id
        JOIN exercise e ON se.exercise_id = e.exercise_id
        JOIN workout_sessions ws ON ws.session_id = se.session_id
        WHERE ws.user_id = %s
          AND ws.completed = 1
          AND ws.is_template = 0
          AND s.weight IS NOT NULL
        GROUP BY e.exercise_id
        ORDER BY volume DESC;
    """, conn, params=[user_id])
    conn.close()
    return df


def load_validation_log(user_id):
    """Load all validation flags."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT v.timestamp,
               e.name AS exercise_name,
               v.input_weight,
               v.expected_max,
               v.flagged_as,
               v.user_action
        FROM data_validation v
        JOIN exercise e ON v.exercise_id = e.exercise_id
        WHERE v.user_id = %s
        ORDER BY v.timestamp DESC;
    """, conn, params=[user_id])
    conn.close()
    return df


def load_bodyweight(user_id):
    """Load bodyweight logs."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT date, weight
        FROM user_stats_log
        WHERE user_id = %s
        ORDER BY date ASC;
    """, conn, params=[user_id])
    conn.close()
    return df

# ----------------------------------------------------------------------
# UI COMPONENTS
# ----------------------------------------------------------------------

def display_user_overview(selected_user, users_df):
    row = users_df[users_df["user_id"] == selected_user].iloc[0]
    st.header("👤 User Overview")
    st.write(f"**Name:** {row.first_name} {row.last_name}")
    st.write(f"**Email:** {row.email}")


def display_pr_table(df):
    st.subheader("🏆 Personal Records")
    if df.empty:
        st.info("No PRs recorded yet.")
    else:
        st.dataframe(df)


def display_progress_charts(df):
    st.subheader("📈 Progress Trends")
    if df.empty:
        st.warning("No progress data available.")
        return

    for ex in df["exercise_name"].unique():
        st.write(f"### {ex}")
        ex_df = df[df["exercise_name"] == ex]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Max Weight Over Time**")
            st.line_chart(ex_df.set_index("date")["max_weight"])

        with col2:
            st.write("**Total Volume Over Time**")
            st.line_chart(ex_df.set_index("date")["total_volume"])


def display_top_volume(df):
    st.subheader("🔥 Highest Training Volume")
    if df.empty:
        st.info("No workout volume recorded.")
    else:
        st.bar_chart(df.set_index("exercise_name"))


def display_validation_log(df):
    st.subheader("🧪 Data Validation History")
    if df.empty:
        st.info("No validation logs yet.")
    else:
        st.dataframe(df)


def display_bodyweight(df):
    st.subheader("⚖️ Bodyweight Trend")
    if df.empty:
        st.info("No bodyweight logs yet.")
    else:
        st.line_chart(df.set_index("date"))

# ----------------------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------------------

def main():
    st.title("WorkoutWare Analytics Dashboard")
    st.caption("Internal analytics tool for developers & evaluators")

    # USER DROPDOWN
    users_df = load_users()
    user_map = {}

    for _, row in users_df.iterrows():
        name = row.first_name or row.username
        display_name = f"{name} ({row.email})"
        user_map[display_name] = row.user_id

    selected_name = st.sidebar.selectbox("Select User", list(user_map.keys()))
    user_id = user_map[selected_name]

    # USER INFO
    display_user_overview(user_id, users_df)

    # PRs
    display_pr_table(load_prs(user_id))

    # Progress Trends
    display_progress_charts(load_user_progress(user_id))

    # Volume
    display_top_volume(load_top_volume_exercises(user_id))

    # Bodyweight
    display_bodyweight(load_bodyweight(user_id))

    # Validation
    display_validation_log(load_validation_log(user_id))


if __name__ == "__main__":
    main()





