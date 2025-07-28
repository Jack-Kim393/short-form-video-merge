#!/bin/bash

# Navigate to the directory where the executable is located
cd "$(dirname "$0")"/dist

# Execute the PyInstaller-generated application
./app/app
