# ================================================================================
# WORKOUTWARE INSTALLATION SCRIPT (Windows PowerShell)
# ================================================================================
# This script automates setup for the Workoutware application on Windows.
#
# PREREQUISITES:
#   - Python 3.10+ installed
#   - pip 25.2+ installed
#   - MySQL 8.0 (or Docker Desktop)
#   - Git installed
#   - Docker Desktop installed (for containerized MySQL)
#
# USAGE:
#   powershell -ExecutionPolicy Bypass -File install.ps1
# ================================================================================

Write-Host "=========================================="
Write-Host "Workoutware Installation Script (Windows)"
Write-Host "==========================================`n"

# Step 1: Clone repository
if (!(Test-Path ".git")) {
    Write-Host "Step 1: Cloning repository from GitHub..."
    git clone https://github.com/Trent-Demers/workoutware
    Set-Location workoutware
} else {
    Write-Host "Step 1: Repository already exists, skipping..."
}

# Step 2: Setup MySQL Docker container
Write-Host "`nStep 2: Setting up MySQL container with Docker..."
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed. Install Docker Desktop first."
    exit 1
}

Write-Host "Pulling MySQL 8.0 image..."
docker pull mysql:8.0

Write-Host "Checking for existing container..."
$containerExists = docker ps -a --format "{{.Names}}" | Select-String "^workoutware$"

if ($containerExists) {
    Write-Host "Container 'workoutware' already exists. Starting it..."
    docker start workoutware
} else {
    Write-Host "Creating new MySQL container..."
    docker run --name workoutware `
        -e MYSQL_ROOT_PASSWORD=Rutgers123 `
        -p 3306:3306 `
        -d mysql:8.0

    Write-Host "Waiting 30 seconds for MySQL to initialize..."
    Start-Sleep -Seconds 30
}

# Step 3: Database schema instructions
Write-Host "`nStep 3: Database schema setup..."
Write-Host "IMPORTANT: You must manually run the SQL scripts from the 'sql' folder:"
Write-Host "  - sql/workoutware_db_setup.sql"
Write-Host "  - sql/sample_data.sql (optional)"
Write-Host "`nUse MySQL Workbench, DBeaver, or:"
Write-Host "  mysql -u root -pRutgers123 < sql/workoutware_db_setup.sql"
Read-Host "Press Enter after running the database setup scripts..."

# Step 4: Setup Python virtual environment
Write-Host "`nStep 4: Creating Python virtual environment..."
if (!(Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "Virtual environment created."
} else {
    Write-Host "Virtual environment already exists."
}

# Step 5: Activate virtual environment
Write-Host "`nStep 5: Activating virtual environment..."
Write-Host "To activate manually in PowerShell, run:"
Write-Host "  .\.venv\Scripts\Activate.ps1"

. ".\.venv\Scripts\Activate.ps1"

# Step 6: Install dependencies
Write-Host "`nStep 6: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Dependencies installed."

# Step 7: Run migrations
Write-Host "`nStep 7: Running Django migrations..."
python manage.py makemigrations
python manage.py migrate
Write-Host "Migrations complete."

# Step 8: Create admin user
Write-Host "`nStep 8: Create Django admin user"
$admin = Read-Host "Do you want to create a superuser now? (y/n)"
if ($admin -eq "y" -or $admin -eq "Y") {
    python manage.py createsuperuser
}

# Step 9: Optional: Start Django server
Write-Host "`n=========================================="
Write-Host "Installation Complete!"
Write-Host "==========================================`n"
Write-Host "Start Django server:"
Write-Host "  python manage.py runserver`n"
Write-Host "Start Streamlit:"
Write-Host "  streamlit run streamlit_client/app.py`n"

$startServer = Read-Host "Start Django server now? (y/n)"
if ($startServer -eq "y" -or $startServer -eq "Y") {
    python manage.py runserver
}
