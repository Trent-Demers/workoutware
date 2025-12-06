import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pymysql
from datetime import date

# ------------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="WorkoutWare Dashboard",
    layout="wide"
)

# ------------------------------------------------------------
# MySQL Database Connection
# ------------------------------------------------------------
DB_HOST = "127.0.0.1"
DB_NAME = "workout_db"
DB_USER = "root"
DB_PASS = "Rutgers123"
DB_PORT = "3306"

@st.cache_resource
def get_engine():
    """Create and cache the SQLAlchemy MySQL engine."""
    try:
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

engine = get_engine()

# ------------------------------------------------------------
# Data Loading Helpers
# ------------------------------------------------------------

def load_table(table_name):
    """Load a full table from MySQL as a pandas DataFrame."""
    try:
        return pd.read_sql(f"SELECT * FROM {table_name};", engine)
    except Exception as e:
        st.error(f"❌ Failed to load table {table_name}: {e}")
        return pd.DataFrame()

def load_workout_data():
    """Load all key data tables required for charts."""
    df_sessions = load_table("workout_sessions")
    df_session_ex = load_table("session_exercises")
    df_sets = load_table("sets")
    df_exercises = load_table("exercise")
    return df_sessions, df_session_ex, df_sets, df_exercises


# ------------------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------------------
# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🏋️ WorkoutWare Dashboard")
st.sidebar.write("Visualize your workouts, progress, and PRs.")

section = st.sidebar.radio(
    "Select a section:",
    ["📈 Weight Trend", "💪 Volume by Muscle Group", "📊 Workout Frequency", "🏆 PR Timeline"]
)

# 📅 Date Range Filter (goes RIGHT BELOW the radio)
from datetime import date

st.sidebar.write("### 📅 Date Range Filter")

start_date = st.sidebar.date_input("Start Date", date(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")

# ------------------------------------------------------------
# KPI Summary Cards
# ------------------------------------------------------------

df_sessions, df_session_ex, df_sets, df_exercises = load_workout_data()
# Apply date filtering to sessions
df_sessions["session_date"] = pd.to_datetime(df_sessions["session_date"])
df_sessions = df_sessions[
    (df_sessions["session_date"] >= pd.to_datetime(start_date)) &
    (df_sessions["session_date"] <= pd.to_datetime(end_date))
]


col1, col2, col3, col4 = st.columns(4)

# KPI 1 — Total Workouts
total_workouts = df_sessions[(df_sessions["completed"] == 1) & (df_sessions["is_template"] == 0)].shape[0]

# KPI 2 — Unique Exercises Logged
unique_exercises = df_session_ex["exercise_id"].nunique()

# KPI 3 — Total PRs
try:
    df_pr = load_table("user_pb")
    total_prs = df_pr.shape[0]
except:
    total_prs = 0

# KPI 4 — Workout Streak
df_sessions["session_date"] = pd.to_datetime(df_sessions["session_date"])
df_sessions = df_sessions.sort_values("session_date", ascending=False)

streak = 1
dates = df_sessions["session_date"].tolist()

for i in range(len(dates) - 1):
    if (dates[i] - dates[i+1]).days == 1:
        streak += 1
    else:
        break

# Display KPI cards
with col1:
    st.metric("🏋️ Total Workouts", total_workouts)

with col2:
    st.metric("🔥 Unique Exercises", unique_exercises)

with col3:
    st.metric("🏆 Total PRs", total_prs)

with col4:
    st.metric("📅 Current Streak", f"{streak} days")


# ------------------------------------------------------------
# SECTION 1 — Weight Trend Chart
# ------------------------------------------------------------
if section == "📈 Weight Trend":
    st.subheader("📈 Weight Lifted Over Time")

    df_sessions, df_session_ex, df_sets, df_exercises = load_workout_data()

    if df_sets.empty:
        st.warning("No workout data found.")
    else:
        # Merge tables
        df = df_sets.merge(df_session_ex, on="session_exercise_id")
        df = df.merge(df_sessions, on="session_id")
        df = df.merge(df_exercises, on="exercise_id")

        # Filter weight data
        df = df[df["weight"].notnull()]

        # Exercise dropdown
        exercises = sorted(df["name"].unique())
        selected_ex = st.selectbox("Select an exercise:", exercises)

        df_ex = df[df["name"] == selected_ex].copy()
        df_ex["session_date"] = pd.to_datetime(df_ex["session_date"])

        # Compute max weight per session
        df_plot = (
            df_ex.groupby("session_date")["weight"]
            .max()
            .reset_index()
            .sort_values("session_date")
        )

        st.line_chart(df_plot, x="session_date", y="weight")
        st.success(f"Showing weight trend for: **{selected_ex}**")


# ------------------------------------------------------------
# SECTION 2 — Volume by Muscle Group
# ------------------------------------------------------------
elif section == "💪 Volume by Muscle Group":
    st.subheader("💪 Training Volume by Muscle Group")

    df_sessions, df_session_ex, df_sets, df_exercises = load_workout_data()

    if df_sets.empty:
        st.warning("No workout data found.")
    else:
        # Merge tables
        df = df_sets.merge(df_session_ex, on="session_exercise_id")
        df = df.merge(df_sessions, on="session_id")
        df = df.merge(df_exercises, on="exercise_id")

        df = df[df["weight"].notnull()]  # ensure valid data

        # Compute training volume
        df["volume"] = df["weight"] * df["reps"]

        # Identify correct muscle group column
        if "muscle_group" in df.columns:
            muscle_col = "muscle_group"
        elif "subtype" in df.columns:
            muscle_col = "subtype"
        else:
            st.error("❌ Could not find a 'muscle_group' or 'subtype' column in exercise table.")
            st.stop()

        # Aggregate volume
        df_group = (
            df.groupby(muscle_col)["volume"]
            .sum()
            .reset_index()
            .sort_values("volume", ascending=False)
        )

        st.bar_chart(df_group, x=muscle_col, y="volume")
        st.success("Volume by muscle group loaded successfully!")


# ------------------------------------------------------------
# SECTION 3 — Workout Frequency (placeholder)
# ------------------------------------------------------------
elif section == "📊 Workout Frequency":
    st.subheader("📊 Workout Frequency by Day")

    df_sessions, df_session_ex, df_sets, df_exercises = load_workout_data()

    if df_sessions.empty:
        st.warning("No workout sessions found.")
    else:
        # Convert dates
        df_sessions["session_date"] = pd.to_datetime(df_sessions["session_date"])

        # Filter only completed workouts (ignore templates)
        df_sessions = df_sessions[
            (df_sessions["completed"] == 1) & (df_sessions["is_template"] == 0)
        ]

        if df_sessions.empty:
            st.warning("No completed workouts found.")
        else:
            # Extract day of week
            df_sessions["day_of_week"] = df_sessions["session_date"].dt.day_name()

            # Order days correctly (not alphabetically)
            ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            df_freq = (
                df_sessions.groupby("day_of_week")
                .size()
                .reindex(ordered_days, fill_value=0)
                .reset_index(name="workout_count")
            )

            # Display bar chart
            st.bar_chart(df_freq, x="day_of_week", y="workout_count")

            st.success("Workout frequency chart loaded!")



# ------------------------------------------------------------
# SECTION 4 — PR Timeline (placeholder)
# ------------------------------------------------------------
elif section == "🏆 PR Timeline":
    st.subheader("🏆 Personal Records Over Time")

    # Load PR table
    try:
        df_pr = load_table("user_pb")
        df_exercises = load_table("exercise")
    except Exception as e:
        st.error(f"❌ Could not load PR data: {e}")
        st.stop()

    if df_pr.empty:
        st.warning("No PR records found.")
    else:
        # Merge exercise names
        df = df_pr.merge(df_exercises, on="exercise_id", how="left")

        # Convert to proper date format
        df["pb_date"] = pd.to_datetime(df["pb_date"])

        # Only Weight PRs (ignore reps or others)
        df = df[df["pr_type"] == "max_weight"]

        # Create dropdown for exercise choice
        exercise_list = sorted(df["name"].unique())
        selected_ex = st.selectbox("Select an exercise:", exercise_list)

        # Filter PRs for selected exercise
        df_ex = df[df["name"] == selected_ex].copy()
        df_ex = df_ex.sort_values("pb_date")

        # Prepare chart data
        df_plot = df_ex[["pb_date", "pb_weight"]]

        # Plot
        st.line_chart(df_plot, x="pb_date", y="pb_weight")

        # Display previous → new PR improvements
        st.write("### Improvement History")
        for _, row in df_ex.iterrows():
            prev = row["previous_pr"]
            curr = row["pb_weight"]
            date_str = row["pb_date"].strftime("%Y-%m-%d")

            if prev:
                diff = curr - prev
                st.write(f"**{date_str}: {curr} lbs** (↑ {diff} lbs from previous PR)")
            else:
                st.write(f"**{date_str}: {curr} lbs** (first PR recorded)")

        st.success(f"PR timeline updated for: **{selected_ex}**")




