# Workoutware Streamlit Implementation Plan

Purpose: deliver a Streamlit-based client that replicates the full user/admin experience shown in the snapshots and defined in `product_requirements.md`, reusing the existing MySQL schema and Django data where possible.

## Current State (from repo review)
- Django app (`workoutware_app`) with models matching the ERD (users, workouts, session_exercises, sets, validation, progress, PRs, goals, stats, templates, targets).
- Django templates implement the user-facing flows seen in snapshots.
- `streamlit_app.py` is an internal analytics dashboard (dev-only) that reads MySQL directly; it is not the end-user UI.
- SQL folder contains schema/data setup; README references MySQL container with root credentials.

## Gap Summary vs PRD
- Streamlit lacks: auth (login/signup), user dashboards, workout logging UX, templates, recommendations, goals UI, body stats logging, progress charts/tables, completed workouts views, admin exercise library UI, and validation messaging.
- Data model alignment is good; we need a Streamlit data/service layer that mirrors Django access patterns and enforces validation rules (PR/outlier thresholds).
- Theming: must match the dark/teal UI patterns outlined in PRD; current Streamlit app uses default theme.

## Architectural Approach
- Use Streamlit as the front-end only; connect directly to MySQL (reuse connection helper pattern from `streamlit_app.py` but move to a shared module with env-driven config).
- Implement lightweight auth/session handling in Streamlit (hashed passwords via Django auth tables or custom users table; consider JWT-like cookies or Streamlit session_state with secure checks).
- Create a small service layer for CRUD (users, workouts, exercises, goals, stats, templates) to avoid raw SQL duplication.
- Encapsulate validation logic (PR detection, outlier thresholds) in a utility module shared by set logging and progress.
- Theming via `st.set_page_config` and custom CSS injected at app start to mirror snapshots.

## Milestones & Tasks
### M1: Foundations
- Add config/env handling for DB creds; centralize connection factory with retries.
- Set up shared UI shell (global CSS, layout, icon set, button styles) to match palette/typography.
- Build navigation structure (sidebar or tabbed) mirroring main flows.

### M2: Authentication
- Implement signup with validation rules; store users; hash passwords; enforce unique usernames/emails.
- Implement login/logout; session management; access control per role (member vs admin).
- Error/success messaging in the themed style; routing to dashboard after auth.

### M3: Member Dashboard
- KPIs: day streak, workouts this week, total workouts, recent PRs.
- Quick actions: log workout, view progress, manage goals, log body stats.
- Recent PR cards and active goals list with progress bars.

### M4: Workout Sessions & Sets
- New session form (name, date, time, duration, goal notes); status in-progress/complete.
- Recommended exercises chips based on recent frequency.
- Templates: list, use, edit, delete; save session as template.
- Session detail: add exercises (targets), log sets (weight/reps/RPE), completed sets table.
- Set confirmation page with validation banners (PR, outlier >15%, suspicious low >30%, normal).

### M5: Completed Workouts
- “This Week” view with detail link; “All Completed” list with view/delete.
- Workout detail view (per session) showing exercises, sets, totals.

### M6: Goals
- Create goal form (strength/conditioning/weight-loss/body-fat/plank/etc.).
- Active goals display with progress bars; add progress updates; status handling.

### M7: Body Stats
- Log measurements form (weight, neck, waist, hips, body fat %, notes) with date picker.
- Historical table/chart integration into Progress.

### M8: Progress & Analytics
- Charts: total volume per workout, bodyweight trend.
- Tables: weekly metrics (volume, avg RPE, sets/reps, validation status); recent validation checks.
- Recommendations block (selected muscle groups last 30 days).

### M9: Admin Experience
- Admin dashboard KPIs (total users, workouts logged, MAU, flagged sets).
- Recent users grid.
- Exercise library CRUD with table actions (edit/delete) and add form (name, muscle, equipment, level/type, defaults).

### M10: Hardening & QA
- Input validation and error handling across forms.
- Permission checks for admin-only pages/actions.
- Caching strategy for reads; cache invalidation on writes.
- Smoke tests for DB connectivity and critical flows (login, create session, log set, create goal).

## Data & Validation Rules to Implement
- PR/outlier/suspicious thresholds: PR when weight > previous max; outlier when >15% jump; suspicious low when >30% below average; normal otherwise.
- Workout status: `in_progress` vs `complete`; templates flagged with `is_template`.
- Goal progress updates must recalc percentage and current vs target values.
- Template usage should clone content; saving changes requires explicit overwrite.
- Deleting workouts/goals/templates should confirm before commit.

## Deliverables
- Streamlit app code organized into modules: `config.py` (env), `db.py` (connections), `services/` (CRUD + validation), `ui/` (components/pages), main `app.py`.
- Themed UI matching snapshot patterns.
- Documentation updates: how to run, required env vars, and feature list aligned with PRD.

## Open Questions / Assumptions
- Auth source: reuse Django auth tables or maintain separate auth in Streamlit schema?
- Email requirements (verification/reset) not shown; assume out of scope unless requested.
- Deployment target: local only or hosted (impacts secrets management).

## Plan ↔ PRD / Snapshot / Codebase Alignment
- **Auth**: Milestone covers login/signup/session mgmt; matches PRD and login/signup snapshots; no such flow in current Streamlit app.
- **Dashboard**: KPIs, quick actions, PRs, active goals planned; aligns with dashboard snapshot and PRD; not present in current Streamlit app.
- **Workouts & Sets**: Session creation, recommendations, templates, set logging, validation feedback included; matches log workout/add exercise/set logged snapshots and PRD; Django templates exist but Streamlit app does not.
- **Completed Workouts**: This-week and all-time lists with view/delete covered; aligns with PRD and snapshots; not in current Streamlit app.
- **Goals**: Create/manage goals with progress bars and updates; matches PRD and fitness goals snapshot; data present in Django models.
- **Body Stats**: Logging form and integration with progress; matches PRD and log body stats snapshot; data model present.
- **Progress/Analytics**: Volume chart, bodyweight trend, weekly metrics, validation checks, recommendations; matches PRD and progress snapshot; current Streamlit app has partial analytics but lacks PRD visuals and flows.
- **Admin**: KPIs, recent users, exercise library CRUD; matches PRD and admin snapshot; requires new Streamlit UI though Django templates exist.
- **UI/Theming**: Custom CSS requirement noted to mirror dark/teal palette from PRD UI patterns; current Streamlit uses default theme.
- **Data Model**: Plan assumes reuse of existing MySQL schema (models.py) which aligns with PRD conceptual model; no new tables required beyond existing ERD.
- **Out-of-scope/Optional**: Django has a leaderboard template not shown in PRD/snapshots; defer unless requested.
