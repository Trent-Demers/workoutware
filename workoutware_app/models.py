from django.db import models

class user_info(models.Model):
    user_id = models.IntegerField(primary_key=True)
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
    registered = models.BooleanField(default=True)
    fitness_goal = models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_info'

class exercise(models.Model):
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

class workout_sessions(models.Model):
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

class session_exercises(models.Model):
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

class sets(models.Model):
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

class data_validation(models.Model):
    validation_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    set_id = models.ForeignKey('sets', on_delete=models.SET_NULL, db_column='set_id', null=True, blank=True)
    exercise_id = models.ForeignKey('exercise', on_delete=models.CASCADE, db_column='exercise_id')
    input_weight = models.DecimalField(max_digits=6, decimal_places=2)
    expected_max = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    flagged_as = models.CharField(max_length=20, blank=True, null=True)
    user_action = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = 'data_validation'

class progress(models.Model):
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

# NEW MODELS - Using your existing tables
class user_pb(models.Model):
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

class goals(models.Model):
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

class user_stats_log(models.Model):
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

class workout_plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('user_info', on_delete=models.CASCADE, db_column='user_id')
    plan_description = models.TextField(blank=True, null=True)
    plan_type = models.CharField(max_length=50, blank=True, null=True)
    number_of_days = models.IntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'workout_plan'