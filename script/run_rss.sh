#!/bin/bash

#this is a script file to be run by scheduler every hour, use4 bash interpreter 
#aeroroutes is updated hourly

#get the script parent folder, then move into that directory
SCRIPT_DIR="$(cd "$(dirname "$BASH_SOURCE[0]")" && pwd)"

PROJECT_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"

cd "$PROJECT_DIR"

mkdir -p log

TIMESTAMP=$(date +"%Y-%m-%d_%H")

#filename inside data
LOG_FILE="log/log_$TIMESTAMP.txt"
#dumb dumb, crontab is running but u stupid input the wrong folder name

#run python from the root folder, then save output console to root file
"$PROJECT_DIR/.venv_aeroroutes/bin/python" src/rss_client.py > "$LOG_FILE" 2>&1
#stderror is redirected to wherever stdout is going, LOG_FILE
