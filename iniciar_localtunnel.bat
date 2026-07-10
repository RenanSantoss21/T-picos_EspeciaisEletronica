@echo off
:loop
echo ========================================================
echo Iniciando o LocalTunnel... (pressione Ctrl+C para parar)
echo ========================================================
npx localtunnel --port 8000 --subdomain controle-processos-renan
echo.
echo LocalTunnel caiu ou foi fechado! Reiniciando em 3 segundos...
timeout /t 3
goto loop
