USE workoutware;

-- 
-- USER TEST DATA
--

INSERT INTO user_info (
    username, first_name, last_name, address, town, state, country,
    email, phone_number, password_hash, date_of_birth, height,
    date_registered, date_unregistered, registered, fitness_goal, user_type
) VALUES
('jdoe', 'John', 'Doe', '123 Elm St', 'Boston', 'MA', 'USA', 'john.doe@example.com', '555-111-2222',
 SHA2('password123',256), '1990-05-10', 180.34, '2025-01-10', NULL, 1, 'Weight Loss', 'client'),

('esmith', 'Emily', 'Smith', '77 Pine Ave', 'Chicago', 'IL', 'USA', 'emily.smith@example.com', '555-333-4444',
 SHA2('trainhard',256), '1995-08-22', 165.10, '2025-01-11', NULL, 1, 'Muscle Gain', 'client'),

('mjohnson', 'Michael', 'Johnson', '45 River Rd', 'Austin', 'TX', 'USA', 'mike.j@example.com', '555-222-5555',
 SHA2('fitlife',256), '1988-12-01', 178.00, '2025-01-11', NULL, 1, 'Endurance', 'client'),

('sbrown', 'Sophia', 'Brown', NULL, 'Seattle', 'WA', 'USA', 'sophia.b@example.com', '555-999-0000',
 SHA2('health123',256), '1997-03-14', 170.20, '2025-01-12', NULL, 1, 'Flexibility', 'client'),

('cwilson', 'Chris', 'Wilson', '150 Main St', 'Denver', 'CO', 'USA', 'chris.w@example.com', '555-444-7777',
 SHA2('adminpass',256), '1985-11-02', 175.50, '2025-01-09', NULL, 1, 'Overall Fitness', 'admin'),

('ajones', 'Ava', 'Jones', NULL, 'Phoenix', 'AZ', 'USA', 'ava.jones@example.com', '555-666-1111',
 SHA2('fitness',256), '1993-04-18', NULL, '2025-01-13', NULL, 1, 'Toning', 'client'),

('wmartin', 'William', 'Martin', '88 Hill St', 'Miami', 'FL', 'USA', 'will.martin@example.com', NULL,
 SHA2('stronger',256), '1991-07-09', 182.30, '2025-01-13', NULL, 1, 'Strength', 'client'),

('llee', 'Lily', 'Lee', '20 Ocean Dr', 'San Diego', 'CA', 'USA', 'lily.lee@example.com', '555-101-3030',
 SHA2('cardiofit',256), '1998-06-21', 160.75, '2025-01-14', NULL, 1, 'Cardio', 'client'),

('dclark', 'Daniel', 'Clark', '45 Palm Way', 'Tampa', 'FL', 'USA', 'dan.clark@example.com', NULL,
 SHA2('password!',256), '1994-01-25', 185.60, '2025-01-14', NULL, 1, 'Endurance', 'client'),

('nharris', 'Noah', 'Harris', '12 Brook Ln', 'Atlanta', 'GA', 'USA', 'noah.h@example.com', '555-654-9087',
 SHA2('betterme',256), '1999-11-01', NULL, '2025-01-15', NULL, 1, 'Weight Loss', 'client'),

('ogreen', 'Olivia', 'Green', '77 Maple St', 'Dallas', 'TX', 'USA', 'olivia.g@example.com', '555-121-3141',
 SHA2('wellness',256), '1996-03-08', 168.55, '2025-01-15', NULL, 1, 'Flexibility', 'client'),

('pphillips', 'Paul', 'Phillips', NULL, 'Detroit', 'MI', 'USA', 'paul.p@example.com', '555-321-7654',
 SHA2('gainmuscle',256), '1989-05-30', 179.20, '2025-01-15', NULL, 1, 'Muscle Gain', 'client'),

('zreid', 'Zoe', 'Reid', '9 Cedar St', 'Portland', 'OR', 'USA', 'zoe.reid@example.com', NULL,
 SHA2('runfast',256), '2000-09-10', 158.90, '2025-01-16', NULL, 1, 'Running', 'client'),

('gturner', 'George', 'Turner', '66 Vine St', 'Cleveland', 'OH', 'USA', 'george.t@example.com', '555-852-8528',
 SHA2('recovery',256), '1987-12-11', 174.10, '2025-01-16', NULL, 1, 'Rehabilitation', 'client'),

('bwalker', 'Bella', 'Walker', NULL, 'Boston', 'MA', 'USA', 'bella.w@example.com', '555-159-7533',
 SHA2('yogamind',256), '1999-10-20', 165.00, '2025-01-16', NULL, 1, 'Flexibility', 'client'),

('tking', 'Thomas', 'King', '32 Cliff Dr', 'New York', 'NY', 'USA', 'thomas.king@example.com', '555-888-1212',
 SHA2('adminsecure',256), '1982-02-18', 180.50, '2025-01-08', NULL, 1, 'Administration', 'admin'),

('nhernandez', 'Natalie', 'Hernandez', '54 River Dr', 'Houston', 'TX', 'USA', 'natalie.h@example.com', NULL,
 SHA2('burnfat',256), '1996-12-02', 170.30, '2025-01-17', NULL, 1, 'Weight Loss', 'client'),

('cscott', 'Caleb', 'Scott', NULL, 'Charlotte', 'NC', 'USA', 'caleb.scott@example.com', '555-212-3434',
 SHA2('getfit',256), '1997-04-27', NULL, '2025-01-17', NULL, 1, 'General Fitness', 'client'),

('lyoung', 'Layla', 'Young', '99 Spring St', 'Philadelphia', 'PA', 'USA', 'layla.y@example.com', NULL,
 SHA2('healthfirst',256), '1998-03-17', 161.20, '2025-01-17', NULL, 1, 'Cardio', 'client'),

('jroberts', 'James', 'Roberts', NULL, 'San Jose', 'CA', 'USA', 'james.r@example.com', NULL,
 SHA2('gostrength',256), '1990-10-30', 188.40, '2025-01-18', NULL, 1, 'Strength', 'client'),

('rhall', 'Ruby', 'Hall', '14 Lake Dr', 'Orlando', 'FL', 'USA', 'ruby.h@example.com', '555-888-2323',
 SHA2('zenfocus',256), '1995-06-02', 169.00, '2025-01-18', NULL, 1, 'Mental Wellness', 'client'),

('hlopez', 'Henry', 'Lopez', '75 North St', 'Cincinnati', 'OH', 'USA', 'henry.l@example.com', NULL,
 SHA2('runbetter',256), '1988-08-12', 183.33, '2025-01-18', NULL, 1, 'Running', 'client'),

('wwhite', 'Willa', 'White', NULL, 'Nashville', 'TN', 'USA', 'willa.w@example.com', '555-444-6666',
 SHA2('pilatescore',256), '1997-01-13', 159.50, '2025-01-18', NULL, 1, 'Core Strength', 'client'),

('gking', 'Gabriel', 'King', '85 Ivy Rd', 'Minneapolis', 'MN', 'USA', 'gabe.king@example.com', '555-300-1200',
 SHA2('powerup',256), '1994-05-11', 180.10, '2025-01-19', NULL, 1, 'Powerlifting', 'client'),

('isanders', 'Isla', 'Sanders', NULL, 'Salt Lake City', 'UT', 'USA', 'isla.s@example.com', '555-700-9999',
 SHA2('stretchgood',256), '1998-11-17', NULL, '2025-01-19', NULL, 1, 'Mobility', 'client'),

('nward', 'Nathan', 'Ward', '12 Elm Dr', 'Denver', 'CO', 'USA', 'nate.w@example.com', NULL,
 SHA2('toneup',256), '1991-03-20', 177.90, '2025-01-19', NULL, 1, 'Toning', 'client'),

('jsanchez', 'Julia', 'Sanchez', '52 Grove St', 'Sacramento', 'CA', 'USA', 'julia.s@example.com', '555-456-7890',
 SHA2('cardiogo',256), '1997-09-29', 170.00, '2025-01-19', NULL, 1, 'Cardio', 'client'),

('rjenkins', 'Ryan', 'Jenkins', '100 Beach Blvd', 'San Diego', 'CA', 'USA', 'ryan.j@example.com', NULL,
 SHA2('buildmuscle',256), '1989-07-07', 185.10, '2025-01-20', NULL, 1, 'Muscle Gain', 'client'),

('cporter', 'Chloe', 'Porter', NULL, 'Baltimore', 'MD', 'USA', 'chloe.p@example.com', NULL,
 SHA2('stretchit',256), '2001-12-28', 162.00, '2025-01-20', NULL, 1, 'Flexibility', 'client'),

('agarcia', 'Aiden', 'Garcia', '39 Pine Cir', 'Las Vegas', 'NV', 'USA', 'aiden.g@example.com', '555-110-2200',
 SHA2('admin1234',256), '1983-01-01', 181.75, '2025-01-05', NULL, 1, 'System Management', 'admin'),

('mmorris', 'Mia', 'Morris', '150 Forest Rd', 'Buffalo', 'NY', 'USA', 'mia.m@example.com', '555-808-7070',
 SHA2('burncalories',256), '1996-04-14', 164.40, '2025-01-20', NULL, 1, 'Weight Loss', 'client'),

('mgray', 'Miles', 'Gray', '62 Sunset Dr', 'Columbus', 'OH', 'USA', 'miles.g@example.com', NULL,
 SHA2('corestable',256), '1993-10-22', NULL, '2025-01-21', NULL, 1, 'Core Strength', 'client'),

('swood', 'Scarlett', 'Wood', NULL, 'Raleigh', 'NC', 'USA', 'scarlett.w@example.com', '555-140-5600',
 SHA2('feelstrong',256), '1995-06-30', NULL, '2025-01-21', NULL, 1, 'Strength', 'client'),

('hprice', 'Hudson', 'Price', '91 Willow St', 'Richmond', 'VA', 'USA', 'hudson.p@example.com', NULL,
 SHA2('betterform',256), '1992-08-23', 180.90, '2025-01-21', NULL, 1, 'General Fitness', 'client'),

('pelias', 'Penelope', 'Elias', '10 Birch Ln', 'Boise', 'ID', 'USA', 'pen.elias@example.com', '555-100-2020',
 SHA2('flowyoga',256), '1999-05-19', 159.00, '2025-01-21', NULL, 1, 'Yoga', 'client'),

('rmitchell', 'Ryder', 'Mitchell', NULL, 'Louisville', 'KY', 'USA', 'ryder.m@example.com', '555-222-1133',
 SHA2('powertrain',256), '1991-03-09', 188.80, '2025-01-22', NULL, 1, 'Strength', 'client'),

('acarson', 'Aria', 'Carson', '28 Garden Rd', 'Fresno', 'CA', 'USA', 'aria.c@example.com', NULL,
 SHA2('learnstretch',256), '2000-08-11', NULL, '2025-01-22', NULL, 1, 'Mobility', 'client'),

('jjordan', 'Jack', 'Jordan', NULL, 'Tulsa', 'OK', 'USA', 'jack.jordan@example.com', '555-778-9900',
 SHA2('swimfast',256), '1994-02-24', 179.70, '2025-01-22', NULL, 1, 'Swimming', 'client'),

('hroberts', 'Hailey', 'Roberts', '57 Cherry Rd', 'Cincinnati', 'OH', 'USA', 'hailey.r@example.com', NULL,
 SHA2('feelgood',256), '1996-09-07', NULL, '2025-01-22', NULL, 1, 'Health', 'client'),

('jmartinez', 'Julian', 'Martinez', '40 Valley Rd', 'Austin', 'TX', 'USA', 'julian.m@example.com', '555-600-3300',
 SHA2('bulkup',256), '1992-05-14', 182.40, '2025-01-23', NULL, 1, 'Bodybuilding', 'client'),

('grogers', 'Grace', 'Rogers', NULL, 'Milwaukee', 'WI', 'USA', 'grace.r@example.com', NULL,
 SHA2('yogacalm',256), '1997-03-03', 164.20, '2025-01-23', NULL, 1, 'Flexibility', 'client'),

('klopez', 'Kai', 'Lopez', '87 Bay St', 'Seattle', 'WA', 'USA', 'kai.lopez@example.com', '555-303-4040',
 SHA2('balance',256), '1998-11-21', NULL, '2025-01-23', NULL, 1, 'Balance Training', 'client'),

('carmstrong', 'Carter', 'Armstrong', '19 Park Pl', 'Chicago', 'IL', 'USA', 'carter.a@example.com', NULL,
 SHA2('cardiohealth',256), '1995-08-05', 178.10, '2025-01-23', NULL, 1, 'Cardio Health', 'client'),

('delson', 'Delilah', 'Elson', '31 Pine Rd', 'Boston', 'MA', 'USA', 'delilah.e@example.com', '555-929-1111',
 SHA2('pilateslife',256), '2001-12-31', 160.00, '2025-01-24', NULL, 1, 'Pilates', 'client'),

('phunt', 'Parker', 'Hunt', NULL, 'Houston', 'TX', 'USA', 'parker.h@example.com', '555-777-0007',
 SHA2('crossfitnow',256), '1989-09-19', 185.20, '2025-01-24', NULL, 1, 'CrossFit', 'client'),

('ssharp', 'Stella', 'Sharp', NULL, 'Phoenix', 'AZ', 'USA', 'stella.s@example.com', '555-314-3142',
 SHA2('stepcount',256), '1999-06-23', NULL, '2025-01-24', NULL, 1, 'Steps Tracking', 'client'),

('evasquez', 'Evan', 'Vasquez', '61 Oak Ln', 'New York', 'NY', 'USA', 'evan.v@example.com', NULL,
 SHA2('admin99',256), '1984-11-08', 183.10, '2025-01-06', NULL, 1, 'System Administration', 'admin');
 
 --
 -- EXERCISE TEST DATA
 --
 
 INSERT INTO exercise (
    name, type, subtype, equipment, difficulty, description, demo_link
) VALUES
('Push-Up', 'Strength', 'Upper Body', 'None', 2, 'Bodyweight chest and tricep push movement.', 'https://youtu.be/_l3ySVKYVJ8'),
('Squat', 'Strength', 'Lower Body', 'None', 2, 'Knee-dominant lower body movement targeting quads.', 'https://youtu.be/aclHkVaku9U'),
('Deadlift', 'Strength', 'Full Body', 'Barbell', 4, 'Hip hinge movement building posterior strength.', 'https://youtu.be/op9kVnSso6Q'),
('Lunges', 'Strength', 'Lower Body', 'None', 2, 'Single-leg exercise improving balance and leg strength.', 'https://youtu.be/QOVaHwm-Q6U'),
('Bench Press', 'Strength', 'Upper Body', 'Barbell', 4, 'Pressing exercise focusing on chest and triceps.', 'https://youtu.be/rT7DgCr-3pg'),
('Pull-Up', 'Strength', 'Back', 'Pull-Up Bar', 4, 'Vertical pulling for upper back and lats.', NULL),
('Bicep Curl', 'Strength', 'Arms', 'Dumbbells', 1, 'Isolation movement for biceps.', 'https://youtu.be/in7PaeYlhrM'),
('Shoulder Press', 'Strength', 'Upper Body', 'Dumbbells', 3, 'Overhead pressing targeting deltoids.', NULL),
('Tricep Dips', 'Strength', 'Arms', 'Dip Bar', 3, 'Bodyweight dip for triceps.', 'https://youtu.be/2z8JmcrW-As'),
('Plank', 'Core', 'Isometric', 'None', 1, 'Core stability exercise.', 'https://youtu.be/pSHjTRCQxIw'),
('Mountain Climbers', 'Cardio', 'HIIT', 'None', 2, 'High-intensity core/cardio.', 'https://youtu.be/3Z0_GdRL7Z4'),
('Burpees', 'Cardio', 'HIIT', 'None', 4, 'Full body explosive cardio movement.', 'https://youtu.be/dZgVxmf6jkA'),
('Jump Rope', 'Cardio', 'Endurance', 'Jump Rope', 2, 'Cardio exercise improving coordination.', NULL),
('Running', 'Cardio', 'Endurance', 'None', NULL, 'Outdoor or treadmill running for endurance.', NULL),
('Cycling', 'Cardio', 'Endurance', 'Bike', 2, 'Low impact cardio with moderate intensity.', NULL),
('Rowing Machine', 'Cardio', 'Full Body', 'Rowing Machine', 3, 'Cardio rowing with strength stimulus.', 'https://youtu.be/8Q-3VW1jgIg'),
('Stair Climber', 'Cardio', 'Lower Body', 'Stair Machine', 3, 'Climbing simulation for legs and heart health.', NULL),
('Elliptical Trainer', 'Cardio', 'Low Impact', 'Elliptical', NULL, 'Smooth cardio exercise reducing joint strain.', NULL),
('Box Jumps', 'Cardio', 'Plyometrics', 'Box', 4, 'Explosive lower body exercise enhancing power.', 'https://youtu.be/52r_Ul5k03g'),
('Jumping Jacks', 'Cardio', 'Warm-Up', 'None', 1, 'Simple aerobic warm-up movement.', NULL),
('Lat Pulldown', 'Strength', 'Back', 'Machine', 2, 'Targets lats and upper back.', 'https://youtu.be/1P4ZFqI9pJ8'),
('Leg Press', 'Strength', 'Lower Body', 'Machine', 3, 'Strengthens legs using a pressing machine.', NULL),
('Calf Raise', 'Strength', 'Lower Body', 'None', 1, 'Strengthens calves with ankle movement.', NULL),
('Hip Thrust', 'Strength', 'Glutes', 'Barbell', 3, 'Glute-focused hip hinge movement.', 'https://youtu.be/LM8XHLYJoYs'),
('Chest Fly', 'Strength', 'Upper Body', 'Dumbbells', 2, 'Isolation exercise for chest.', NULL),
('Bent-Over Row', 'Strength', 'Back', 'Barbell', 4, 'Pulling exercise strengthening posterior chain.', 'https://youtu.be/kBWAon7ItDw'),
('Russian Twists', 'Core', 'Rotational', 'None', 2, 'Core rotation exercise improving obliques.', 'https://youtu.be/wkD8rjkodUI'),
('Crunches', 'Core', 'Abs', 'None', 1, 'Ab isolation exercise.', NULL),
('Leg Raises', 'Core', 'Abs', 'None', 2, 'Lower ab focused bodyweight movement.', NULL),
('Superman Hold', 'Core', 'Back Stability', 'None', 1, 'Strengthens lower back extensor muscles.', NULL),
('Yoga Sun Salutation', 'Yoga', 'Flow', 'Mat', NULL, 'Flow sequence improving flexibility and calmness.', 'https://youtu.be/6IUyY9Dyr5w'),
('Warrior Pose II', 'Yoga', 'Strength', 'Mat', 1, 'Stability and lower body strength posture.', NULL),
('Downward Dog', 'Yoga', 'Flexibility', 'Mat', 1, 'Stretching of posterior chain.', 'https://youtu.be/0FxBh2fRbdU'),
('Child''s Pose', 'Yoga', 'Recovery', 'Mat', NULL, 'Relaxing stretch for the back and hips.', NULL),
('Tree Pose', 'Yoga', 'Balance', 'Mat', 1, 'Balance-focused single-leg posture.', NULL),
('Bridge Pose', 'Yoga', 'Strength', 'Mat', 1, 'Glute activation and spinal extension posture.', NULL),
('Seated Forward Fold', 'Yoga', 'Flexibility', 'Mat', NULL, 'Hamstring stretch improving mobility.', NULL),
('Cat-Cow', 'Yoga', 'Mobility', 'Mat', 1, 'Spinal mobility flow.', 'https://youtu.be/kqnua4rHVVA'),
('Pigeon Pose', 'Yoga', 'Flexibility', 'Mat', 1, 'Hip opener increasing mobility.', NULL),
('Cobra Pose', 'Yoga', 'Mobility', 'Mat', 1, 'Spinal extension pose.', NULL),
('Pilates Hundred', 'Pilates', 'Core', 'Mat', 2, 'Pilates core breathing exercise.', NULL),
('Side Leg Lift', 'Pilates', 'Lower Body', 'Mat', 1, 'Strengthens outer glutes.', NULL),
('Bird Dog', 'Mobility', 'Core Stability', 'Mat', 1, 'Spinal alignment and core activation.', 'https://youtu.be/v7AYKMP6rOE'),
('Wall Sit', 'Strength', 'Isometric', 'None', 2, 'Lower-body static endurance exercise.', NULL),
('Farmer\'s Carry', 'Strength', 'Grip', 'Dumbbells', 3, 'Loaded carry improving grip and stability.', NULL),
('Kettlebell Swing', 'Strength', 'Hip Hinge', 'Kettlebell', 3, 'Explosive hip drive movement.', 'https://youtu.be/6u6C_9Vml_A'),
('Medicine Ball Slam', 'Strength', 'Power', 'Medicine Ball', 3, 'Explosive upper-body power exercise.', NULL),
('Glute Kickback', 'Strength', 'Glutes', 'Cable Machine', 2, 'Glute isolation movement.', NULL),
('Side Plank', 'Core', 'Isometric', 'None', 2, 'Oblique stability exercise.', 'https://youtu.be/KAy4z6ehgNw'),
('Hamstring Curl Machine', 'Strength', 'Lower Body', 'Machine', 2, 'Hamstring isolation exercise.', NULL);

-- 
-- TARGET TEST DATA
--

INSERT INTO target (
    target_name, target_group, target_function
) VALUES
('Chest', 'Upper Body', 'Push movement and shoulder horizontal adduction'),
('Back', 'Upper Body', 'Pulling movements and posture support'),
('Shoulders', 'Upper Body', 'Overhead pressing and shoulder stabilization'),
('Biceps', 'Arms', 'Elbow flexion'),
('Triceps', 'Arms', 'Elbow extension'),
('Forearms', 'Arms', 'Grip strength and wrist movement'),
('Quadriceps', 'Lower Body', 'Knee extension'),
('Hamstrings', 'Lower Body', 'Knee flexion and hip extension'),
('Glutes', 'Lower Body', 'Hip extension and pelvic stability'),
('Calves', 'Lower Body', 'Ankle plantar flexion'),
('Lower Back', 'Core', 'Spine extension and stabilization'),
('Abdominals', 'Core', 'Spine flexion and trunk stability'),
('Obliques', 'Core', 'Trunk rotation and lateral flexion'),
('Hips', 'Lower Body', 'Hip stability and mobility'),
('Spinal Erectors', 'Core', 'Postural control and lumbar extension'),
('Rotator Cuff', 'Upper Body', 'Shoulder joint stabilization'),
('Traps', 'Upper Body', 'Scapular elevation and upper back support'),
('Lats', 'Upper Body', 'Shoulder extension and back strength'),
('Pectorals', 'Upper Body', 'Upper body pushing'),
('Neck', 'Upper Body', NULL),
('Cardiovascular System', 'Full Body', 'Aerobic and endurance conditioning'),
('Full Body', 'Full Body', 'Multi-joint compound movement'),
('Hip Flexors', 'Lower Body', 'Hip flexion'),
('Adductors', 'Lower Body', 'Leg adduction'),
('Abductors', 'Lower Body', 'Hip abduction'),
('Core Stability', 'Core', 'Stabilization of the spine during movement'),
('Balance/Proprioception', 'Mobility', 'Body control and balance'),
('Flexibility', 'Mobility', 'Muscle and joint range of motion'),
('Shoulder Girdle', 'Upper Body', NULL),
('Glute Medius', 'Lower Body', 'Hip abduction and stability');

INSERT INTO workout_sessions (
    user_id, session_name, session_date, start_time, end_time,
    duration_minutes, bodyweight, completed, is_template
) VALUES
(5, 'Intro Full-Body Workout', '2025-01-01', '08:00:00', '09:00:00', 60, 85.0, 1, 0),
(5, 'Upper Body Strength', '2025-01-03', '08:15:00', '09:05:00', 50, 84.8, 1, 0),
(5, 'Cardio Day - Treadmill', '2025-01-05', '07:50:00', '08:35:00', 45, 84.6, 1, 0),
(5, 'Lower Body Focus', '2025-01-07', '18:10:00', '19:00:00', 50, 84.4, 1, 0),
(5, 'HIIT Circuit', '2025-01-09', '17:40:00', '18:20:00', 40, 84.3, 1, 0),
(5, 'Push Day', '2025-01-11', '08:05:00', '09:00:00', 55, 84.1, 1, 0),
(5, 'Pull Day', '2025-01-13', '07:55:00', '08:50:00', 55, 84.0, 1, 0),
(5, 'Leg Strength', '2025-01-15', '18:10:00', '19:00:00', 50, 83.8, 1, 0),
(5, 'Steady-State Cardio', '2025-01-17', '07:45:00', '08:30:00', 45, 83.7, 1, 0),
(5, 'Mobility + Core', '2025-01-19', NULL, NULL, 30, 83.6, 1, 0),
(5, 'Full Body Power', '2025-01-21', '18:20:00', '19:10:00', 50, 83.5, 1, 0),
(5, 'Rowing Day', '2025-01-23', '08:10:00', '09:00:00', 50, 83.4, 1, 0),
(5, 'Upper Body Strength', '2025-01-25', '07:55:00', '08:50:00', 55, 83.3, 1, 0),
(5, 'HIIT + Core', '2025-01-27', '18:00:00', '18:40:00', 40, 83.2, 1, 0),
(5, 'Light Cardio Recovery', '2025-01-29', NULL, NULL, 35, 83.1, 0, 0),
(5, 'Evening Bike Ride',        '2025-02-02', '18:30:00', NULL,       NULL,    83.0, 0, 0),
(5, 'Quick Stretch Session',    '2025-02-05', '07:10:00', '07:20:00', 10,      NULL, 0, 0),
(5, 'Back and Biceps',          '2025-02-07', NULL,       NULL,       NULL,    82.9, 0, 0),
(5, 'Cardio Attempt',           '2025-02-09', '08:00:00', '08:10:00', 10,      82.9, 0, 0),
(5, 'Leg Day (Cut Short)',      '2025-02-11', '18:00:00', '18:25:00', 25,      82.8, 0, 0),
(5, 'Mobility Recovery',        '2025-02-13', NULL,       NULL,       20,      82.8, 0, 0),
(5, 'Rowing Warm-up Only',      '2025-02-15', '08:15:00', '08:27:00', 12,      82.7, 0, 0),
(5, 'Arms and Abs',             '2025-02-17', '19:30:00', NULL,       NULL,    82.7, 0, 0),
(5, 'HIIT Plan Unfinished',     '2025-02-19', '07:50:00', '08:05:00', 15,      NULL, 0, 0),
(5, 'Light Walk',               '2025-02-21', NULL,       NULL,       30,      82.6, 0, 0);

INSERT INTO session_exercises (session_id, exercise_id, exercise_order, target_sets, target_reps, completed) VALUES
-- Session 11
(11, 12, 1, 3, 10, 1),
(11, 18, 2, 4, 12, 1),
(11, 25, 3, 3, 8, 1),

-- Session 12
(12, 16, 1, 3, 12, 1),
(12, 21, 2, 4, 10, 1),
(12, 33, 3, 4, 15, 1),
(12, 40, 4, 3, 8, 1),

-- Session 13
(13, 14, 1, 4, 10, 1),
(13, 27, 2, 3, 12, 1),
(13, 36, 3, 4, 10, 1),

-- Session 14
(14, 19, 1, 3, 15, 1),
(14, 29, 2, 4, 10, 1),
(14, 42, 3, 4, 12, 1),
(14, 49, 4, 3, 8, 1),

-- Session 15
(15, 20, 1, 3, 12, 1),
(15, 26, 2, 4, 15, 1),
(15, 38, 3, 3, 10, 1),

-- Session 16
(16, 23, 1, 3, 10, 1),
(16, 32, 2, 4, 12, 1),
(16, 45, 3, 3, 10, 1),
(16, 57, 4, 4, 8, 1),

-- Session 17
(17, 24, 1, 4, 10, 1),
(17, 31, 2, 3, 15, 1),
(17, 41, 3, 4, 12, 1),

-- Session 18
(18, 22, 1, 4, 12, 1),
(18, 30, 2, 3, 10, 1),
(18, 48, 3, 4, 15, 1),
(18, 61, 4, 3, 8, 1),

-- Session 19
(19, 28, 1, 3, 12, 1),
(19, 33, 2, 3, 10, 1),
(19, 50, 3, 4, 10, 1),

-- Session 20
(20, 34, 1, 4, 8, 1),
(20, 43, 2, 4, 12, 1),
(20, 56, 3, 3, 10, 1),

-- Session 21
(21, 35, 1, 3, 15, 1),
(21, 44, 2, 4, 10, 1),
(21, 52, 3, 3, 12, 1),
(21, 59, 4, 4, 10, 1),

-- Session 22
(22, 37, 1, 3, 12, 1),
(22, 46, 2, 3, 10, 1),
(22, 51, 3, 4, 15, 1),

-- Session 23
(23, 39, 1, 3, 10, 1),
(23, 47, 2, 4, 12, 1),
(23, 55, 3, 3, 8, 1),
(23, 60, 4, 4, 10, 1),

-- Session 24
(24, 41, 1, 4, 10, 1),
(24, 54, 2, 3, 12, 1),
(24, 58, 3, 4, 8, 1),

-- Session 25
(25, 42, 1, 3, 10, 1),
(25, 49, 2, 4, 12, 1),
(25, 53, 3, 4, 15, 1),
(25, 61, 4, 3, 8, 1),

-- Session 26
(26, 45, 1, 4, 12, 1),
(26, 51, 2, 3, 10, 1),
(26, 57, 3, 4, 15, 1),

-- Session 27
(27, 46, 1, 3, 10, 1),
(27, 52, 2, 3, 12, 1),
(27, 60, 3, 4, 8, 1),

-- Session 28
(28, 47, 1, 4, 10, 1),
(28, 55, 2, 4, 12, 1),
(28, 58, 3, 3, 10, 1),

-- Session 29
(29, 48, 1, 3, 12, 1),
(29, 53, 2, 3, 8, 1),
(29, 59, 3, 4, 10, 1),
(29, 61, 4, 3, 10, 1),

-- Session 30
(30, 50, 1, 3, 10, 1),
(30, 54, 2, 4, 12, 1),
(30, 56, 3, 4, 10, 1),

-- Session 31
(31, 37, 1, 3, 12, 1),
(31, 44, 2, 4, 10, 1),
(31, 57, 3, 3, 8, 1),

-- Session 32
(32, 38, 1, 3, 10, 1),
(32, 46, 2, 3, 12, 1),
(32, 51, 3, 4, 10, 1),
(32, 60, 4, 4, 12, 1),

-- Session 33
(33, 39, 1, 4, 10, 1),
(33, 48, 2, 3, 8, 1),
(33, 55, 3, 3, 12, 1),

-- Session 34
(34, 40, 1, 3, 12, 1),
(34, 49, 2, 4, 15, 1),
(34, 58, 3, 4, 10, 1),
(34, 61, 4, 4, 12, 1),

-- Session 35
(35, 41, 1, 3, 10, 1),
(35, 52, 2, 4, 12, 1),
(35, 59, 3, 3, 10, 1);

INSERT INTO sets (session_exercise_id, set_number, weight, reps, rpe, completed, is_warmup, completion_time) VALUES
-- Session 32 (session_exercise_id: 64–67)
(64, 1, 95.00, 10, 7, 1, 1, '2025-01-26 10:05:00'),
(64, 2, 115.00, 8, 8, 1, 0, '2025-01-26 10:09:00'),
(64, 3, 115.00, 8, 8, 1, 0, '2025-01-26 10:13:00'),

(65, 1, 0.00, 12, 6, 1, 1, '2025-01-26 10:17:00'),
(65, 2, 20.00, 12, 7, 1, 0, '2025-01-26 10:21:00'),
(65, 3, 20.00, 12, 7, 1, 0, '2025-01-26 10:25:00'),

(66, 1, 135.00, 10, 7, 1, 1, '2025-01-26 10:29:00'),
(66, 2, 185.00, 8, 8, 1, 0, '2025-01-26 10:33:00'),
(66, 3, 185.00, 8, 8, 1, 0, '2025-01-26 10:37:00'),

(67, 1, 50.00, 12, 6, 1, 1, '2025-01-26 10:41:00'),
(67, 2, 70.00, 10, 7, 1, 0, '2025-01-26 10:45:00'),
(67, 3, 70.00, 10, 7, 1, 0, '2025-01-26 10:49:00'),

-- Session 33 (session_exercise_id: 68–70)
(68, 1, 45.00, 10, 7, 1, 1, '2025-01-28 09:05:00'),
(68, 2, 65.00, 8, 8, 1, 0, '2025-01-28 09:09:00'),
(68, 3, 65.00, 8, 8, 1, 0, '2025-01-28 09:13:00'),

(69, 1, 110.00, 12, 7, 1, 1, '2025-01-28 09:17:00'),
(69, 2, 155.00, 10, 8, 1, 0, '2025-01-28 09:21:00'),
(69, 3, 155.00, 10, 8, 1, 0, '2025-01-28 09:25:00'),

(70, 1, 25.00, 12, 6, 1, 1, '2025-01-28 09:29:00'),
(70, 2, 45.00, 10, 7, 1, 0, '2025-01-28 09:33:00'),
(70, 3, 45.00, 10, 7, 1, 0, '2025-01-28 09:37:00'),

-- Session 34 (session_exercise_id: 71–74)
(71, 1, 95.00, 10, 7, 1, 1, '2025-01-30 18:05:00'),
(71, 2, 135.00, 8, 8, 1, 0, '2025-01-30 18:09:00'),
(71, 3, 135.00, 8, 8, 1, 0, '2025-01-30 18:13:00'),

(72, 1, 0.00, 15, 6, 1, 1, '2025-01-30 18:17:00'),
(72, 2, 25.00, 12, 7, 1, 0, '2025-01-30 18:21:00'),
(72, 3, 25.00, 12, 7, 1, 0, '2025-01-30 18:25:00'),

(73, 1, 135.00, 10, 7, 1, 1, '2025-01-30 18:29:00'),
(73, 2, 185.00, 8, 8, 1, 0, '2025-01-30 18:33:00'),
(73, 3, 185.00, 8, 8, 1, 0, '2025-01-30 18:37:00'),

(74, 1, 50.00, 12, 7, 1, 1, '2025-01-30 18:41:00'),
(74, 2, 70.00, 10, 8, 1, 0, '2025-01-30 18:45:00'),
(74, 3, 70.00, 10, 8, 1, 0, '2025-01-30 18:49:00'),

-- Session 35 (session_exercise_id: 75–77)
(75, 1, 65.00, 12, 7, 1, 1, '2025-02-01 17:05:00'),
(75, 2, 95.00, 10, 8, 1, 0, '2025-02-01 17:09:00'),
(75, 3, 95.00, 10, 8, 1, 0, '2025-02-01 17:13:00'),

(76, 1, 0.00, 15, 6, 1, 1, '2025-02-01 17:17:00'),
(76, 2, 20.00, 12, 7, 1, 0, '2025-02-01 17:21:00'),
(76, 3, 20.00, 12, 7, 1, 0, '2025-02-01 17:25:00'),

(77, 1, 135.00, 10, 7, 1, 1, '2025-02-01 17:29:00'),
(77, 2, 155.00, 8, 8, 1, 0, '2025-02-01 17:33:00'),
(77, 3, 155.00, 8, 8, 1, 0, '2025-02-01 17:37:00');

INSERT INTO user_pb (
    user_id, exercise_id, pr_type, pb_weight, pb_reps, pb_time, pb_date, previous_pr, notes
) VALUES
-- Bench Press PR
(5, 15, 'Weight x Reps', 185.00, 5, NULL, '2025-02-01', NULL, 'Solid lockout, slight pause on chest'),

-- Squat PR
(5, 18, 'Weight x Reps', 225.00, 5, NULL, '2025-01-28', NULL, 'Depth improved, belt used'),

-- Deadlift PR
(5, 21, 'Weight x 1', 315.00, 1, NULL, '2025-01-30', NULL, 'Grip held strong, slight hitch'),

-- Shoulder Press PR
(5, 14, 'Weight x Reps', 105.00, 3, NULL, '2025-02-03', NULL, 'Strict form'),

-- Barbell Row PR
(5, 19, 'Weight x Reps', 165.00, 6, NULL, '2025-01-25', NULL, 'Maintained back angle well'),

-- Pull-up Reps PR (no weight)
(5, 25, 'Max Reps', NULL, 10, NULL, '2025-01-26', NULL, 'Last two reps were tough'),

-- Plank Hold Time PR
(5, 34, 'Time', NULL, NULL, '00:02:15', '2025-01-29', NULL, 'Goal: reach 3 minutes'),

-- Running 1 Mile Time PR (cardio)
(5, 50, 'Time', NULL, NULL, '00:07:45', '2025-01-24', NULL, 'Good pace, slight incline'),

-- Barbell Hip Thrust PR
(5, 23, 'Weight x Reps', 245.00, 6, NULL, '2025-02-03', NULL, 'Glutes activated well'),

-- Leg Press PR
(5, 30, 'Weight x Reps', 410.00, 10, NULL, '2025-01-20', NULL, 'Focused on full ROM');

INSERT INTO user_stats_log (
    user_id, date, weight, neck, waist, hips, body_fat_percentage, notes
) VALUES
(5, '2025-01-01', 180.50, 15.00, 34.50, 38.00, 18.50, 'Starting out the new year, feeling motivated'),
(5, '2025-01-08', 179.80, 15.00, 34.20, 37.90, 18.30, 'Workout consistency improving'),
(5, '2025-01-15', 179.20, NULL, 34.00, 37.80, NULL, 'Did not measure neck/body fat this week'),
(5, '2025-01-22', 178.90, 14.90, 33.90, 37.70, 18.10, NULL),
(5, '2025-01-29', 178.40, 14.90, 33.80, 37.60, 18.00, 'Waist measurement trending down'),
(5, '2025-02-05', 177.90, 14.90, 33.70, 37.50, 17.90, NULL),
(5, '2025-02-12', 177.60, NULL, 33.60, 37.40, 17.80, 'Feeling stronger in the gym'),
(5, '2025-02-19', 177.20, 14.80, NULL, 37.40, 17.70, 'Skipped waist measurement'),
(5, '2025-02-26', 176.80, 14.80, 33.40, 37.30, 17.60, 'Energy levels high'),
(5, '2025-03-05', 176.50, 14.80, 33.30, 37.20, NULL, 'Almost at target weight goal');

INSERT INTO workout_plan (
    user_id, plan_description, plan_type, number_of_days
) VALUES
-- General strength training plan
(5, 'A full-body strength program focused on compound lifts and progressive overload.', 'Strength', 3),

-- Hypertrophy (muscle growth) plan
(5, 'Split training program targeting each muscle group twice per week with moderate to high volume.', 'Hypertrophy', 5),

-- Weight loss/cardio-focused plan
(5, 'Combination of moderate lifting with high-intensity interval cardio sessions.', 'Weight Loss', 4),

-- Beginner-friendly functional fitness plan
(5, 'Functional movement workouts incorporating stability, balance, and flexibility work.', 'Functional Fitness', 3),

-- Athletic conditioning plan
(5, 'Performance-based training incorporating agility drills and power exercises.', 'Conditioning', 4);

INSERT INTO daily_workout_plan (workout_plan_id, day, wk_day, session_id) VALUES
-- Plan 4
(4, 1, 'Monday', 11),
(4, 2, 'Wednesday', 12),
(4, 3, 'Friday', 13),
(4, 4, 'Saturday', 14),

-- Plan 5
(5, 1, 'Monday', 15),
(5, 2, 'Tuesday', 16),
(5, 3, 'Thursday', 17),
(5, 4, 'Friday', 18),
(5, 5, 'Sunday', 19),

-- Plan 6
(6, 1, 'Monday', 20),
(6, 2, 'Tuesday', 21),
(6, 3, 'Thursday', 22),
(6, 4, 'Friday', 23),
(6, 5, 'Sunday', 24),

-- Plan 7
(7, 1, 'Monday', 25),
(7, 2, 'Wednesday', 26),
(7, 3, 'Friday', 27),
(7, 4, 'Saturday', 28),

-- Plan 8
(8, 1, 'Monday', 29),
(8, 2, 'Tuesday', 30),
(8, 3, 'Thursday', 31),
(8, 4, 'Friday', 32),
(8, 5, 'Sunday', 33),
(8, 6, 'Saturday', 34),
(8, 7, 'Sunday', 35);


INSERT INTO exercise_target_association (exercise_id, target_id, intensity) VALUES
-- Exercises 12–20 (example: upper body compound)
(12, 11, 'Primary'),  -- Chest
(12, 17, 'Secondary'), -- Traps
(12, 18, 'Secondary'), -- Lats
(13, 14, 'Primary'),  -- Shoulders
(13, 16, 'Secondary'), -- Triceps
(14, 15, 'Primary'),  -- Biceps
(14, 16, 'Secondary'), -- Triceps
(15, 17, 'Primary'),  -- Back
(15, 18, 'Secondary'), -- Lats
(16, 19, 'Primary'),  -- Quadriceps
(16, 20, 'Secondary'), -- Hamstrings
(17, 21, 'Primary'),  -- Glutes
(17, 19, 'Secondary'), -- Quadriceps
(18, 22, 'Primary'),  -- Calves
(19, 23, 'Primary'),  -- Lower Back
(20, 24, 'Primary'),  -- Abdominals

-- Exercises 21–30 (example: lower body and core)
(21, 19, 'Primary'),  -- Quadriceps
(21, 21, 'Secondary'), -- Glutes
(22, 20, 'Primary'),  -- Hamstrings
(22, 21, 'Secondary'), -- Glutes
(23, 21, 'Primary'),  -- Glutes
(23, 19, 'Secondary'), -- Quadriceps
(24, 24, 'Primary'),  -- Abdominals
(24, 25, 'Secondary'), -- Obliques
(25, 24, 'Primary'),  -- Abdominals
(25, 25, 'Secondary'), -- Obliques
(26, 26, 'Primary'),  -- Hips
(26, 21, 'Secondary'), -- Glutes
(27, 27, 'Primary'),  -- Spinal Erectors
(28, 28, 'Primary'),  -- Rotator Cuff
(29, 29, 'Primary'),  -- Traps
(30, 18, 'Primary'),  -- Lats

-- Exercises 31–40 (mix of upper, lower, and cardio)
(31, 11, 'Primary'),  -- Chest
(32, 16, 'Primary'),  -- Triceps
(33, 15, 'Primary'),  -- Biceps
(34, 24, 'Primary'),  -- Abdominals
(35, 25, 'Primary'),  -- Obliques
(36, 26, 'Primary'),  -- Hips
(37, 27, 'Primary'),  -- Spinal Erectors
(38, 28, 'Primary'),  -- Rotator Cuff
(39, 29, 'Primary'),  -- Traps
(40, 18, 'Primary'),  -- Lats

-- Exercises 41–50
(41, 11, 'Primary'),
(42, 12, 'Primary'),
(43, 14, 'Primary'),
(44, 15, 'Primary'),
(45, 16, 'Primary'),
(46, 19, 'Primary'),
(47, 20, 'Primary'),
(48, 21, 'Primary'),
(49, 22, 'Primary'),
(50, 23, 'Primary'),

-- Exercises 51–61
(51, 24, 'Primary'),
(52, 25, 'Primary'),
(53, 26, 'Primary'),
(54, 27, 'Primary'),
(55, 28, 'Primary'),
(56, 29, 'Primary'),
(57, 11, 'Primary'),
(58, 12, 'Primary'),
(59, 14, 'Primary'),
(60, 15, 'Primary'),
(61, 16, 'Primary');

INSERT INTO goals (
    user_id, goal_type, goal_description, target_value, current_value, unit, exercise_id, start_date, target_date, status, completion_date
) VALUES
-- Strength goal: Bench Press
(5, 'Strength', 'Increase bench press max to 200 lbs', 200.00, 185.00, 'lbs', 15, '2025-01-01', '2025-03-01', 'active', NULL),

-- Strength goal: Squat
(5, 'Strength', 'Squat 250 lbs for 5 reps', 250.00, 225.00, 'lbs', 18, '2025-01-01', '2025-03-15', 'active', NULL),

-- Strength goal: Deadlift
(5, 'Strength', 'Deadlift 325 lbs for 1 rep', 325.00, 315.00, 'lbs', 21, '2025-01-01', '2025-03-20', 'active', NULL),

-- Cardio goal: 1-mile run time
(5, 'Cardio', 'Run 1 mile under 7:30 minutes', 7.50, 7.82, 'minutes', 50, '2025-01-01', '2025-02-28', 'active', NULL),

-- Bodyweight goal
(5, 'Body Composition', 'Reduce body weight to 175 lbs', 175.00, 180.50, 'lbs', NULL, '2025-01-01', '2025-03-01', 'active', NULL),

-- Body fat percentage goal
(5, 'Body Composition', 'Lower body fat to 16%', 16.00, 18.50, '%', NULL, '2025-01-01', '2025-03-15', 'active', NULL),

-- Strength goal: Plank hold
(5, 'Core Strength', 'Hold plank for 3 minutes', 180.00, 135.00, 'seconds', 34, '2025-01-01', '2025-02-28', 'active', NULL),

-- Flexibility goal
(5, 'Flexibility', 'Touch toes without bending knees', 1.00, 0.00, 'boolean', NULL, '2025-01-01', '2025-03-01', 'active', NULL),

-- Functional strength goal: Pull-ups
(5, 'Strength', 'Perform 12 strict pull-ups', 12.00, 10.00, 'reps', 25, '2025-01-01', '2025-02-28', 'active', NULL),

-- Hip strength goal: Hip Thrust
(5, 'Strength', 'Hip thrust 260 lbs for 6 reps', 260.00, 245.00, 'lbs', 23, '2025-01-01', '2025-03-01', 'active', NULL);

INSERT INTO progress (
    user_id, exercise_id, date, period_type, max_weight, avg_weight, total_volume, workout_count
) VALUES
-- Week 1
(5, 15, '2025-01-01', 'week', 175.00, 165.00, 4950.00, 3),
(5, 18, '2025-01-01', 'week', 215.00, 205.00, 6150.00, 3),
(5, 21, '2025-01-01', 'week', 300.00, 290.00, 8700.00, 3),
(5, 14, '2025-01-01', 'week', 100.00, 95.00, 1140.00, 3),
(5, 19, '2025-01-01', 'week', 155.00, 150.00, 3000.00, 2),
(5, 25, '2025-01-01', 'week', NULL, NULL, NULL, 4),
(5, 34, '2025-01-01', 'week', NULL, NULL, NULL, 4),
(5, 23, '2025-01-01', 'week', 230.00, 220.00, 4400.00, 3),
(5, 30, '2025-01-01', 'week', 400.00, 390.00, 11700.00, 3),
(5, 33, '2025-01-01', 'week', 32.50, 30.00, 900.00, 3),

-- Week 2
(5, 15, '2025-01-08', 'week', 178.00, 168.00, 5040.00, 3),
(5, 18, '2025-01-08', 'week', 218.00, 208.00, 6240.00, 3),
(5, 21, '2025-01-08', 'week', 305.00, 295.00, 8850.00, 3),
(5, 14, '2025-01-08', 'week', 102.00, 97.00, 1161.00, 3),
(5, 19, '2025-01-08', 'week', 158.00, 152.00, 3040.00, 2),
(5, 25, '2025-01-08', 'week', NULL, NULL, NULL, 4),
(5, 34, '2025-01-08', 'week', NULL, NULL, NULL, 4),
(5, 23, '2025-01-08', 'week', 235.00, 225.00, 4500.00, 3),
(5, 30, '2025-01-08', 'week', 405.00, 395.00, 11850.00, 3),
(5, 33, '2025-01-08', 'week', 33.00, 31.00, 930.00, 3),

-- Week 3
(5, 15, '2025-01-15', 'week', 180.00, 170.00, 5100.00, 3),
(5, 18, '2025-01-15', 'week', 220.00, 210.00, 6300.00, 3),
(5, 21, '2025-01-15', 'week', 310.00, 300.00, 9000.00, 3),
(5, 14, '2025-01-15', 'week', 104.00, 98.00, 1176.00, 3),
(5, 19, '2025-01-15', 'week', 160.00, 153.00, 3060.00, 2),
(5, 25, '2025-01-15', 'week', NULL, NULL, NULL, 4),
(5, 34, '2025-01-15', 'week', NULL, NULL, NULL, 4),
(5, 23, '2025-01-15', 'week', 238.00, 228.00, 4560.00, 3),
(5, 30, '2025-01-15', 'week', 410.00, 400.00, 12000.00, 3),
(5, 33, '2025-01-15', 'week', 33.50, 31.50, 945.00, 3),

-- Week 4
(5, 15, '2025-01-22', 'week', 182.00, 172.00, 5160.00, 3),
(5, 18, '2025-01-22', 'week', 223.00, 212.00, 6360.00, 3),
(5, 21, '2025-01-22', 'week', 315.00, 305.00, 9150.00, 3),
(5, 14, '2025-01-22', 'week', 105.00, 100.00, 1200.00, 3),
(5, 19, '2025-01-22', 'week', 162.00, 155.00, 3100.00, 2),
(5, 25, '2025-01-22', 'week', NULL, NULL, NULL, 4),
(5, 34, '2025-01-22', 'week', NULL, NULL, NULL, 4),
(5, 23, '2025-01-22', 'week', 240.00, 230.00, 4600.00, 3),
(5, 30, '2025-01-22', 'week', 415.00, 405.00, 12150.00, 3),
(5, 33, '2025-01-22', 'week', 34.00, 32.00, 960.00, 3),

-- Week 5
(5, 15, '2025-01-29', 'week', 185.00, 175.00, 5250.00, 3),
(5, 18, '2025-01-29', 'week', 225.00, 215.00, 6450.00, 3),
(5, 21, '2025-01-29', 'week', 320.00, 310.00, 9300.00, 3),
(5, 14, '2025-01-29', 'week', 106.00, 101.00, 1212.00, 3),
(5, 19, '2025-01-29', 'week', 165.00, 157.00, 3140.00, 2),
(5, 25, '2025-01-29', 'week', NULL, NULL, NULL, 4),
(5, 34, '2025-01-29', 'week', NULL, NULL, NULL, 4),
(5, 23, '2025-01-29', 'week', 243.00, 233.00, 4690.00, 3),
(5, 30, '2025-01-29', 'week', 420.00, 410.00, 12300.00, 3),
(5, 33, '2025-01-29', 'week', 34.50, 32.50, 975.00, 3),

-- Week 6
(5, 15, '2025-02-05', 'week', 187.00, 177.00, 5310.00, 3),
(5, 18, '2025-02-05', 'week', 228.00, 218.00, 6540.00, 3),
(5, 21, '2025-02-05', 'week', 325.00, 315.00, 9450.00, 3),
(5, 14, '2025-02-05', 'week', 107.00, 102.00, 1224.00, 3),
(5, 19, '2025-02-05', 'week', 167.00, 159.00, 3180.00, 2),
(5, 25, '2025-02-05', 'week', NULL, NULL, NULL, 4),
(5, 34, '2025-02-05', 'week', NULL, NULL, NULL, 4),
(5, 23, '2025-02-05', 'week', 245.00, 235.00, 4710.00, 3),
(5, 30, '2025-02-05', 'week', 425.00, 415.00, 12450.00, 3),
(5, 33, '2025-02-05', 'week', 35.00, 33.00, 990.00, 3);