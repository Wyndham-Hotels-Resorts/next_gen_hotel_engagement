@echo off
REM Change to your Git repository directory
cd /d "D:\Business Intelligence\PythonScripts\next_gen_hotel_engagement"

REM Optional: log start time
echo [%date% %time%] Starting git pull >> next_gen_hotel_engagement_git_auto_pull_log.txt

REM Pull from origin main (change 'main' if needed)
git pull origin main >> next_gen_hotel_engagement_git_auto_pull_log.txt 2>&1

REM Optional: log end time
echo [%date% %time%] Finished git pull >> next_gen_hotel_engagement_git_auto_pull_log.txt