"""
Streamlit front-end for Workoutware.

Run with:
    streamlit run streamlit_client/app.py
"""

from datetime import date
from typing import Dict, Any, Optional, List
import os
import sys

import pandas as pd
import streamlit as st

# Ensure the package is importable when run directly via `streamlit run`.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from streamlit_client.config import get_settings
from streamlit_client.services import auth, workouts, goals, stats, admin as admin_service
from streamlit_client.ui.theme import apply_theme


# ------------------------------------------------------------------------------
# SESSION STATE HELPERS
# ------------------------------------------------------------------------------

def _init_state() -> None:
    """Ensure session_state keys exist."""
    st.session_state.setdefault("page", "dashboard")
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("selected_session_id", None)
    st.session_state.setdefault("flash", None)


def _set_flash(message: str, kind: str = "success") -> None:
    st.session_state["flash"] = {"message": message, "kind": kind}


def _consume_flash() -> None:
    flash = st.session_state.get("flash")
    if flash:
        if flash["kind"] == "success":
            st.success(flash["message"])
        else:
            st.warning(flash["message"])
    st.session_state["flash"] = None


# ------------------------------------------------------------------------------
# USER HANDLING
# ------------------------------------------------------------------------------
def _normalize_user(user_row: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce user rows into a consistent shape for session state."""
    return {
        "user_id": user_row["user_id"],
        "username": user_row["username"],
        "email": user_row.get("email"),
        "user_type": user_row.get("user_type") or "member",
        "fitness_goal": user_row.get("fitness_goal"),
    }


# ------------------------------------------------------------------------------
# NAVIGATION
# ------------------------------------------------------------------------------

def render_nav(user: Dict[str, Any], users: List[Dict[str, Any]]) -> None:
    with st.sidebar:
        st.header("Active User")
        options = [f"{u['username']} (id {u['user_id']})" for u in users]
        current_label = f"{user['username']} (id {user['user_id']})"
        try:
            current_index = options.index(current_label)
        except ValueError:
            current_index = 0
        selected_label = st.selectbox("Switch user", options, index=current_index)
        selected_user = users[options.index(selected_label)]
        if selected_user["user_id"] != user["user_id"]:
            st.session_state["user"] = _normalize_user(selected_user)
            st.rerun()

        st.markdown("---")
        if st.button("Dashboard", use_container_width=True):
            st.session_state["page"] = "dashboard"
        if st.button("Log Workout", use_container_width=True):
            st.session_state["page"] = "log_workout"
        if st.button("Progress", use_container_width=True):
            st.session_state["page"] = "progress"
        if st.button("Goals", use_container_width=True):
            st.session_state["page"] = "goals"
        if st.button("Body Stats", use_container_width=True):
            st.session_state["page"] = "body_stats"
        if st.button("Completed Workouts", use_container_width=True):
            st.session_state["page"] = "completed"
        if user.get("user_type") == "admin":
            if st.button("Admin", use_container_width=True):
                st.session_state["page"] = "admin"


# ------------------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------------------

def render_dashboard(user: Dict[str, Any]) -> None:
    st.title("Dashboard")
    _consume_flash()
    kpis = stats.dashboard_kpis(user["user_id"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Day Workout Streak", kpis["streak"])
    with col2:
        st.metric("Workouts This Week", kpis["week_completed"])
    with col3:
        st.metric("Total Workouts", kpis["total_completed"])

    st.markdown("### Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("Log Workout", use_container_width=True):
            st.session_state["page"] = "log_workout"
            st.rerun()
    with q2:
        if st.button("View Progress", use_container_width=True):
            st.session_state["page"] = "progress"
            st.rerun()
    with q3:
        if st.button("Manage Goals", use_container_width=True):
            st.session_state["page"] = "goals"
            st.rerun()
    with q4:
        if st.button("Log Body Stats", use_container_width=True):
            st.session_state["page"] = "body_stats"
            st.rerun()

    st.markdown("### Recent PRs")
    prs = stats.recent_prs(user["user_id"])
    if prs:
        df_prs = pd.DataFrame(prs)
        st.dataframe(df_prs, use_container_width=True, hide_index=True)
    else:
        st.info("No PRs yet—log a workout to get started.")

    st.markdown("### Active Goals")
    active = goals.list_active_goals(user["user_id"])
    if not active:
        st.info("No active goals. Create one on the Goals page.")
    else:
        for goal in active:
            pct = goal["progress_percent"]
            label = goal["goal_description"] or goal["goal_type"]
            st.progress(min(pct / 100, 1.0), text=f"{label} — {pct:.1f}%")

    st.markdown("### This Week")
    recent = workouts.list_completed_sessions(user["user_id"], this_week_only=True)
    if recent:
        st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
    else:
        st.info("No completed workouts this week yet.")


# ------------------------------------------------------------------------------
# WORKOUT CREATION + DETAIL
# ------------------------------------------------------------------------------

def _render_session_detail(user: Dict[str, Any], session_id: int) -> None:
    detail = workouts.get_session_detail(session_id)
    session = detail.get("session")
    if not session:
        st.error("Session not found.")
        return

    st.subheader(f"{session.get('session_name') or 'Workout'} — {session.get('session_date')}")
    st.caption("Add exercises, log sets, and mark complete.")

    exercises = detail.get("exercises", [])

    # Add exercise form
    catalog = workouts.list_exercise_catalog()
    exercise_options = {}
    ex_label = None
    target_sets = 3
    target_reps = 8
    submitted = False
    
    with st.form(f"add_exercise_{session_id}"):
        st.markdown("**Add Exercise**")
        if not catalog:
            st.warning("No exercises available. Please add exercises via the Admin page.")
        else:
            exercise_options = {f"{ex['name']} ({ex.get('exercise_type') or 'Strength'})": ex["exercise_id"] for ex in catalog}
            option_keys = list(exercise_options.keys())
            ex_label = st.selectbox("Exercise", option_keys, index=0 if option_keys else None)
        target_sets = st.number_input("Target Sets", min_value=1, max_value=10, value=3)
        target_reps = st.number_input("Target Reps", min_value=1, max_value=30, value=8)
        submitted = st.form_submit_button("Add Exercise")
    
    if submitted and catalog and ex_label and ex_label in exercise_options:
        order = len(exercises) + 1
        workouts.add_exercise_to_session(session_id, exercise_options[ex_label], order, target_sets, target_reps)
        _set_flash("Exercise added.")
        st.rerun()

    for ex in exercises:
        st.markdown(f"#### {ex['name']} — Target {ex.get('target_sets') or '-'} x {ex.get('target_reps') or '-'}")
        sets = ex.get("sets", [])
        if sets:
            st.dataframe(pd.DataFrame(sets), hide_index=True, use_container_width=True)
        else:
            st.info("No sets logged yet.")

        with st.form(f"log_set_{ex['session_exercise_id']}"):
            weight = st.number_input("Weight (lbs)", min_value=0.0, step=5.0, key=f"w_{ex['session_exercise_id']}")
            reps = st.number_input("Reps", min_value=1, max_value=50, step=1, key=f"r_{ex['session_exercise_id']}")
            rpe = st.number_input("RPE (0-10)", min_value=0, max_value=10, value=8, step=1, key=f"rpe_{ex['session_exercise_id']}")
            log = st.form_submit_button(f"Log Set #{len(sets)+1}")
        if log:
            result = workouts.log_set(
                session_exercise_id=ex["session_exercise_id"],
                user_id=user["user_id"],
                exercise_id=ex["exercise_id"],
                weight=weight,
                reps=reps,
                rpe=rpe,
            )
            val = result["validation"]
            if val["status"] == "pr":
                st.success(f"New PR! Previous max: {val.get('expected_max') or 'n/a'}")
            elif val["status"] == "outlier":
                st.warning("Outlier detected (>15% jump). Double-check your input — could be a PR.")
            elif val["status"] == "suspicious_low":
                st.info("This looks lower than usual (>30% drop).")
            else:
                st.success("Set logged.")
            st.rerun()

    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("Mark Session Complete", use_container_width=True):
            workouts.complete_session(session_id)
            _set_flash("Session marked complete.")
            st.rerun()
    with col_right:
        with st.form(f"template_{session_id}"):
            template_name = st.text_input("Save as Template Name", value=session.get("session_name") or "Template")
            save_template = st.form_submit_button("Save Session as Template")
        if save_template:
            new_id = workouts.save_as_template(session_id, user["user_id"], template_name)
            if new_id:
                _set_flash("Template saved.")
            else:
                _set_flash("Could not save template.", kind="warn")
            st.rerun()


def render_log_workout(user: Dict[str, Any]) -> None:
    st.title("Log Workout")
    _consume_flash()

    with st.form("new_session"):
        session_name = st.text_input("Workout Name", value="New Session")
        session_date = st.date_input("Date", value=date.today())
        start_time = st.time_input("Start Time", value=None)
        duration = st.number_input("Duration (minutes)", min_value=0, max_value=300, value=60)
        create = st.form_submit_button("Create Workout Session")
    if create:
        session_id = workouts.create_session(
            user_id=user["user_id"],
            name=session_name,
            session_date=session_date,
            start_time=start_time.strftime("%H:%M:%S") if start_time else None,
            duration_minutes=int(duration) if duration else None,
        )
        st.session_state["selected_session_id"] = session_id
        st.session_state["page"] = "session_detail"
        _set_flash("Session created. Add exercises below.")
        st.rerun()

    st.markdown("### Recommended Exercises")
    recs = workouts.recommended_exercises(user["user_id"])
    if recs:
        for rec in recs:
            st.markdown(f"<span class='pill'>{rec['name']}</span>", unsafe_allow_html=True)
    else:
        st.caption("Recommendations will appear after you log a few workouts.")

    st.markdown("### Templates")
    templates = workouts.list_templates(user["user_id"])
    if templates:
        for tpl in templates:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{tpl['session_name']}** — {tpl.get('session_date')}")
            with col2:
                if st.button("Use Template", key=f"use_{tpl['session_id']}"):
                    new_id = workouts.use_template(tpl["session_id"], user["user_id"], date.today())
                    if new_id:
                        st.session_state["selected_session_id"] = new_id
                        st.session_state["page"] = "session_detail"
                        _set_flash("Template applied. Add sets to your new workout.")
                        st.rerun()
            with col3:
                st.caption("Template")
    else:
        st.caption("No templates yet.")

    st.markdown("### Recent Sessions")
    recent = workouts.list_recent_sessions(user["user_id"], limit=6)
    if recent:
        for sess in recent:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{sess['session_name']}**")
                st.caption(sess["session_date"])
            with col2:
                st.write(f"Volume: {int(sess['total_volume'])}")
            with col3:
                status = "Complete" if sess["completed"] else "In Progress"
                st.write(status)
            with col4:
                if st.button("View", key=f"view_{sess['session_id']}"):
                    st.session_state["selected_session_id"] = sess["session_id"]
                    st.session_state["page"] = "session_detail"
                    st.rerun()
    else:
        st.info("No sessions yet. Create one above.")

    if st.session_state.get("page") == "session_detail" and st.session_state.get("selected_session_id"):
        st.markdown("---")
        _render_session_detail(user, st.session_state["selected_session_id"])


# ------------------------------------------------------------------------------
# PROGRESS & ANALYTICS
# ------------------------------------------------------------------------------

def render_progress(user: Dict[str, Any]) -> None:
    st.title("Progress & Analytics")
    volume = stats.volume_by_workout(user["user_id"])
    if volume:
        df = pd.DataFrame(volume)
        df = df.sort_values("session_date")
        df_chart = df[["session_name", "volume"]].set_index("session_name")
        st.bar_chart(df_chart)
    else:
        st.info("No completed workouts yet.")

    bw = stats.bodyweight_trend(user["user_id"])
    if bw:
        df_bw = pd.DataFrame(bw).set_index("date")
        st.line_chart(df_bw["weight"])

    st.markdown("### Weekly Metrics")
    weekly = stats.weekly_metrics(user["user_id"])
    if weekly:
        st.dataframe(pd.DataFrame(weekly), use_container_width=True, hide_index=True)
    else:
        st.info("Metrics will appear after you log workouts.")

    st.markdown("### Validation History")
    validations = stats.validation_events(user["user_id"])
    if validations:
        st.dataframe(pd.DataFrame(validations), use_container_width=True, hide_index=True)
    else:
        st.caption("No validation events yet.")


# ------------------------------------------------------------------------------
# GOALS
# ------------------------------------------------------------------------------

def render_goals(user: Dict[str, Any]) -> None:
    st.title("Fitness Goals")
    with st.form("goal_form"):
        title = st.text_input("Goal Title / Description")
        goal_type = st.selectbox("Category", ["strength", "conditioning", "bodyweight", "body-fat", "streak", "other"])
        target_value = st.number_input("Target Value", min_value=0.0, step=1.0)
        unit = st.text_input("Unit", value="lbs")
        start_date = st.date_input("Start Date", value=date.today())
        use_target_date = st.checkbox("Set Target Date", value=True)
        target_date = st.date_input("Target Date", value=date.today()) if use_target_date else None
        current_value = st.number_input("Current Value", min_value=0.0, step=1.0, value=0.0)
        submitted = st.form_submit_button("Add Goal")
    if submitted:
        goal_id = goals.create_goal(
            user_id=user["user_id"],
            goal_type=goal_type,
            description=title,
            target_value=target_value,
            unit=unit,
            start_date=start_date,
            target_date=target_date,
            current_value=current_value,
        )
        _set_flash("Goal added.")
        st.rerun()

    active = goals.list_active_goals(user["user_id"])
    if not active:
        st.info("No active goals yet.")
    else:
        for goal in active:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.subheader(goal["goal_description"] or goal["goal_type"])
                st.write(f"Target: {goal['target_value']} {goal['unit']}")
                st.progress(min(goal["progress_percent"] / 100, 1.0), text=f"{goal['progress_percent']:.1f}%")
            with col2:
                with st.form(f"progress_{goal['goal_id']}"):
                    new_val = st.number_input("Update Current Value", value=float(goal.get("current_value") or 0), key=f"g_{goal['goal_id']}")
                    update = st.form_submit_button("Add Progress")
                if update:
                    goals.update_progress(goal["goal_id"], new_val)
                    _set_flash("Goal progress updated.")
                    st.rerun()
                if st.button("Mark Complete", key=f"complete_{goal['goal_id']}"):
                    goals.complete_goal(goal["goal_id"])
                    _set_flash("Goal marked complete.")
                    st.rerun()


# ------------------------------------------------------------------------------
# BODY STATS
# ------------------------------------------------------------------------------

def render_body_stats(user: Dict[str, Any]) -> None:
    st.title("Body Stats")
    with st.form("body_stats_form"):
        log_date = st.date_input("Date", value=date.today())
        weight = st.number_input("Bodyweight (lbs)", min_value=0.0, step=0.5)
        neck = st.number_input("Neck (in)", min_value=0.0, step=0.1)
        waist = st.number_input("Waist (in)", min_value=0.0, step=0.1)
        hips = st.number_input("Hips (in)", min_value=0.0, step=0.1)
        bodyfat = st.number_input("Body Fat %", min_value=0.0, max_value=80.0, step=0.1)
        notes = st.text_area("Notes", placeholder="Fast state, hydration, mood…")
        submit = st.form_submit_button("Log Stats")
    if submit:
        stats.log_body_stats(
            user_id=user["user_id"],
            log_date=log_date,
            weight=weight,
            neck=neck or None,
            waist=waist or None,
            hips=hips or None,
            body_fat_pct=bodyfat or None,
            notes=notes or None,
        )
        _set_flash("Stats logged.")
        st.rerun()

    logs = stats.list_body_stats(user["user_id"])
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
    else:
        st.info("No body stats recorded yet.")


# ------------------------------------------------------------------------------
# COMPLETED WORKOUTS
# ------------------------------------------------------------------------------

def render_completed(user: Dict[str, Any]) -> None:
    st.title("Completed Workouts")
    this_week = workouts.list_completed_sessions(user["user_id"], this_week_only=True)
    st.markdown("### This Week")
    if this_week:
        st.dataframe(pd.DataFrame(this_week), use_container_width=True, hide_index=True)
    else:
        st.caption("No completed workouts this week yet.")

    st.markdown("### All Completed")
    all_completed = workouts.list_completed_sessions(user["user_id"], this_week_only=False)
    if all_completed:
        for sess in all_completed:
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{sess['session_name']}** ({sess['session_date']})")
            with col2:
                st.write(f"Volume: {int(sess['total_volume'])}")
            with col3:
                view = st.button("View Details", key=f"view_comp_{sess['session_id']}")
                delete = st.button("Delete", key=f"del_comp_{sess['session_id']}")
                if view:
                    st.session_state["selected_session_id"] = sess["session_id"]
                    st.session_state["page"] = "session_detail"
                    st.rerun()
                if delete:
                    workouts.delete_session(sess["session_id"], user["user_id"])
                    _set_flash("Workout deleted.")
                    st.rerun()
    else:
        st.info("No completed workouts.")


# ------------------------------------------------------------------------------
# ADMIN
# ------------------------------------------------------------------------------

def render_admin(user: Dict[str, Any]) -> None:
    if user.get("user_type") != "admin":
        st.error("Admins only.")
        return

    st.title("Admin Dashboard")
    kpis = admin_service.admin_kpis()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Users", kpis["users"])
    c2.metric("Workouts Logged", kpis["workouts"])
    c3.metric("MAU (30d)", kpis["mau"])
    c4.metric("Flagged Sets", kpis["flagged_sets"])

    st.markdown("### Recent Users")
    recent = admin_service.recent_users()
    if recent:
        st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
    else:
        st.caption("No users yet.")

    st.markdown("### Exercise Library")
    exercises = admin_service.list_exercises()
    st.dataframe(pd.DataFrame(exercises), use_container_width=True, hide_index=True)

    st.markdown("**Add / Edit Exercise**")
    with st.form("exercise_form"):
        selected_id = st.selectbox(
            "Choose existing to edit (or leave blank to add new)",
            options=[0] + [ex["exercise_id"] for ex in exercises],
            format_func=lambda x: "Add New" if x == 0 else f"Edit #{x}",
        )
        name = st.text_input("Name")
        exercise_type = st.text_input("Type", value="Strength")
        subtype = st.text_input("Muscle / Subtype")
        equipment = st.text_input("Equipment")
        difficulty = st.text_input("Difficulty")
        description = st.text_area("Notes / Variations")
        submit = st.form_submit_button("Save Exercise")
    if submit:
        if selected_id == 0:
            admin_service.create_exercise(name, exercise_type, subtype or None, equipment or None, difficulty or None, description or None)
            _set_flash("Exercise added.")
        else:
            admin_service.update_exercise(selected_id, name, exercise_type, subtype or None, equipment or None, difficulty or None, description or None)
            _set_flash("Exercise updated.")
        st.rerun()


# ------------------------------------------------------------------------------
# ENTRY
# ------------------------------------------------------------------------------

def main():
    settings = get_settings()
    st.set_page_config(page_title=f"{settings.app_name} — Streamlit", layout="wide")
    apply_theme()
    _init_state()

    users = auth.list_users()
    if not users:
        st.error("No users found in the database. Please seed user_info or create a user via Django/admin.")
        return

    if not st.session_state.get("user"):
        st.session_state["user"] = _normalize_user(users[0])

    user = st.session_state["user"]

    render_nav(user, users)
    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        render_dashboard(user)
    elif page == "log_workout":
        render_log_workout(user)
    elif page == "session_detail" and st.session_state.get("selected_session_id"):
        _render_session_detail(user, st.session_state["selected_session_id"])
    elif page == "progress":
        render_progress(user)
    elif page == "goals":
        render_goals(user)
    elif page == "body_stats":
        render_body_stats(user)
    elif page == "completed":
        render_completed(user)
    elif page == "admin":
        render_admin(user)
    else:
        render_dashboard(user)


if __name__ == "__main__":
    main()