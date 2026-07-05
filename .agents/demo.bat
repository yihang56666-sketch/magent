@echo off
chcp 65001 >nul
echo Starting Codex-only demo...
echo.
echo Preparing a sample manual run pack...
echo This will create prompts and output files for the current Codex session.
echo.

magent.exe run --task "分析这个多智能体框架的代码质量和架构设计" --scope ".agents/scripts/" --model codex-current-session

echo.
echo Open the generated agent-prompts.md file and answer each agent in the current Codex session.
echo Then run: magent.exe step latest
pause
