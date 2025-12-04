from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db import connection
from django.db.models import Sum, Avg, Max, Count, Q
from django.http import JsonResponse
from .models import (user_info, exercise, workout_sessions, session_exercises, 
                     sets, data_validation, progress, user_pb, goals, user_stats_log, target, exercise_target_association)
from .recommendations import get_workout_recommendations
from datetime import datetime, date, timedelta
from decimal import Decimal
from collections import defaultdict
import json

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_user_record(request_user):
    """Get or create user_info record for Django auth user"""
    try:
        return user_info.objects.get(email=request_user.email)
    except user_info.DoesNotExist:
        return user_info.objects.create(
            first_name=request_user.first_name or request_user.username,
            last_name=request_user.last_name or '',
            email=request_user.email,
            password_hash='django_auth',
            registered=True,
            date_registered=date.today()
        )

def calculate_workout_streak(user_id):
    """Calculate consecutive workout days"""
    sessions = workout_sessions.objects.filter(
        user_id=user_id,
        completed=True,
        is_template=False
    ).order_by('-session_date').values_list('session_date', flat=True)
    
    if not sessions:
        return 0
    
    sessions_list = list(sessions)
    streak = 1
    
    for i in range(len(sessions_list) - 1):
        days_diff = (sessions_list[i] - sessions_list[i + 1]).days
        if days_diff == 1:
            streak += 1
        else:
            break
    
    return streak

def get_exercise_suggestions(user_id):
    """Get exercises user hasn't done recently"""
    recent_exercises = session_exercises.objects.filter(
        session_id__user_id=user_id,
        session_id__session_date__gte=date.today() - timedelta(days=7),
        session_id__is_template=False
    ).values_list('exercise_id', flat=True).distinct()
    
    suggestions = exercise.objects.exclude(
        exercise_id__in=recent_exercises
    ).order_by('?')[:5]
    
    return suggestions

def check_and_record_pr(user_id, exercise_id, weight, reps, set_obj):
    """Check if this is a PR and record it"""
    existing_pr = user_pb.objects.filter(
        user_id=user_id,
        exercise_id=exercise_id,
        pr_type='max_weight'
    ).first()
    
    if existing_pr:
        if weight > existing_pr.pb_weight:
            user_pb.objects.create(
                user_id=user_info.objects.get(user_id=user_id),
                exercise_id=exercise.objects.get(exercise_id=exercise_id),
                pr_type='max_weight',
                pb_weight=weight,
                pb_reps=reps,
                pb_date=date.today(),
                previous_pr=existing_pr.pb_weight,
                notes=f'Set ID: {set_obj.set_id}'
            )
            return True, existing_pr.pb_weight
    else:
        user_pb.objects.create(
            user_id=user_info.objects.get(user_id=user_id),
            exercise_id=exercise.objects.get(exercise_id=exercise_id),
            pr_type='max_weight',
            pb_weight=weight,
            pb_reps=reps,
            pb_date=date.today(),
            notes=f'Set ID: {set_obj.set_id}'
        )
        return True, None
    
    return False, None

def validate_weight_input(user_id, exercise_id, input_weight):
    """Smart validation"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MAX(s.weight) as max_weight,
                   AVG(s.weight) as avg_weight
            FROM sets s
            JOIN session_exercises se ON s.session_exercise_id = se.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s 
              AND se.exercise_id = %s
              AND s.weight IS NOT NULL
              AND ws.is_template = 0
        """, [user_id, exercise_id])
        
        result = cursor.fetchone()
        
        if result[0] is None:
            return {
                'flag': 'first_time',
                'message': '🌟 First time logging this exercise! Great start!',
                'expected_max': None
            }
        
        max_weight = Decimal(str(result[0]))
        avg_weight = Decimal(str(result[1]))
        
        if input_weight > max_weight * Decimal('1.15'):
            return {
                'flag': 'outlier',
                'message': f'⚠️ {input_weight} lbs is {input_weight - max_weight:.1f} lbs more than your max ({max_weight} lbs). Verify?',
                'expected_max': max_weight
            }
        elif input_weight > max_weight:
            return {
                'flag': 'new_pr',
                'message': f'🎉 NEW PR! {input_weight} lbs is {input_weight - max_weight:.1f} lbs more than your previous max!',
                'expected_max': max_weight
            }
        elif input_weight < avg_weight * Decimal('0.7'):
            return {
                'flag': 'suspicious_low',
                'message': f'⚠️ {input_weight} lbs is unusually low (your average is {avg_weight:.1f} lbs). Correct?',
                'expected_max': max_weight
            }
        else:
            return {
                'flag': 'normal',
                'message': f'✓ Looks good! Within your typical range.',
                'expected_max': max_weight
            }


# ============================================================================
# MAIN VIEWS
# ============================================================================

@login_required
def home(request):
    """Enhanced dashboard with stats, PRs, and goals"""
    if request.user.is_superuser:
        # ADMIN DASHBOARD
        from django.db.models import Count
        
        total_users = user_info.objects.count()
        total_exercises = exercise.objects.count()
        total_workouts = workout_sessions.objects.filter(completed=True, is_template=False).count()
        
        # MySQL-compatible way to count distinct users active today
        active_today_sessions = workout_sessions.objects.filter(
            session_date=date.today(),
            completed=True,
            is_template=False
        ).values_list('user_id', flat=True)
        active_today = len(set(active_today_sessions))
        
        recent_users = user_info.objects.order_by('-date_registered')[:6]
        exercises = exercise.objects.all()
        
        popular_exercises = exercise.objects.annotate(
            usage_count=Count('session_exercises', filter=Q(session_exercises__session_id__is_template=False))
        ).order_by('-usage_count')[:5]
        
        context = {
            'total_users': total_users,
            'total_exercises': total_exercises,
            'total_workouts': total_workouts,
            'active_today': active_today,
            'recent_users': recent_users,
            'exercises': exercises,
            'popular_exercises': popular_exercises,
        }
        
        return render(request, 'admin_dashboard.html', context)
    
    # USER DASHBOARD
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id
    
    streak_days = calculate_workout_streak(user_id)
    
    # Get unique PRs (only best per exercise)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.name as exercise_name,
                pb.pb_weight,
                pb.pb_date,
                pb.previous_pr
            FROM user_pb pb
            INNER JOIN exercise e ON pb.exercise_id = e.exercise_id
            WHERE pb.user_id = %s
              AND pb.pr_id IN (
                  SELECT MAX(pr_id) 
                  FROM user_pb 
                  WHERE user_id = %s 
                  GROUP BY exercise_id
              )
            ORDER BY pb.pb_date DESC
            LIMIT 5
        """, [user_id, user_id])
        
        prs_data = cursor.fetchall()
        recent_prs = []
        for row in prs_data:
            pr_dict = {
                'exercise_name': row[0],
                'pb_weight': row[1],
                'pb_date': row[2],
                'previous_pr': row[3],
                'improvement': row[1] - row[3] if row[3] else 0
            }
            recent_prs.append(pr_dict)
    
    active_goals = goals.objects.filter(
        user_id=user_id,
        status='active'
    ).select_related('exercise_id')[:3]
    
    for goal in active_goals:
        if goal.exercise_id:
            latest_pr = user_pb.objects.filter(
                user_id=user_id,
                exercise_id=goal.exercise_id,
                pr_type='max_weight'
            ).order_by('-pb_date').first()
            
            if latest_pr:
                goal.current_value = latest_pr.pb_weight
                goal.save()
    
    week_start = date.today() - timedelta(days=date.today().weekday())
    workouts_this_week = workout_sessions.objects.filter(
        user_id=user_id,
        session_date__gte=week_start,
        completed=True,
        is_template=False
    ).count()
    
    total_workouts = workout_sessions.objects.filter(
        user_id=user_id,
        completed=True,
        is_template=False
    ).count()
    
    context = {
        'streak_days': streak_days,
        'recent_prs': recent_prs,
        'active_goals': active_goals,
        'workouts_this_week': workouts_this_week,
        'total_workouts': total_workouts,
    }
    
    return render(request, 'user_dashboard.html', context)

@login_required
def add_exercise(request):
    """Admin: Add new exercise"""
    new_exercise = exercise(
        name=request.POST.get('exercise_name'),
        type=request.POST.get('exercise_type'),
        subtype=request.POST.get('exercise_subtype'),
        equipment=request.POST.get('exercise_equipment'),
        difficulty=request.POST.get('exercise_difficulty'),
        description=request.POST.get('exercise_description'),
        demo_link=request.POST.get('exercise_demo'),
    )
    new_exercise.save()
    return redirect('/')

@login_required
def edit_exercise(request, exercise_id):
    """Admin: Edit existing exercise"""
    if not request.user.is_superuser:
        return redirect('/')
    
    ex = get_object_or_404(exercise, exercise_id=exercise_id)
    ex.name = request.POST.get('exercise_name')
    ex.type = request.POST.get('exercise_type')
    ex.subtype = request.POST.get('exercise_subtype')
    ex.equipment = request.POST.get('exercise_equipment')
    ex.difficulty = request.POST.get('exercise_difficulty')
    ex.description = request.POST.get('exercise_description')
    ex.demo_link = request.POST.get('exercise_demo')
    ex.save()
    return redirect('/')

@login_required
def delete_exercise(request, exercise_id):
    """Admin: Delete exercise"""
    if not request.user.is_superuser:
        return redirect('/')
    
    ex = get_object_or_404(exercise, exercise_id=exercise_id)
    ex.delete()
    return redirect('/')

@login_required
def log_workout(request):
    """Display workout logging interface"""
    exercises_list = exercise.objects.all()
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id
    
    # Get recent sessions (excluding templates)
    recent_sessions = workout_sessions.objects.filter(
        user_id=user_id,
        completed=True,
        is_template=False
    ).order_by('-session_date', '-session_id')[:5]
    
    # Get templates
    templates = workout_sessions.objects.filter(
        user_id=user_id,
        is_template=True
    ).order_by('-session_id')
    
    suggestions = get_exercise_suggestions(user_id)
    
    return render(request, 'log_workout.html', {
        'exercises': exercises_list,
        'recent_sessions': recent_sessions,
        'templates': templates,
        'suggestions': suggestions,
        'today': date.today()
    })

@login_required
def create_workout_session(request):
    """Create new workout session"""
    if request.method == 'POST':
        user_record = get_or_create_user_record(request.user)
        
        new_session = workout_sessions(
            user_id=user_record,
            session_name=request.POST.get('session_name'),
            session_date=request.POST.get('session_date', date.today()),
            start_time=request.POST.get('start_time') or None,
            bodyweight=request.POST.get('bodyweight') or None,
            is_template=False
        )
        new_session.save()
        
        return redirect('add_exercises_to_session', session_id=new_session.session_id)
    
    return redirect('log_workout')

@login_required
def use_template(request, template_id):
    """Create workout from template with custom name"""
    template = get_object_or_404(workout_sessions, session_id=template_id, is_template=True)
    user_record = get_or_create_user_record(request.user)
    
    if request.method == 'POST':
        # Get custom name from form
        custom_name = request.POST.get('session_name', template.session_name.replace(' (Template)', ''))
        
        # Create new session from template
        new_session = workout_sessions.objects.create(
            user_id=user_record,
            session_name=custom_name,
            session_date=date.today(),
            is_template=False
        )
        
        # Copy exercises from template
        template_exercises = session_exercises.objects.filter(session_id=template)
        for te in template_exercises:
            session_exercises.objects.create(
                session_id=new_session,
                exercise_id=te.exercise_id,
                exercise_order=te.exercise_order,
                target_sets=te.target_sets,
                target_reps=te.target_reps
            )
        
        return redirect('add_exercises_to_session', session_id=new_session.session_id)
    
    return redirect('log_workout')

@login_required
def save_as_template(request, session_id):
    """Save current workout as template"""
    if request.method == 'POST':
        session = get_object_or_404(workout_sessions, session_id=session_id)
        
        # Create template
        template = workout_sessions.objects.create(
            user_id=session.user_id,
            session_name=f"{session.session_name} (Template)",
            session_date=date.today(),
            is_template=True
        )
        
        # Copy exercises
        for se in session_exercises.objects.filter(session_id=session):
            session_exercises.objects.create(
                session_id=template,
                exercise_id=se.exercise_id,
                exercise_order=se.exercise_order,
                target_sets=se.target_sets,
                target_reps=se.target_reps
            )
        
        return redirect('log_workout')

@login_required
def delete_template(request, template_id):
    """Delete a workout template"""
    if request.method == 'POST':
        template = get_object_or_404(workout_sessions, session_id=template_id, is_template=True)
        template.delete()
    return redirect('log_workout')

@login_required
def delete_workout(request, session_id):
    """Delete a logged workout"""
    if request.method == 'POST':
        session = get_object_or_404(workout_sessions, session_id=session_id, is_template=False)
        session.delete()
    return redirect('log_workout')

@login_required
def rename_workout(request, session_id):
    """Rename a workout session"""
    if request.method == 'POST':
        session = get_object_or_404(workout_sessions, session_id=session_id)
        new_name = request.POST.get('session_name', '').strip()
        
        if new_name:
            session.session_name = new_name
            session.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Name cannot be empty'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def add_exercises_to_session(request, session_id):
    """Add exercises and sets to a workout session"""
    session = workout_sessions.objects.get(session_id=session_id)
    exercises_list = exercise.objects.all()
    
    session_ex = session_exercises.objects.filter(
        session_id=session_id
    ).select_related('exercise_id').order_by('exercise_order')
    
    session_data = []
    for se in session_ex:
        sets_data = sets.objects.filter(
            session_exercise_id=se.session_exercise_id
        ).order_by('set_number')
        session_data.append({
            'session_exercise': se,
            'sets': sets_data
        })
    
    return render(request, 'add_exercises.html', {
        'session': session,
        'exercises': exercises_list,
        'session_data': session_data
    })

@login_required
def add_exercise_to_session(request, session_id):
    """Add a single exercise to session"""
    if request.method == 'POST':
        exercise_id = request.POST.get('exercise_id')
        target_sets = request.POST.get('target_sets', 3)
        target_reps = request.POST.get('target_reps', 10)
        
        max_order = session_exercises.objects.filter(
            session_id=session_id
        ).count()
        
        new_se = session_exercises(
            session_id=workout_sessions.objects.get(session_id=session_id),
            exercise_id=exercise.objects.get(exercise_id=exercise_id),
            exercise_order=max_order + 1,
            target_sets=target_sets,
            target_reps=target_reps
        )
        new_se.save()
        
    return redirect('add_exercises_to_session', session_id=session_id)

@login_required
def log_set(request, session_exercise_id):
    """Log individual sets with smart validation and PR checking"""
    if request.method == 'POST':
        weight_input = request.POST.get('weight', '0')
        weight_input = Decimal(weight_input) if weight_input else Decimal('0')
        reps_input = int(request.POST.get('reps', 0))
        rpe_input = int(request.POST.get('rpe', 5))
        set_number = int(request.POST.get('set_number', 1))
        
        se = session_exercises.objects.get(session_exercise_id=session_exercise_id)
        ex = se.exercise_id
        session = se.session_id
        user_record = session.user_id
        
        # Validate weight
        validation_result = validate_weight_input(
            user_record.user_id, 
            ex.exercise_id, 
            weight_input
        )
        
        # Create set
        new_set = sets(
            session_exercise_id=se,
            set_number=set_number,
            weight=weight_input if weight_input > 0 else None,
            reps=reps_input,
            rpe=rpe_input,
            completion_time=datetime.now()
        )
        new_set.save()
        
        # Check for PR
        is_pr = False
        previous_pr_weight = None
        if weight_input > 0:
            is_pr, previous_pr_weight = check_and_record_pr(
                user_record.user_id,
                ex.exercise_id,
                weight_input,
                reps_input,
                new_set
            )
        
        # Log validation
        data_validation.objects.create(
            user_id=user_record,
            set_id=new_set,
            exercise_id=ex,
            input_weight=weight_input,
            expected_max=validation_result.get('expected_max'),
            flagged_as=validation_result['flag'],
            timestamp=datetime.now()
        )
        
        return render(request, 'set_logged.html', {
            'validation': validation_result,
            'set': new_set,
            'is_pr': is_pr,
            'previous_pr': previous_pr_weight,
            'exercise_name': ex.name,
            'session_exercise_id': session_exercise_id,
            'session_id': session.session_id
        })
    
    return redirect('log_workout')

@login_required
def view_progress(request):
    """Enhanced progress view with charts and trends"""
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id
    
    # Get progress data
    progress_data = progress.objects.filter(
        user_id=user_id
    ).select_related('exercise_id').order_by('-date')[:20]
    
    # Get recent validations
    recent_validations = data_validation.objects.filter(
        user_id=user_id
    ).select_related('exercise_id').order_by('-timestamp')[:10]
    
    # Get exercise trends for TOP 5 charts (by volume)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.exercise_id,
                e.name,
                SUM(s.weight * s.reps) as total_volume
            FROM exercise e
            JOIN session_exercises se ON e.exercise_id = se.exercise_id
            JOIN sets s ON se.session_exercise_id = s.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s 
              AND s.weight IS NOT NULL
              AND ws.is_template = 0
            GROUP BY e.exercise_id, e.name
            ORDER BY total_volume DESC
            LIMIT 5
        """, [user_id])
        
        top_exercises = cursor.fetchall()
    
    # Build chart data for TOP 5 exercises
    exercise_trends = {}
    for ex_id, ex_name, _ in top_exercises:
        weekly_progress = progress.objects.filter(
            user_id=user_id,
            exercise_id=ex_id,
            period_type='weekly'
        ).order_by('date')[:8]
        
        if weekly_progress:
            exercise_trends[ex_name] = {
                'dates': [p.date.strftime('%m/%d') for p in weekly_progress],
                'max_weights': [float(p.max_weight) if p.max_weight else 0 for p in weekly_progress],
                'volumes': [float(p.total_volume) if p.total_volume else 0 for p in weekly_progress]
            }
    
    # Get ALL user exercises for dropdown
    user_exercises = exercise.objects.filter(
        session_exercises__session_id__user_id=user_id,
        session_exercises__session_id__is_template=False
    ).distinct().values_list('exercise_id', 'name').order_by('name')
    
    # Get bodyweight trends (FIXED: reversed for chronological order - oldest to newest)
    bodyweight_logs = user_stats_log.objects.filter(
        user_id=user_id
    ).order_by('date')[:30]  # Changed from '-date' to 'date'
    
    bodyweight_trend = {
        'dates': [log.date.strftime('%m/%d') for log in bodyweight_logs],
        'weights': [float(log.weight) for log in bodyweight_logs]
    }
    
    recommendations = get_workout_recommendations(user_id)

    context = {
        'progress_data': progress_data,
        'validations': recent_validations,
        'exercise_trends': json.dumps(exercise_trends),
        'bodyweight_trend': json.dumps(bodyweight_trend),
        'user_exercises': user_exercises,
        'weight_increase_recs': recommendations['weight_increase'],
        'neglected_muscle_group_recs': recommendations['neglected_muscle_groups'],
    }
    
    return render(request, 'progress.html', context)

@login_required
def get_exercise_data(request, exercise_id):
    """API endpoint for custom exercise chart data"""
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id
    
    # Get data for specific exercise
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ws.session_date,
                MAX(s.weight) as max_weight,
                AVG(s.reps) as avg_reps,
                SUM(s.weight * s.reps) as total_volume
            FROM workout_sessions ws
            JOIN session_exercises se ON ws.session_id = se.session_id
            JOIN sets s ON se.session_exercise_id = s.session_exercise_id
            WHERE ws.user_id = %s 
              AND se.exercise_id = %s
              AND s.weight IS NOT NULL
              AND ws.is_template = 0
            GROUP BY ws.session_date
            ORDER BY ws.session_date ASC
            LIMIT 20
        """, [user_id, exercise_id])
        
        results = cursor.fetchall()
    
    data = {
        'dates': [row[0].strftime('%m/%d') for row in results],
        'max_weights': [float(row[1]) if row[1] else 0 for row in results],
        'avg_reps': [float(row[2]) if row[2] else 0 for row in results],
        'total_volume': [float(row[3]) if row[3] else 0 for row in results]
    }
    
    return JsonResponse(data)

@login_required
def manage_goals(request):
    """Goal management interface"""
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id
    
    if request.method == 'POST':
        goals.objects.create(
            user_id=user_record,
            goal_type=request.POST.get('goal_type'),
            goal_description=request.POST.get('goal_description'),
            target_value=Decimal(request.POST.get('target_value')),
            unit=request.POST.get('unit'),
            exercise_id=exercise.objects.get(exercise_id=request.POST.get('exercise_id')) if request.POST.get('exercise_id') else None,
            start_date=date.today(),
            target_date=request.POST.get('target_date') or None,
            status='active'
        )
        return redirect('manage_goals')
    
    all_goals = goals.objects.filter(
        user_id=user_id
    ).select_related('exercise_id').order_by('-start_date')
    
    exercises_list = exercise.objects.all()
    
    return render(request, 'goals.html', {
        'goals': all_goals,
        'exercises': exercises_list
    })

@login_required
def update_goal_status(request, goal_id):
    """Mark goal as completed or abandoned"""
    if request.method == 'POST':
        goal = get_object_or_404(goals, goal_id=goal_id)
        new_status = request.POST.get('status')
        
        goal.status = new_status
        if new_status == 'completed':
            goal.completion_date = date.today()
        goal.save()
        
    return redirect('manage_goals')

@login_required
def log_body_stats(request):
    """Log bodyweight and body measurements"""
    user_record = get_or_create_user_record(request.user)
    
    if request.method == 'POST':
        user_stats_log.objects.create(
            user_id=user_record,
            date=request.POST.get('date', date.today()),
            weight=Decimal(request.POST.get('weight')),
            neck=Decimal(request.POST.get('neck')) if request.POST.get('neck') else None,
            waist=Decimal(request.POST.get('waist')) if request.POST.get('waist') else None,
            hips=Decimal(request.POST.get('hips')) if request.POST.get('hips') else None,
            body_fat_percentage=Decimal(request.POST.get('body_fat')) if request.POST.get('body_fat') else None,
            notes=request.POST.get('notes', '')
        )
        return redirect('progress')
    
    recent_logs = user_stats_log.objects.filter(
        user_id=user_record.user_id
    ).order_by('-date')[:10]
    
    return render(request, 'log_stats.html', {
        'recent_logs': recent_logs,
        'today': date.today()
    })

def signup(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})




@login_required
def progress_view(request):
    user = request.user

    # whatever you already compute for progress...
    # progress_data = ...

    recommendations = get_workout_recommendations(user)

    context = {
        # "progress_data": progress_data,
        "weight_increase_recs": recommendations["weight_increase"],
        "neglected_muscle_group_recs": recommendations["neglected_muscle_groups"],
    }

    return render(request, "workoutware_app/progress.html", context)
