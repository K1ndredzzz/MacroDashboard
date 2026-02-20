@echo off
REM Configure Cloud Scheduler for FRED data collection

set PROJECT_ID=gen-lang-client-0815236933
set REGION=us-central1
set JOB_NAME=ingest-fred-daily

echo Configuring Cloud Scheduler...
echo Project: %PROJECT_ID%
echo Job: %JOB_NAME%
echo.

REM Get function URL
for /f "delims=" %%i in ('gcloud functions describe ingest-fred --region=%REGION% --project=%PROJECT_ID% --gen2 --format="value(serviceConfig.uri)"') do set FUNCTION_URL=%%i

echo Function URL: %FUNCTION_URL%
echo.

REM Create scheduler job (runs daily at 8 AM UTC)
gcloud scheduler jobs create http %JOB_NAME% ^
  --location=%REGION% ^
  --schedule="0 8 * * *" ^
  --uri="%FUNCTION_URL%" ^
  --http-method=POST ^
  --headers="Content-Type=application/json" ^
  --message-body="{\"lookback_days\": 7}" ^
  --time-zone="UTC" ^
  --project=%PROJECT_ID%

echo.
echo Scheduler configured successfully!
echo Schedule: Daily at 8:00 AM UTC

pause
