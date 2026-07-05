@echo off
chcp 65001 >nul
echo Creating mock execution for Dashboard demo...
echo.

REM Create mock run directory
set RUN_ID=20260610-180000-demo
set RUN_DIR=..\reports\runs\%RUN_ID%
mkdir "%RUN_DIR%" 2>nul

REM Create dispatch plan
echo {"dispatch_plan":[{"id":"security-1","agent_type":"security-engineer","task":"安全审计"},{"id":"architect-1","agent_type":"software-architect","task":"架构分析"},{"id":"backend-1","agent_type":"backend-api-engineer","task":"API设计"}],"total":3} > "%RUN_DIR%\dispatch-plan.json"

REM Create execution summary
echo {"total":3,"completed":2,"failed":0,"total_tokens":5420,"elapsed_seconds":18.5,"results":[{"agent_id":"security-1","agent_type":"security-engineer","status":"completed","tokens":2100},{"agent_id":"architect-1","agent_type":"software-architect","status":"running","tokens":0},{"agent_id":"backend-1","agent_type":"backend-api-engineer","status":"pending","tokens":0}]} > "%RUN_DIR%\execution-summary.json"

REM Create event stream
echo {"timestamp":1000000001,"type":"agent_start","data":{"agent_id":"security-1"}} > "%RUN_DIR%\stream.jsonl"
echo {"timestamp":1000000012,"type":"agent_complete","data":{"agent_id":"security-1","tokens":2100}} >> "%RUN_DIR%\stream.jsonl"
echo {"timestamp":1000000013,"type":"agent_start","data":{"agent_id":"architect-1"}} >> "%RUN_DIR%\stream.jsonl"

echo.
echo Mock data created!
echo Open Dashboard and navigate to: http://localhost:8080/dashboard-live.html?run=%RUN_ID%
echo.
echo You'll see:
echo   - 1 completed agent (cyan)
echo   - 1 running agent (gold, pulsing)
echo   - 1 pending agent (gray)
echo   - Event stream showing start/complete
echo   - Concurrency slots active
echo.
pause
