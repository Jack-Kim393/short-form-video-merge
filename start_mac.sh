#!/bin/bash

# ANSI Color Codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Shortform Video Editor Setup & Launch ---${NC}"

# 1. Check for Python 3
echo -e "\n${CYAN}[Step 1/5] Checking for Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3 from python.org or via Homebrew (brew install python)."
    exit 1
fi
echo "Python 3 found: $(python3 --version)"

# 2. Recreate Virtual Environment
echo -e "\n${CYAN}[Step 2/5] Setting up a clean virtual environment...${NC}"
if [ -d ".venv" ]; then
    echo "Removing old virtual environment."
    rm -rf .venv
fi
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create virtual environment.${NC}"
    exit 1
fi
echo "Virtual environment created successfully."

# 3. Install Dependencies
echo -e "\n${CYAN}[Step 3/5] Installing required libraries...${NC}"
# Use the pip from the virtual environment directly
./.venv/bin/python3 -m pip install --upgrade pip > /dev/null
./.venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install libraries from requirements.txt.${NC}"
    echo "Please check your internet connection and the console output above for errors."
    exit 1
fi
echo "Libraries installed."

# 4. Verify Installation
echo -e "\n${CYAN}[Step 4/5] Verifying library installation...${NC}"
echo "--- Installed Packages List ---"
./.venv/bin/pip freeze
echo "-----------------------------"

echo "\nAttempting to import 'moviepy.editor' directly..."
./.venv/bin/python3 -c "import moviepy.editor"
if [ $? -ne 0 ]; then
    echo -e "\n${RED}Error: Verification FAILED. The 'moviepy' library could not be imported.${NC}"
    echo "The installation appears to be broken. Please review the installation logs above."
    exit 1
fi
echo -e "${GREEN}Verification successful! 'moviepy' is installed correctly.${NC}"

# 5. Run the Streamlit App
echo -e "\n${CYAN}[Step 5/5] Starting the application...${NC}"
echo "Your web browser will open with the application shortly."
./.venv/bin/streamlit run app.py

echo -e "\n${GREEN}Application has been closed. Exiting script.${NC}"
