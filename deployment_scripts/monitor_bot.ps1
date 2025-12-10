# AgentX Trading Bot - Monitoring Script
# Real-time performance monitoring and alerts

param(
    [Parameter(Mandatory=$false)]
    [int]$RefreshSeconds = 30
)

$BotPath = "$PSScriptRoot\..\trading_bot"
$LogPath = "$BotPath\logs\trading_agent.log"

function Show-Dashboard {
    Clear-Host

    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "AgentX Trading Bot - Live Dashboard" -ForegroundColor Cyan
    Write-Host "APPS Holdings WY, Inc." -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "Refresh: ${RefreshSeconds}s | Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""

    # Check if bot is running
    $pidFile = "$BotPath\bot.pid"
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue

        if ($process) {
            Write-Host "Bot Status: RUNNING" -ForegroundColor Green
            Write-Host "PID: $pid | CPU: $([math]::Round($process.CPU, 2))s | Memory: $([math]::Round($process.WorkingSet / 1MB, 2)) MB"
        }
        else {
            Write-Host "Bot Status: STOPPED" -ForegroundColor Red
        }
    }
    else {
        Write-Host "Bot Status: STOPPED" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Recent Activity:" -ForegroundColor Yellow
    Write-Host "-" * 80

    # Parse log for key metrics
    if (Test-Path $LogPath) {
        $recentLines = Get-Content $LogPath -Tail 100

        # Find positions
        $positions = $recentLines | Select-String "Position opened" | Select-Object -Last 5
        if ($positions) {
            Write-Host "`nRecent Positions:" -ForegroundColor Cyan
            $positions | ForEach-Object { Write-Host "  $_" }
        }

        # Find closures
        $closures = $recentLines | Select-String "Position closed" | Select-Object -Last 5
        if ($closures) {
            Write-Host "`nRecent Closures:" -ForegroundColor Cyan
            $closures | ForEach-Object { Write-Host "  $_" }
        }

        # Find capital status
        $capitalLines = $recentLines | Select-String "Capital:" | Select-Object -Last 1
        if ($capitalLines) {
            Write-Host "`nCurrent Status:" -ForegroundColor Cyan
            Write-Host "  $capitalLines"
        }

        # Find errors
        $errors = $recentLines | Select-String "ERROR" | Select-Object -Last 5
        if ($errors) {
            Write-Host "`nRecent Errors:" -ForegroundColor Red
            $errors | ForEach-Object { Write-Host "  $_" }
        }
    }
    else {
        Write-Host "No log file found" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "-" * 80
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
}

# Main loop
Write-Host "Starting live monitoring..." -ForegroundColor Green
Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    Show-Dashboard
    Start-Sleep -Seconds $RefreshSeconds
}
