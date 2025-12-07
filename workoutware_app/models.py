"""
Database models for the WorkoutWare application.

This module defines the core relational schema for the app, mapping
fitness- and progress-related concepts to Django ORM models, including:

- `user_info`: Profile and demographic details for each user.
- `exercise`: Master catalog of exercises (name, type, equipment, etc.).
- `workout_sessions`: Individual workout sessions per user.
- `session_exercises`: Exercises assigned to a specific workout session.
- `sets`: Logged sets (weight, reps, RPE) for each exercise within a session.
- `data_validation`: Records of weight-input validation flags and outcomes.
- `progress`: Aggregated training metrics (volume, max, averages) over time.
- `user_pb`: Personal records (PRs) per user and exercise.
- `goals`: User-defined fitness goals tied optionally to an exercise.
- `user_stats_log`: Body metrics and measurements over time.
- `workout_plan`: High-level plans describing multi-day workout structure.
- `daily_workout_plan`: Daily breakdown linking sessions to plan days.
- `exercise_history_summary`: Aggregated all-time exercise statistics per user.
- `target` and `exercise_target_association`: Muscle groups / targets and
  their relationship with exercises.
- `workout_goal_link`: Links between goals and workout sessions.

All models are designed to work with a MySQL backend (via Docker container)
and are used heavily throughout the views, analytics, and Streamlit dashboard.
"""

from django.db import models


class user_info(models.Model):
    """
    Stores profile and demographic information for a user.

    This table acts as the WorkoutWare-specific user profile that links
    logically to Django's authentication user (via `username` and `email`),
    and is used as the foreign key target for most other models in this app.

    Fields:
        user_id (int): Primary key for the user_info record.
        username (str): Unique username for the user.
        first_name (str): User's first name.
        last_name (str): User's last name.
        address, town, state, country (str): Optional location details.
        email (str): Contact email and logical link to auth user.
        phone_number (str): Optional contact phone number.
        password_hash (str): Legacy / non-Django password storage.
        date_of_birth (date): Optional date of birth.
        height (Decimal): Optional height measurement.
        date_registered (date): When the profile was created.
        date_unregistered (date): When the user left the platform.
        registered (bool): Whether the account is currently active.
        fitness_goal (str): High-level description of the user's main goal.
        user_type (str): Role classification (e.g., 'member', 'coach', etc.).
    """

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=50, blank=True, null=True)
    town = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    password_hash = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date_registered = models.DateField(blank=True, null=True)
    date_unregistered = models.DateField(blank=True, null=True)
    registered = models.BooleanField(blank=True, null=True)
    fitness_goal = models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_info'

    def __str__(self) -> str:
        """Return a readable representation combining username and email."""
        return f"{self.username} ({self.email})"


class exercise(models.Model):
    """
    Master exercise catalog entry.

    Represents a single exercise definition (e.g. "Barbell Back Squat")
    that can be reused across multiple users, workout sessions, and goals.

    Fields:
        exercise_id (int): Primary key.
        name (str): Human-readable exercise name.
        type (str): High-level category (Strength, Cardio, etc.).
        subtype (str): Body region / muscle group (Chest, Legs, Back, etc.).
        equipment (str): Equipment required (Dumbbell, Barbell, Machine, etc.).
        difficulty (int): Difficulty level (numeric scale).
        description (str): Free-text instructions or notes.
        demo_link (str): Optional YouTube or external demo link.
    """

    exercise_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    subtype = models.CharField(max_length=50, blank=True, null=True)
    equipment = models.CharField(max_length=50, blank=True, null=True)
    difficulty = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    demo_link = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'exercise'

    def __str__(self) -> str:
        """Return the exercise name for admin and shell display."""
        return self.name


class workout_sessions(models.Model):
    """
    Represents a single workout session for a user.

    A workout session may be a real workout or a reusable template. Each
    session can contain multiple exercises via the `session_exercises` model.

    Fields:
        session_id (int): Primary key.
        user_id (FK user_info): The user who owns this session.
        session_name (str): Optional title, e.g. "Push Day" or "Legs A".
        session_date (date): Calendar date when the workout occurs.
        start_time, end_time (time): Optional timestamps.
        duration_minutes (int): Duration in minutes (derived or stored).
        bodyweight (Decimal): User bodyweight at the time of the session.
        completed (bool): Whether the workout is finished.
        is_template (bool): Marks this as a template instead of a real workout.
    """

    session_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    session_name = models.CharField(max_length=100, blank=True, null=True)
    session_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    bodyweight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    completed = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False)
    
    class Meta:
        managed = False
        db_table = 'workout_sessions'

    def __str__(self) -> str:
        """Return a concise label for the session."""
        base = self.session_name or f"Session {self.session_id}"
        return f"{base} on {self.session_date}"


class session_exercises(models.Model):
    """
    Intermediate model linking a workout session to specific exercises.

    Each row represents one exercise in a given session, with its own
    ordering and target sets/reps. Logged sets for this combination are
    stored in the `sets` model.

    Fields:
        session_exercise_id (int): Primary key.
        session_id (FK workout_sessions): Parent workout session.
        exercise_id (FK exercise): Exercise to be performed.
        exercise_order (int): Position in the workout (1 = first, etc.).
        target_sets (int): Planned number of sets.
        target_reps (int): Planned number of reps per set.
        completed (bool): Whether this exercise has been fully completed.
    """

    session_exercise_id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey('workout_sessions', on_delete=models.CASCADE, db_column='session_id')
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    exercise_order = models.IntegerField()
    target_sets = models.IntegerField(blank=True, null=True)
    target_reps = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'session_exercises'

    def __str__(self) -> str:
        """Return a readable representation including session and exercise."""
        return f"{self.session_id} - {self.exercise_id} (order {self.exercise_order})"


class sets(models.Model):
    """
    Logged set data for a specific exercise within a workout session.

    Each row stores a single set (weight × reps) and optional RPE and timing,
    enabling detailed tracking of training volume and intensity.

    Fields:
        set_id (int): Primary key.
        session_exercise_id (FK session_exercises): Parent exercise in session.
        set_number (int): Sequential set index (1, 2, 3, ...).
        weight (Decimal): Load used in this set (can be null for bodyweight).
        reps (int): Number of repetitions performed.
        rpe (int): Subjective difficulty rating (Rate of Perceived Exertion).
        completed (bool): Whether the set is considered valid/completed.
        is_warmup (bool): Whether the set is a warmup set.
        completion_time (datetime): Timestamp when the set was logged.
    """

    set_id = models.AutoField(primary_key=True)
    session_exercise_id = models.ForeignKey('session_exercises', on_delete=models.CASCADE, db_column='session_exercise_id')
    set_number = models.IntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reps = models.IntegerField(blank=True, null=True)
    rpe = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(default=True)
    is_warmup = models.BooleanField(default=False, blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'sets'

    def __str__(self) -> str:
        """Return a concise label describing the set."""
        return f"Set {self.set_number} ({self.weight} x {self.reps})"


class data_validation(models.Model):
    """
    Stores validation metadata for weight inputs.

    This model records how the system classified a given weight entry
    (e.g., normal, outlier, new PR, suspicious low), along with any
    expected maximum and user action taken.

    Fields:
        validation_id (int): Primary key.
        user_id (FK user_info): User who logged the set.
        set_id (FK sets): The associated set, if applicable.
        exercise_id (FK exercise): Exercise the weight belongs to.
        input_weight (Decimal): Weight entered by the user.
        expected_max (Decimal): Previous max weight (used for comparison).
        flagged_as (str): Category, e.g. 'normal', 'outlier', 'new_pr'.
        user_action (str): How user responded in the UI (if tracked).
        timestamp (datetime): When the validation entry was recorded.
    """

    validation_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    set_id = models.ForeignKey('sets', on_delete=models.SET_NULL, db_column='set_id', null=True, blank=True)
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    input_weight = models.DecimalField(max_digits=6, decimal_places=2)
    expected_max = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    flagged_as = models.CharField(max_length=20, blank=True, null=True)
    user_action = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'data_validation'

    def __str__(self) -> str:
        """Return a descriptive summary for debugging/analytics."""
        return f"Validation #{self.validation_id} - {self.flagged_as}"


class progress(models.Model):
    """
    Aggregated training progress metrics for a user and exercise.

    Each record summarizes performance over a given period (daily or weekly),
    enabling charts and analytics in the Progress dashboard.

    Fields:
        progress_id (int): Primary key.
        user_id (FK user_info): User this record belongs to.
        exercise_id (FK exercise): Exercise summarized.
        date (date): Start date or reference date for the period.
        period_type (str): Granularity, e.g. 'daily', 'weekly'.
        max_weight (Decimal): Maximum weight lifted in the period.
        avg_weight (Decimal): Average working weight.
        total_volume (Decimal): Sum of (weight × reps) across sets.
        workout_count (int): Number of sessions contributing to this row.
    """

    progress_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    date = models.DateField()
    period_type = models.CharField(max_length=20)
    max_weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    avg_weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    total_volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    workout_count = models.IntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'progress'

    def __str__(self) -> str:
        """Return a readable label with user, exercise, and period."""
        return f"Progress for {self.user_id} - {self.exercise_id} ({self.period_type} @ {self.date})"


class user_pb(models.Model):
    """
    Personal record (PR) table for user achievements.

    Tracks best performances (e.g., 1RM estimates, max weight for a lift)
    along with historical previous PR values and notes.

    Fields:
        pr_id (int): Primary key.
        user_id (FK user_info): User who owns this PR.
        exercise_id (FK exercise): Exercise this PR relates to.
        pr_type (str): Type of PR (e.g., 'max_weight').
        pb_weight (Decimal): Best weight lifted.
        pb_reps (int): Reps completed at pb_weight.
        pb_time (time): Optional, for time-based PRs.
        pb_date (date): Date when the PR was achieved.
        previous_pr (Decimal): Previous best value (if any).
        notes (str): Free-text notes, often including set IDs or context.
    """

    pr_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    pr_type = models.CharField(max_length=20)
    pb_weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    pb_reps = models.IntegerField(blank=True, null=True)
    pb_time = models.TimeField(blank=True, null=True)
    pb_date = models.DateField()
    previous_pr = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_pb'

    def __str__(self) -> str:
        """Return a short description of the PR."""
        return f"PR {self.pr_type} for {self.user_id} on {self.pb_date}"


class goals(models.Model):
    """
    User-defined fitness goals.

    A goal can be numeric (e.g. squat 200 lbs, lose 5 kg) and optionally
    tied to a specific exercise. Status and completion dates are tracked
    for progress monitoring.

    Fields:
        goal_id (int): Primary key.
        user_id (FK user_info): Owner of the goal.
        goal_type (str): Category, e.g. 'strength', 'weight_loss'.
        goal_description (str): Detailed description of the goal.
        target_value (Decimal): Target numeric value (e.g., 200.0).
        current_value (Decimal): Current measure toward the target.
        unit (str): Unit of measurement (kg, lbs, %, etc.).
        exercise_id (FK exercise, nullable): Relevant exercise, if any.
        start_date (date): When the goal starts being tracked.
        target_date (date): Optional deadline for the goal.
        status (str): 'active', 'completed', 'abandoned', etc.
        completion_date (date): When the goal was completed.
    """

    goal_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    goal_type = models.CharField(max_length=100)
    goal_description = models.TextField(blank=True, null=True)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    current_value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=20)
    exercise_id = models.ForeignKey('exercise', on_delete=models.SET_NULL, db_column='exercise_id', null=True, blank=True)
    start_date = models.DateField()
    target_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, default='active')
    completion_date = models.DateField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'goals'

    def __str__(self) -> str:
        """Return a readable label combining type and user."""
        return f"{self.goal_type} ({self.user_id})"


class user_stats_log(models.Model):
    """
    Logs body measurements and body composition metrics over time.

    These records are used to visualize trends such as weight change
    or circumferences, and to support transformation tracking.

    Fields:
        log_id (int): Primary key.
        user_id (FK user_info): Owner of the log entry.
        date (date): Date of measurement.
        weight (Decimal): Bodyweight.
        neck, waist, hips (Decimal): Circumference measurements.
        body_fat_percentage (Decimal): Optional body fat estimate.
        notes (str): Free-text notes (e.g., conditions, mood, etc.).
    """

    log_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    neck = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    waist = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hips = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'user_stats_log'

    def __str__(self) -> str:
        """Return a simple identifier for the log entry."""
        return f"Stats for {self.user_id} on {self.date}"


class workout_plan(models.Model):
    """
    High-level workout plan metadata.

    A plan can describe a multi-day split or macro-structure assigned
    to a user, independent of individual `workout_sessions`.

    Fields:
        plan_id (int): Primary key.
        user_id (FK user_info): Owner of the plan.
        plan_description (str): Narrative description of the plan.
        plan_type (str): Category (e.g., 'hypertrophy', 'strength block').
        number_of_days (int): Days per week or total days in the cycle.
    """

    plan_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    plan_description = models.TextField(blank=True, null=True)
    plan_type = models.CharField(max_length=50, blank=True, null=True)
    number_of_days = models.IntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'workout_plan'

    def __str__(self) -> str:
        """Return a readable label combining user and type."""
        return f"Plan for {self.user_id} ({self.plan_type})"


class target(models.Model):
    """
    Muscle group or training target.

    Represents a body part, movement pattern, or training focus area
    that exercises can be associated with.

    Fields:
        target_id (int): Primary key.
        target_name (str): Name of the target (e.g., 'Quadriceps').
        target_group (str): Grouping/category (e.g., 'Lower Body').
        target_function (str): Functional role or classification.
    """

    target_id = models.AutoField(primary_key=True)
    target_name = models.CharField(max_length=50)
    target_group = models.CharField(max_length=50, blank=True, null=True)
    target_function = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'target'

    def __str__(self) -> str:
        """Return the target name."""
        return self.target_name


class exercise_target_association(models.Model):
    """
    Link table between exercises and targets (muscle groups).

    Enables a many-to-many relationship so that each exercise can train
    multiple targets, and each target can be trained by multiple exercises.

    Fields:
        association_id (int): Primary key.
        exercise_id (FK exercise): The exercise in question.
        target_id (FK target): The muscle group / target trained.
        intensity (str): Qualitative intensity/priority (e.g., 'primary', 'secondary').
    """

    association_id = models.AutoField(primary_key=True)
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    target_id = models.ForeignKey('target', on_delete=models.CASCADE, db_column='target_id')
    intensity = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'exercise_target_association'

    def __str__(self) -> str:
        """Return a descriptive label for the association."""
        return f"{self.exercise_id} → {self.target_id} ({self.intensity or 'unspecified'})"


class daily_workout_plan(models.Model):
    """
    Daily breakdown of a workout plan.

    Links individual workout sessions to specific days within a multi-day
    workout plan structure.

    Fields:
        daily_plan_id (int): Primary key.
        workout_plan_id (FK workout_plan): Parent workout plan.
        day (int): Day number in the plan cycle.
        wk_day (str): Optional day of week name (e.g., 'Monday').
        session_id (FK workout_sessions): The workout session for this day.
    """

    daily_plan_id = models.AutoField(primary_key=True)
    workout_plan_id = models.ForeignKey('workout_plan', on_delete=models.CASCADE, db_column='workout_plan_id')
    day = models.IntegerField()
    wk_day = models.CharField(max_length=50, blank=True, null=True)
    session_id = models.ForeignKey('workout_sessions', on_delete=models.SET_NULL, db_column='session_id', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'daily_workout_plan'

    def __str__(self) -> str:
        """Return a readable label for the daily plan."""
        day_name = self.wk_day or f"Day {self.day}"
        return f"{self.workout_plan_id} - {day_name}"


class exercise_history_summary(models.Model):
    """
    Aggregated exercise history and statistics per user.

    Provides a summary view of all-time training metrics for each
    exercise a user has performed, useful for quick lookups and analytics.

    Fields:
        summary_id (int): Primary key.
        user_id (FK user_info): User this summary belongs to.
        exercise_id (FK exercise): Exercise being summarized.
        total_workouts (int): Total number of workouts including this exercise.
        total_sets (int): Total sets logged across all time.
        total_reps (int): Total reps performed across all time.
        lifetime_volume (Decimal): Cumulative volume (weight × reps).
        current_pr (Decimal): Current personal record for this exercise.
        last_workout_date (date): Most recent workout date for this exercise.
    """

    summary_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    total_workouts = models.IntegerField(default=0)
    total_sets = models.IntegerField(default=0)
    total_reps = models.IntegerField(default=0)
    lifetime_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    current_pr = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    last_workout_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exercise_history_summary'

    def __str__(self) -> str:
        """Return a readable summary label."""
        return f"Summary for {self.user_id} - {self.exercise_id}"


class workout_goal_link(models.Model):
    """
    Link table between goals and workout sessions.

    Tracks which goals are associated with which workout sessions,
    enabling progress tracking toward specific fitness objectives.

    Fields:
        id (int): Primary key.
        user_id (FK user_info): Owner of both the goal and session.
        goal (FK goals): The fitness goal being tracked (nullable).
        session (FK workout_sessions): The workout session contributing to the goal.
        created_at (datetime): When the link was created.
    """

    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    goal = models.ForeignKey('goals', on_delete=models.SET_NULL, db_column='goal', null=True, blank=True)
    session = models.ForeignKey('workout_sessions', on_delete=models.CASCADE, db_column='session')
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'workout_goal_link'

    def __str__(self) -> str:
        """Return a descriptive label for the goal-session link."""
        return f"Goal {self.goal_id if self.goal else 'None'} linked to Session {self.session_id}"