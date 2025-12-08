"""
WorkoutWare Streamlit Dashboard
===============================

Internal analytics dashboard for the WorkoutWare fitness system.

This app connects directly to the MySQL database `workoutware_db` and mirrors
your ER diagram tables:

    user_info, workout_sessions, session_exercises, sets,
    exercise, target, exercise_target_association,
    user_stats_log, user_pb, goals, workout_plan,
    daily_workout_plan, progress, data_validation

It is for **developers / evaluators**, not end-users. It lets you quickly see:

  • User list & profile info
  • Workout history and volume
  • PR (personal record) history
  • Exercise usage & volume rankings
  • Bodyweight trend
  • Validation flags (outliers, new PRs, etc.)

Run from the project root with:

    streamlit run streamlit_app.py
"""

from datetime import datetime

import mysql.connector
import pandas as pd
import streamlit as st


# ------------------------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------------------------

def get_connection():
    """
    Open a NEW connection to the MySQL database.

    We DO NOT cache the connection. Each loader opens and closes its own
    connection so we never reuse a dead connection (avoids
    'MySQL Connection not available' errors).
    """
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Rutgers123",
        database="workoutware_db",
        port=3306,
    )


# ------------------------------------------------------------------------------
# DATA LOADERS (ALL CACHE **DATAFRAMES**, NOT CONNECTIONS)
# ------------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading users…")
def load_users():
    """
    Fetch all registered users from user_info.

    Returns
    -------
    DataFrame with:
        user_id, first_name, last_name, email,
        date_registered, fitness_goal, user_type, display_name
    """
    query = """
        SELECT
            user_id,
            first_name,
            last_name,
            email,
            date_registered,
            fitness_goal,
            user_type,
            registered
        FROM user_info
        ORDER BY
            date_registered DESC,
            user_id DESC;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return df

    def make_display(row):
        name = f"{row['first_name']} {row['last_name']}".strip()
        if not name:
            name = row["email"] or f"User #{row['user_id']}"
        return f"{name} (id={row['user_id']})"

    df["display_name"] = df.apply(make_display, axis=1)
    return df


@st.cache_data(show_spinner="Loading workout history…")
def load_workout_summary(user_id: int) -> pd.DataFrame:
    """
    Summary of workouts per session for a given user.

    Returns columns:
        session_id, session_date, session_name, completed,
        exercise_count, set_count, total_volume
    """
    query = """
        SELECT
            ws.session_id,
            ws.session_date,
            ws.session_name,
            ws.completed,
            COUNT(DISTINCT se.session_exercise_id) AS exercise_count,
            COUNT(s.set_id) AS set_count,
            COALESCE(
                SUM(
                    CASE
                        WHEN s.weight IS NOT NULL AND s.reps IS NOT NULL
                        THEN s.weight * s.reps
                        ELSE 0
                    END
                ),
                0
            ) AS total_volume
        FROM workout_sessions ws
        LEFT JOIN session_exercises se
            ON se.session_id = ws.session_id
        LEFT JOIN sets s
            ON s.session_exercise_id = se.session_exercise_id
        WHERE
            ws.user_id = %s
            AND ws.is_template = 0
        GROUP BY
            ws.session_id,
            ws.session_date,
            ws.session_name,
            ws.completed
        ORDER BY
            ws.session_date DESC,
            ws.session_id DESC;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


@st.cache_data(show_spinner="Loading PRs…")
def load_prs(user_id: int) -> pd.DataFrame:
    """
    Personal records per exercise.

    Returns columns:
        exercise_name, pb_weight, pb_reps, pb_time, pb_date, previous_pr
    """
    query = """
        SELECT
            e.name AS exercise_name,
            pb.pb_weight,
            pb.pb_reps,
            pb.pb_time,
            pb.pb_date,
            pb.previous_pr
        FROM user_pb pb
        JOIN exercise e
            ON pb.exercise_id = e.exercise_id
        WHERE
            pb.user_id = %s
        ORDER BY
            pb.pb_date DESC,
            e.name ASC;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


@st.cache_data(show_spinner="Loading progress metrics…")
def load_progress(user_id: int) -> pd.DataFrame:
    """
    Load weekly / daily progress from progress table.

    Returns columns:
        date, exercise_id, exercise_name, max_weight,
        avg_weight, total_volume, period_type, workout_count
    """
    query = """
        SELECT
            p.date,
            p.exercise_id,
            e.name AS exercise_name,
            p.max_weight,
            p.avg_weight,
            p.total_volume,
            p.period_type,
            p.workout_count
        FROM progress p
        JOIN exercise e
            ON p.exercise_id = e.exercise_id
        WHERE
            p.user_id = %s
        ORDER BY
            p.date ASC,
            e.name ASC;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


@st.cache_data(show_spinner="Loading validation flags…")
def load_validation_flags(user_id: int) -> pd.DataFrame:
    """
    Load recent smart-validation events.

    Returns columns:
        timestamp, exercise_name, input_weight,
        expected_max, flagged_as, user_action
    """
    query = """
        SELECT
            v.timestamp,
            e.name AS exercise_name,
            v.input_weight,
            v.expected_max,
            v.flagged_as,
            v.user_action
        FROM data_validation v
        LEFT JOIN exercise e
            ON v.exercise_id = e.exercise_id
        WHERE
            v.user_id = %s
        ORDER BY
            v.timestamp DESC
        LIMIT 100;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


@st.cache_data(show_spinner="Loading bodyweight trend…")
def load_bodyweight_trend(user_id: int) -> pd.DataFrame:
    """
    Bodyweight over time from user_stats_log.

    Returns columns:
        date, weight
    """
    query = """
        SELECT
            date,
            weight
        FROM user_stats_log
        WHERE
            user_id = %s
            AND weight IS NOT NULL
        ORDER BY
            date ASC;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


@st.cache_data(show_spinner="Loading top-volume exercises…")
def load_top_volume_exercises(user_id: int) -> pd.DataFrame:
    """
    Total training volume per exercise.

    Returns columns:
        exercise_name, volume
    """
    query = """
        SELECT
            e.name AS exercise_name,
            COALESCE(
                SUM(
                    CASE
                        WHEN s.weight IS NOT NULL AND s.reps IS NOT NULL
                        THEN s.weight * s.reps
                        ELSE 0
                    END
                ),
                0
            ) AS volume
        FROM workout_sessions ws
        JOIN session_exercises se
            ON se.session_id = ws.session_id
        JOIN exercise e
            ON e.exercise_id = se.exercise_id
        LEFT JOIN sets s
            ON s.session_exercise_id = se.session_exercise_id
        WHERE
            ws.user_id = %s
            AND ws.completed = 1
            AND ws.is_template = 0
        GROUP BY
            e.exercise_id,
            e.name
        ORDER BY
            volume DESC;
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=[user_id])
    conn.close()
    return df


# ------------------------------------------------------------------------------
# UI HELPERS
# ------------------------------------------------------------------------------

def show_user_overview(user_row: pd.Series):
    st.subheader("👤 User Overview")

    name = f"{user_row['first_name']} {user_row['last_name']}".strip()
    if not name:
        name = "(no name recorded)"

    st.write(f"**Name:** {name}")
    st.write(f"**Email:** {user_row['email'] or '(none)'}")

    if pd.notna(user_row.get("date_registered")):
        st.write(f"**Registered:** {user_row['date_registered']:%Y-%m-%d}")
    if user_row.get("fitness_goal"):
        st.write(f"**Fitness Goal:** {user_row['fitness_goal']}")
    if user_row.get("user_type"):
        st.write(f"**User Type:** {user_row['user_type']}")


def show_pr_section(pr_df: pd.DataFrame):
    st.subheader("🏆 Personal Records")
    if pr_df.empty:
        st.info("No PRs recorded yet for this user.")
        return

    df = pr_df.copy()
    if "pb_date" in df.columns:
        df["pb_date"] = pd.to_datetime(df["pb_date"]).dt.date
    st.dataframe(df, use_container_width=True)


def show_workout_history(df: pd.DataFrame):
    st.subheader("📓 Workout History")
    if df.empty:
        st.info("No workouts logged yet for this user.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completed Workouts", int(df["completed"].sum()))
    with col2:
        st.metric("Total Sessions", int(len(df)))
    with col3:
        st.metric("Total Volume (lbs)",
                  int(df["total_volume"].sum()))

    st.markdown("#### Recent Sessions")
    st.dataframe(df.head(20), use_container_width=True)

    # Simple chart: total volume over time
    vol = df[["session_date", "total_volume"]].copy()
    vol = vol.sort_values("session_date")
    vol = vol.set_index("session_date")
    st.line_chart(vol)


def show_progress_charts(progress_df: pd.DataFrame):
    st.subheader("📈 Progress by Exercise")
    if progress_df.empty:
        st.info("No progress rows found in `progress` table.")
        return

    exercises = sorted(progress_df["exercise_name"].unique())
    ex_name = st.selectbox("Choose exercise", exercises)

    df_ex = progress_df[progress_df["exercise_name"] == ex_name].copy()
    df_ex = df_ex.sort_values("date")
    df_ex = df_ex.set_index("date")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Max Weight Over Time (lbs)**")
        if "max_weight" in df_ex:
            st.line_chart(df_ex["max_weight"])
        else:
            st.write("No `max_weight` column in progress table.")

    with col2:
        st.markdown("**Total Volume Over Time (lbs)**")
        if "total_volume" in df_ex:
            st.line_chart(df_ex["total_volume"])
        else:
            st.write("No `total_volume` column in progress table.")

    st.markdown("**Raw Progress Data**")
    st.dataframe(df_ex.reset_index(), use_container_width=True)


def show_bodyweight_chart(weight_df: pd.DataFrame):
    st.subheader("⚖️ Bodyweight Trend")
    if weight_df.empty:
        st.info("No bodyweight logs in `user_stats_log`.")
        return

    df = weight_df.copy()
    df = df.sort_values("date").set_index("date")
    st.line_chart(df["weight"])


def show_validation_table(v_df: pd.DataFrame):
    st.subheader("🛡️ Recent Validation Flags")
    if v_df.empty:
        st.info("No rows in `data_validation` for this user.")
        return

    df = v_df.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.dataframe(df, use_container_width=True)


def show_top_volume_chart(tv_df: pd.DataFrame):
    st.subheader("🔥 Highest-Volume Exercises")
    if tv_df.empty:
        st.info("No completed workout volume for this user.")
        return

    df = tv_df.set_index("exercise_name")
    st.bar_chart(df["volume"])


# ------------------------------------------------------------------------------
# MAIN APP
# ------------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="WorkoutWare Streamlit Dashboard",
        layout="wide",
    )

    st.title("WorkoutWare Streamlit Dashboard")

    # ----- Sidebar: choose user -----
    st.sidebar.header("Select User")
    users_df = load_users()

    if users_df.empty:
        st.error("No users found in `user_info`.")
        return

    selected_display = st.sidebar.selectbox(
        "User",
        users_df["display_name"].tolist(),
    )
    user_row = users_df[users_df["display_name"] == selected_display].iloc[0]
    user_id = int(user_row["user_id"])

    # ----- Sections -----
    show_user_overview(user_row)

    # Layout: PRs + bodyweight
    col_left, col_right = st.columns(2)
    with col_left:
        prs = load_prs(user_id)
        show_pr_section(prs)
    with col_right:
        bw = load_bodyweight_trend(user_id)
        show_bodyweight_chart(bw)

    st.markdown("---")

    # Workout history + top-volume
    workouts = load_workout_summary(user_id)
    top_vol = load_top_volume_exercises(user_id)

    col1, col2 = st.columns([3, 2])
    with col1:
        show_workout_history(workouts)
    with col2:
        show_top_volume_chart(top_vol)

    st.markdown("---")

    # Progress table & charts
    progress_df = load_progress(user_id)
    show_progress_charts(progress_df)

    st.markdown("---")

    # Validation flags
    v_df = load_validation_flags(user_id)
    show_validation_table(v_df)


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()







