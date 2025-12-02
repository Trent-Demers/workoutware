# Workoutware: Installation and Setup
Workoutware is a Django-based exercise tracking application backed by a relational database (see ER diagram below). This sections explains how to setup and run the application on your local machine.

## Prerequisites
- **PYTHON VERSION 3.10+**
- **GIT**
- **PIP VERSION: 25.2**
- **MyAQL VERSION: 8.0**



## Running the Application
- Download the repository from Github
  ```
  git clone https://github.com/Trent-Demers/workoutware
  cd workoutware
  ```
- Setup MySQL container with Docker
  ```
  docker pull mysql:8.0
  docker run --name workoutware -e MYSQL_ROOT_PASSWORD=Rutgers123 -p 3306:3306 -d mysql:8.0
  ```
- Setup database

  Run scripts in the _sql_ folder (can be done using MySQL Workbench, DBeaver, or through VSCode)
- Create and activate virtual environment
  ```
  python -m venv .venv
  ```
    **Windows**
    ```
    cd .venv/Scripts
    activate
    ```

    **Mac**
    ```
    cd .venv/bin
    activate
    ```
- Installing Dependencies

  All dependencies are listed in **`requirements.txt`**.
  
  To install everything, run:
  ```
  pip install -r requirements.txt
  ```
- Linking Django to MySQL Database
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```
- Creating an Admin account (Optional but recommended)
  ```
  python manage.py createsuperuser
  ```
- Run the application & start the server
  ```
  python manage.py runserver
  ```
- To see the use of the application, **user must sign up**





## 📊 ER Diagram 

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#FFF7E6',
    'primaryTextColor': '#111111',
    'nodeBorder': '#CCCCCC',
    'lineColor': '#ffffff',
    'edgeColor': '#ffffff'
  },
  'flowchart': { 'curve': 'linear' }
}}%%
erDiagram
  USER ||--o{ USER_STATS_LOG : logs
  USER ||--o{ USER_PB : "has personal bests"
  USER ||--o{ WORKOUT_SESSIONS : performs
  WORKOUT_SESSIONS ||--o{ SESSION_EXERCISES : contains
  SESSION_EXERCISES ||--o{ SETS : consists_of
  EXERCISE ||--o{ SESSION_EXERCISES : used_in
  EXERCISE ||--o{ EXERCISE_TARGET_ASSOCIATION : linked_with
  TARGET ||--o{ EXERCISE_TARGET_ASSOCIATION : "has targets"
  USER ||--o{ PROGRESS : "tracks performance"
  EXERCISE ||--o{ PROGRESS : "progress per exercise"
  USER ||--o{ GOALS : "sets goals"
  USER ||--o{ WORKOUT_PLAN : "has plan"
  WORKOUT_PLAN ||--o{ DAILY_WORKOUT_PLAN : includes
  USER ||--o{ DATA_VALIDATION : validates
  EXERCISE ||--o{ DATA_VALIDATION : validated_on
  SETS ||--o{ DATA_VALIDATION : "validation per set"

  USER { 
    int user_id PK
    string first_name
    string last_name
    string address
    string town
    string state
    string country
    string email
    string phone_number
    string password_hash
    date date_of_birth
    decimal height
    date date_registered
    date date_unregistered
    boolean registered
    string fitness_goal
    string user_type 
  }

  USER_STATS_LOG {
    int log_id PK
    int user_id FK
    date date
    decimal weight
    decimal neck
    decimal waist
    decimal hips
    decimal body_fat_percentage
    string notes
  }

  EXERCISE {
    int exercise_id PK
    string name
    string type
    string subtype
    string equipment
    int difficulty
    string description
    string demo_link
  }

  TARGET {
    int target_id PK
    string target_name
    string target_group
    string target_function
  }

  EXERCISE_TARGET_ASSOCIATION {
    int association_id PK
    int exercise_id FK
    int target_id FK
    string intensity
  }

  USER_PB {
    int pr_id PK
    int user_id FK
    int exercise_id FK
    string pr_type
    decimal pb_weight
    int pb_reps
    time pb_time
    date pb_date
    decimal previous_pr
    string notes
  }

  WORKOUT_SESSIONS {
    int session_id PK
    int user_id FK
    string session_name
    date session_date
    time start_time
    time end_time
    int duration_minutes
    decimal bodyweight
    boolean completed
    int is_template
  }

  SESSION_EXERCISES {
    int session_exercise_id PK
    int session_id FK
    int exercise_id FK
    int exercise_order
    int target_sets
    int target_reps
    boolean completed
  }

  SETS {
    int set_id PK
    int session_exercise_id FK
    int set_number
    decimal weight
    int reps
    int rpe
    boolean completed
    boolean is_warmup
    datetime completion_time
  }

  GOALS {
    int goal_id PK
    int user_id FK
    string goal_type
    string goal_description
    decimal target_value
    decimal current_value
    string unit
    int exercise_id FK
    date start_date
    date target_date
    string status
    date completion_date
  }

  PROGRESS {
    int progress_id PK
    int user_id FK
    int exercise_id FK
    date date
    string period_type
    decimal max_weight
    decimal avg_weight
    decimal total_volume
    int workout_count
  }

  DATA_VALIDATION {
    int validation_id PK
    int user_id FK
    int set_id FK
    int exercise_id FK
    decimal input_weight
    decimal expected_max
    string flagged_as
    string user_action
    datetime timestamp
  }

  WORKOUT_PLAN {
    int plan_id PK
    int user_id FK
    string plan_description
    string plan_type
    int number_of_days
  }

  DAILY_WORKOUT_PLAN {
    int daily_plan_id PK
    int workout_plan_id FK
    int day
    string wk_day
    int session_id FK
  }


