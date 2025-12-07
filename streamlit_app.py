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

import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime


# ------------------------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------------------------

def get_connection():
    """
    Create and return a connection to the MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection
            An active database connection.

    Notes:
        Connection parameters must match Django settings.py.
        The Streamlit dashboard runs outside Django, so it needs
        explicit credentials.
    """
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Rutgers123",
        database="workoutware",
        port=3306
    )


# ------------------------------------------------------------------------------
# DATA LOADERS
# ------------------------------------------------------------------------------

def load_users():
    """
    Fetch all users from the user_info table.

    Returns:
        pandas.DataFrame:
            Columns: user_id, first_name, last_name, email
    """
    conn = get_connection()
    query = """
        SELECT user_id, first_name, last_name, email
        FROM user_info
        ORDER BY date_registered DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_user_progress(user_id):
    """
    Load all daily and weekly progress metrics for a given user.

    Args:
        user_id (int)

    Returns:
        pandas.DataFrame:
            Contains date, exercise_id, max_weight, total_volume, period_type
    """
    conn = get_connection()
    query = """
        SELECT p.date, p.exercise_id, e.name AS exercise_name,
               p.max_weight, p.total_volume, p.period_type
        FROM progress p
        JOIN exercise e ON p.exercise_id = e.exercise_id
        WHERE p.user_id = %s
        ORDER BY p.date ASC;
    """
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


def load_prs(user_id):
    """
    Load personal records (PRs) for a given user.

    Args:
        user_id (int)

    Returns:
        pandas.DataFrame:
            Contains exercise name, PR weight, PR date, and previous PR value.
    """
    conn = get_connection()
    query = """
        SELECT e.name AS exercise_name,
               pb.pb_weight, pb.pb_date, pb.previous_pr
        FROM user_pb pb
        JOIN exercise e ON pb.exercise_id = e.exercise_id
        WHERE pb.user_id = %s
        ORDER BY pb.pb_date DESC;
    """
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


def load_top_volume_exercises(user_id):
    """
    Compute which exercises contribute the highest total volume.

    Args:
        user_id (int)

    Returns:
        pandas.DataFrame:
            exercise_name, total_volume
    """
    conn = get_connection()
    query = """
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
    """
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


# ------------------------------------------------------------------------------
# UI COMPONENTS
# ------------------------------------------------------------------------------

def display_user_overview(selected_user, users_df):
    """
    Display the selected user's profile summary.

    Args:
        selected_user (int): user_id
        users_df (DataFrame): dataframe containing user list
    """
    row = users_df[users_df["user_id"] == selected_user].iloc[0]

    st.subheader("👤 User Information")
    st.write(f"**Name:** {row.first_name} {row.last_name}")
    st.write(f"**Email:** {row.email}")


def display_pr_table(pr_df):
    """
    Display a table of personal records.

    Args:
        pr_df (DataFrame)
    """
    st.subheader("🏆 Personal Records")
    if pr_df.empty:
        st.info("No PRs recorded yet.")
        return
    st.dataframe(pr_df)


def display_progress_charts(progress_df):
    """
    Plot progress trends for all exercises.

    Args:
        progress_df (DataFrame)
    """
    st.subheader("📈 Progress Trends")

    if progress_df.empty:
        st.warning("No progress data available.")
        return

    exercises = progress_df["exercise_name"].unique()

    for ex in exercises:
        st.write(f"### {ex}")

        df_ex = progress_df[progress_df["exercise_name"] == ex]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Max Weight Over Time**")
            st.line_chart(df_ex[["date", "max_weight"]].set_index("date"))

        with col2:
            st.write("**Training Volume Over Time**")
            st.line_chart(df_ex[["date", "total_volume"]].set_index("date"))


def display_top_volume(top_vol_df):
    """
    Display which exercises have the highest overall training volume.

    Args:
        top_vol_df (DataFrame)
    """
    st.subheader("🔥 Highest Volume Exercises")

    if top_vol_df.empty:
        st.info("No logged workouts for this user.")
        return

    st.bar_chart(top_vol_df.set_index("exercise_name"))


# ------------------------------------------------------------------------------
# MAIN APP
# ------------------------------------------------------------------------------

def main():
    """
    Entry point for the Streamlit dashboard.

    Renders:
        - User dropdown selector
        - User profile information
        - PR history table
        - Daily / weekly progress charts
        - Top-volume exercise chart
    """
    st.title("WorkoutWare Analytics Dashboard")
    st.markdown("A developer-friendly interface for analyzing workout trends.")

    st.sidebar.header("Select User")
    users_df = load_users()

    if users_df.empty:
        st.error("No users found in database.")
        return

    user_map = {f"{row.first_name} {row.last_name}": row.user_id for _, row in users_df.iterrows()}
    selected_name = st.sidebar.selectbox("User", list(user_map.keys()))
    selected_user = user_map[selected_name]

    # SECTION: USER INFO
    display_user_overview(selected_user, users_df)

    # SECTION: PERSONAL RECORDS
    pr_df = load_prs(selected_user)
    display_pr_table(pr_df)

    # SECTION: PROGRESS
    progress_df = load_user_progress(selected_user)
    display_progress_charts(progress_df)

    # SECTION: VOLUME
    top_vol_df = load_top_volume_exercises(selected_user)
    display_top_volume(top_vol_df)


# ------------------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()





