USE workoutware;

INSERT INTO workout_sessions (session_id, user_id, session_name, session_date, start_time, end_time, duration_minutes, bodyweight, completed, is_template)
	VALUES 
    (1, 5, "Session 1", "2025-12-01", "08:00:00", "09:00:00", 60, 150.0, TRUE, FALSE),
    (2, 5, "Session 2", "2025-12-03", "09:27:00", "10:04:00", 37, 148.0, TRUE, FALSE),
    (3, 5, "Session 3", "2025-12-04", "08:17:00", "09:00:00", 43, 149.0, TRUE, FALSE),
    (4, 5, "Session 4", "2025-12-05", "08:46:00", "09:06:00", 20, 147.0, TRUE, FALSE);
    
INSERT INTO session_exercises (session_exercise_id, session_id, exercise_id, exercise_order, target_sets, target_reps, completed)
	VALUES 
    (1, 1, 1, 1, 3, 20, TRUE),
    (2, 1, 9, 2, 3, 10, TRUE),
    (3, 1, 10, 3, 3, 10, TRUE),
    (4, 1, 11, 4, 3, 20, TRUE),
    (5, 1, 12, 5, 2, 20, TRUE),
    (6, 2, 4, 1, 3, 20, TRUE),
    (7, 2, 5, 2, 3, 10, TRUE),
    (8, 2, 6, 3, 3, 10, TRUE),
    (9, 2, 7, 4, 3, 20, TRUE),
    (10, 2, 8, 5, 2, 20, TRUE),
    (11, 3, 13, 5, 4, 10, TRUE),
    (12, 3, 14, 5, 3, 15, TRUE),
    (13, 3, 15, 5, 3, 15, TRUE),
    (14, 3, 16, 5, 2, 20, TRUE),
    (15, 4, 2, 1, NULL, NULL, TRUE);
	
    
INSERT INTO exercise (exercise_id, name, type, subtype, equipment, difficulty, description, demo_link)
	VALUES
    (1, "Bicep Curl", "Strength", "Pull", "Dumbbells", 2, "Raise the weight from your hip to your face, using your elbow as a hinge", NULL),
    (2, "Jogging", "Cardio", "Endurance", NULL, 3, "Maintain a constant pace", NULL),
    (3, "Plank", "Strength", "Core", NULL, 5, "Keep your hips aligned with your back", NULL),
    (4, "Overhead Tricep Extension", "Strength", "Push", "Dumbbells", 2, "Lower the weight slowly and explode to bring it upwards", NULL),
    (5, "Chest Fly", "Strength", "Push", "Dumbbells", 1, "Keep your hands algined horizontally with the center of your chest and keep your chest pushed outwards", NULL),
    (6, "Bench Press", "Strength", "Push", "Barbell", 5, "Bring the bar down to the center of your chest, then use your breath and your legs to assist in pushing it back overhead.", NULL),
    (7, "Dips", "Strength", "Push", "Dip Machine", 5, "Keep yourself balanced and lower yourself slowly", NULL),
    (8, "Incline Dumbbell Press", "Strength", "Push", "Dumbbells", 3, "Lower the weight slowly and explode to bring it upwards", NULL),
    (9, "Seated Rows", "Strength", "Pull", "Cable", 3, "Keep your back straight and stretch forwards before explosively pulling backwards", NULL),
    (10, "Bent-Over Rows", "Strength", "Pull", "Barbell", 4, "Keep your back straight and stay balanced", NULL),
    (11, "Preacher Curls", "Strength", "Pull", "Dumbbell", 2, "Focus on slow movement when relaxed and explosive movement when pulling", NULL),
    (12, "Lateral Raises", "Strength", "Pull", "Dumbbell", 3, "Use low weight and focus on slow movement", NULL),
    (13, "Barbell Squat", "Strength", "Legs", "Barbell", 4, "Keep your back straight and focus on flexing your quads when lifting", NULL),
    (14, "Leg Curls", "Strength", "Legs", "Cable", 2, "Try not to use your back or use any momentum to get the weight moving; only your legs should do the work", NULL),
    (15, "Leg Extensions", "Strength", "Legs", "Cable", 2, "Use your hands to get a good grip on the machine, as balance assists in the movement", NULL),
    (16, "Leg Press", "Strength", "Legs", "Machine", 4, "Use a wide stance on the machine to prevent injury", NULL);