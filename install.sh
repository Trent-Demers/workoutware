#!/bin/bash
# ================================================================================
# WORKOUTWARE INSTALLATION SCRIPT
# ================================================================================
# This script automates the setup process for Workoutware application.
# Run this script from the project root directory after cloning the repository.
#
# PREREQUISITES:
#   - Python 3.10+ installed
#   - pip version 25.2+ installed
#   - MySQL 8.0 (or Docker for containerized MySQL)
#   - Git installed
#   - Docker installed (if using containerized MySQL)
#
# USAGE:
#   chmod +x install.sh
#   ./install.sh
#
# NOTE: This script is for Mac/Linux. For Windows, use the commands manually
#       or adapt for PowerShell.
# ================================================================================

# PYTHON VERSION: 3.12.1
# PIP VERSION: 25.2
# MySQL VERSION: 8.0

echo "=========================================="
echo "Workoutware Installation Script"
echo "=========================================="
echo ""

# Step 1: Download repository from GitHub (if not already cloned)
if [ ! -d ".git" ]; then
    echo "Step 1: Cloning repository from GitHub..."
    git clone https://github.com/Trent-Demers/workoutware
    cd workoutware
else
    echo "Step 1: Repository already cloned, skipping..."
fi

# Step 2: Setup MySQL container with Docker
echo ""
echo "Step 2: Setting up MySQL container with Docker..."
echo "Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

echo "Pulling MySQL 8.0 image..."
docker pull mysql:8.0

echo "Creating MySQL container..."
# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^workoutware$"; then
    echo "Container 'workoutware' already exists. Starting it..."
    docker start workoutware
else
    echo "Creating new MySQL container..."
    docker run --name workoutware -e MYSQL_ROOT_PASSWORD=Rutgers123 -p 3306:3306 -d mysql:8.0
    echo "Waiting for MySQL to initialize (30 seconds)..."
    sleep 30
fi

# Step 3: Setup database schema
echo ""
echo "Step 3: Database schema setup..."
echo "IMPORTANT: You must manually run SQL scripts from the 'sql' folder:"
echo "  - sql/workoutware_db_setup.sql (creates database and tables)"
echo "  - sql/sample_data.sql (optional, adds sample data)"
echo ""
echo "You can use MySQL Workbench, DBeaver, or VSCode to execute these scripts."
echo "Or run: mysql -u root -pRutgers123 < sql/workoutware_db_setup.sql"
read -p "Press Enter after you've run the database setup scripts..."

# Step 4: Setup Python virtual environment
echo ""
echo "Step 4: Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Step 5: Activate virtual environment
echo ""
echo "Step 5: Activating virtual environment..."
echo "To activate manually, run:"
echo "  source .venv/bin/activate"
source .venv/bin/activate

# Step 6: Install dependencies
echo ""
echo "Step 6: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed."

# Step 7: Link Django to MySQL database
echo ""
echo "Step 7: Linking Django to MySQL database..."
python manage.py makemigrations
python manage.py migrate
echo "Migrations completed."

# Step 8: Create admin user (optional)
echo ""
echo "Step 8: Creating admin user (optional)..."
read -p "Do you want to create a superuser/admin account? (y/n): " create_admin
if [ "$create_admin" = "y" ] || [ "$create_admin" = "Y" ]; then
    python manage.py createsuperuser
fi

# Step 9: Start the server
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To start the Django server, run:"
echo "  python manage.py runserver"
echo ""
echo "To start the Streamlit client (in a separate terminal), run:"
echo "  streamlit run streamlit_client/app.py"
echo ""
echo "IMPORTANT: Users must sign up to use the application."
echo ""
read -p "Do you want to start the Django server now? (y/n): " start_server
if [ "$start_server" = "y" ] || [ "$start_server" = "Y" ]; then
    echo "Starting Django development server..."
    python manage.py runserver
fi
