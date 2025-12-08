# Workoutware Streamlit Product Requirements

## Purpose and Scope
Build a full-featured fitness tracking web app in Streamlit that mirrors the provided UI/UX and flows. Core capabilities: authentication, workout session creation and completion, exercise/set logging with validation and PR tracking, templates and recommendations, goal management, body measurements, progress analytics, completed workout history, and admin exercise library management. No Streamlit code is requested here; this document defines behaviors and flows to be replicated.

## User Roles
- **Member/User**: Logs workouts, sets, body stats; manages goals; views analytics and history.
- **Admin**: All member capabilities plus exercise library CRUD and monitoring of platform usage and flagged sets.

## Functional Requirements

### Authentication
- Login form: username, password, submit CTA, link to signup.
- Signup form: username (<=150 chars, alphanumerics and @/./+/-/_), email, password + confirm with rules (>=8 chars, not common, not similar to personal info, not entirely numeric), submit CTA, link to login.

### Member Dashboard
- Greeting with username and subtitle describing tracked metrics.
- KPI tiles: `Day Workout Streak`, `Workouts This Week`, `Total Workouts`, `Recent PRs`.
- Quick actions: `Log Workout`, `View Progress`, `Manage Goals`, `Log Body Stats`.
- Recent personal records: list of latest PRs (exercise name, weight/time, date).
- Active goals: list with goal title and target (e.g., weight/time/volume), progress bars, and status text.

### Workout Sessions
- **Start New Session**: fields for workout name, date, start time, time worked out today (hrs), optional goal linkage/notes; CTA `Create Workout Session`.
- **Recommended Exercises**: pill chips of recently used exercises to quickly add to session.
- **Templates**: list of templates with title, description/notes, `Use` action plus edit/delete controls.
- **Recent Workout Sessions**: list with workout name, date/time, duration, volume, status (`In Progress`/`Complete`), actions `View`, `Complete`, `Delete`.
- **Session Detail (Add Exercise)**:
  - Header with workout name and date; controls: back to log workout, view progress, save as template.
  - Form to add exercise: dropdown select exercise, target sets, target reps, CTA `Add Exercise`.
  - For each exercise in session: show target sets/reps; form to log next set with fields weight (lbs), reps, RPE (0–10), CTA `Log Set #n`; completed sets table with columns Set #, Weight, Reps, RPE.
- **Set Logged Confirmation**:
  - Success banner and set details (exercise, weight, reps, RPE, set number).
  - Smart validation & PR tracking statuses:
    - New PR: celebrate when beating previous max.
    - Outlier: flag unrealistically high jump (>15% increase).
    - Suspicious Low: flag >30% below average.
    - Normal: within expected range.

### Completed Workouts
- **This Week**: page showing completed sessions in the current week; each card includes name, date, and `View Workout Details`; controls to go back to dashboard and to progress.
- **All Completed**: list of all completed workouts; each card shows workout name, status (`complete`), date/time, duration/volume summary, actions `View Details` and `Delete`.

### Fitness Goals
- Create goal form: goal title, start date, target date, target metric/type, target value, initial/current value (optional), target sets/reps when relevant, CTA `Add Goal`.
- Active goals list: each goal shows title, target metric, progress bar with percentage and current vs target values; action `Add Progress`.
- Goal categories seen: strength (bench/squat/deadlift), conditioning (1 mile under X), body weight/fat %, plank time, weekly exercise streaks.

### Body Stats
- Log measurements form: date, bodyweight (lbs), neck (in), waist (in), hips (in), body fat %, notes; CTA `Log Stats`.
- Empty state messaging when no stats logged.
- Quick links: back to dashboard, view progress.

### Progress & Analytics
- Charts:
  - Total volume per workout (bar chart by workout name).
  - Bodyweight trend (line chart over time).
- Recommendations: text block highlighting selected muscle groups (last 30 days).
- Weekly progress metrics table: columns for workout, duration, volume, avg RPE, total sets, total reps, validation flag/result, and other key stats.
- Recent validation checks table: shows per-workout validation status (e.g., normal/outlier/PR/suspicious) with timestamps.

### Admin Dashboard
- KPIs: total users, workouts logged, monthly active users, flagged sets; logout control.
- Recent users grid: username, last login, last workout.
- Exercise library management:
  - Add exercise form fields: exercise name, muscle group, equipment, level, type/movement, default sets, default reps, default RPE/effort, and notes/variation (as shown).
  - Current exercises table: columns ID, name, muscle, equipment, level, type, default sets/reps/RPE; actions `Edit` and `Delete` per row.

## User Flows
- Signup → login → land on dashboard.
- From dashboard: choose a quick action (log workout, view progress, manage goals, log body stats).
- Log workout:
  1) Create session with name/date/time/goal.  
  2) Optionally choose recommended exercises or a template.  
  3) Add exercises with target sets/reps.  
  4) Log sets with weight/reps/RPE; view completed sets table and validation feedback.  
  5) Save workout as template (if desired) and mark session complete.
- Log a set: submit weight/reps/RPE → see success page with validation/PR result → return to workout.
- Goals: create goal → see in active list with progress bar → add progress updates over time.
- Body stats: open body stats page → enter measurements → save → data surfaces in progress analytics.
- Progress: view charts, recommendations, weekly metrics, validation history; navigate back to dashboard.
- Completed workouts: review this week’s or all-time; view details or delete.
- Admin: monitor KPIs and recent users; add/edit/delete exercises in library; review flagged sets metric.

## Data Model (conceptual)
- User: id, username, email, password hash, role, last_login, last_workout_at.
- WorkoutSession: id, user_id, name, date, start_time, duration, status (in_progress/complete), volume, linked_goal_id, notes, created_from_template_id.
- Exercise: id, name, muscle_group, equipment, level, type/movement, default_sets, default_reps, default_rpe, notes/variation, active flag.
- SessionExercise: id, session_id, exercise_id, target_sets, target_reps, order.
- SetEntry: id, session_exercise_id, set_number, weight, reps, rpe, validation_status (normal/pr/outlier/suspicious_low), created_at.
- Goal: id, user_id, title, category, start_date, target_date, target_metric, target_value, current_value, progress_percent, status.
- BodyStat: id, user_id, date, bodyweight, neck, waist, hips, body_fat_pct, notes.
- Template: id, user_id, name, notes, exercises (composed of sets/reps), is_default flag.
- RecommendationLog/ValidationCheck: id, user_id, session_id, status, context, created_at.

## Validation & Business Rules
- Password constraints per signup screen.
- Set validation thresholds: outlier >15% increase over baseline; suspicious low >30% below average; PR when exceeding previous max; normal otherwise.
- Workout statuses: in_progress vs complete; deleting should prompt confirmation.
- Goal progress must update progress bars and percentages.
- Template use pre-fills session data; edits do not overwrite original template unless explicitly saved.

## Non-Functional Requirements
- UX: Match dark theme, teal/green accent, iconography, spacing, and CTA prominence from snapshots.
- Accessibility: form labels, focus states, keyboard navigation for dropdowns/buttons.
- Performance: snappy page loads and instant feedback on form submissions; cache charts where feasible.
- Audit: track created/updated timestamps and actor for admin CRUD actions.
- Security: authenticated access for member features; role-based gating for admin dashboard and exercise library.

## Navigation Map
- Auth: Login ↔ Signup.
- Dashboard (home) → Log Workout → Session Detail → Set Confirmation → back to Dashboard.
- Dashboard → View Progress (charts/tables/recommendations).
- Dashboard → Manage Goals (create/manage).
- Dashboard → Log Body Stats.
- Dashboard → Completed Workouts (all) and Completed This Week.
- Admin Dashboard → Exercise Library (add/edit/delete) and metrics.

## UI Design Patterns (to replicate visually)
- **Palette**: dark background (#0c1116–#101820), card surfaces slightly lighter (#111b21–#152028); primary accent teal/emerald gradient (#0ad7b3 → #05b883); secondary accent green (#13c27b) for success; warning amber (#f7a736); danger red (#e05c57) for deletes; neutral text light gray (#d7e0e7) with secondary muted gray (#7b8a92); dividers/borders subtle (#1c2a32).
- **Typography**: bold, uppercase headers for sections and buttons; clean sans-serif (e.g., Montserrat/SemiBold for headings, Regular for body); letter spacing on titles; numeric KPIs large and high-contrast.
- **Cards/Surfaces**: soft rounded corners (8–12px), subtle inner shadow/glow, consistent padding; card headers often icon + label in uppercase.
- **Buttons**: primary CTAs use horizontal teal gradient, white text, bold uppercase; hover states slightly brighter; secondary buttons outlined in accent teal with transparent fill; danger buttons solid muted red with white text.
- **Inputs**: dark fields with light borders and subtle glow on focus; placeholders light gray; form labels uppercase, small, muted; dropdowns with caret icon.
- **Chips/Pills**: rounded pills for recommendations and statuses; accent-colored text on muted background; status pills (e.g., `complete`, `in progress`) use green/yellow with uppercase text.
- **Progress Bars**: thick bars with accent fill; include percentage text and label (current vs target).
- **Tables/Lists**: zebra-free dark rows; thin separators; rows contain title + metadata (date, duration, volume) and right-aligned action buttons; validation status column uses colored text.
- **KPIs**: tiles with icon + metric count and caption; even spacing and consistent size.
- **Navigation/Links**: text links in teal with small inline icons; back links styled as ghost buttons with outline and icon.
- **Feedback**: success banners with check icon and teal text; validation legend uses colored icons (green check, yellow warning, amber alert, teal star for PR).
