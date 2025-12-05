# AgentX Trading Bot - PowerShell Deployment Script
# APPS Holdings WY, Inc.
# Deploys and manages the trading bot on Windows systems

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('paper', 'live')]
    [string]$Mode = 'paper',

    [Parameter(Mandatory=$false)]
    [switch]$Install,

    [Parameter(Mandatory=$false)]
    [switch]$Start,

    [Parameter(Mandatory=$false)]
    [switch]$Stop,

    [Parameter(Mandatory=$false)]
    [switch]$Status,

    [Parameter(Mandatory=$false)]
    [switch]$Logs
)

$ErrorActionPreference = "Stop"
$BotName = "AgentX-TradingBot"
$BotPath = "$PSScriptRoot\..\trading_bot"
$LogPath = "$BotPath\logs"
$PidFile = "$BotPath\bot.pid"

# Banner
function Show-Banner {
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "AgentX Trading Bot - Deployment Manager" -ForegroundColor Cyan
    Write-Host "APPS Holdings WY, Inc." -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host ""
}

# Check if Python is installed
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
        return $false
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow

    Set-Location $BotPath

    # Check if venv exists
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }

    # Activate venv
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"

    # Install requirements
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    # Create directories
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }

    # Check for .env file
    if (-not (Test-Path ".env")) {
        Write-Host "`n⚠ WARNING: .env file not found!" -ForegroundColor Yellow
        Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "`nPlease edit .env with your Kraken API credentials:" -ForegroundColor Cyan
        Write-Host "  $BotPath\.env" -ForegroundColor Cyan
        Write-Host ""
    }

    Write-Host "✓ Installation complete!" -ForegroundColor Green
}

# Start the bot
function Start-Bot {
    param([string]$TradingMode)

    Set-Location $BotPath

    # Check if already running
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
            Write-Host "✗ Bot is already running (PID: $pid)" -ForegroundColor Yellow
            return
        }
        else {
            Remove-Item $PidFile
        }
    }

    Write-Host "`nStarting bot in $TradingMode mode..." -ForegroundColor Yellow

    # Activate venv
    & ".\venv\Scripts\Activate.ps1"

    # Set trading mode
    $env:TRADING_MODE = $TradingMode

    # Start bot in background
    if ($TradingMode -eq 'live') {
        Write-Host "`n⚠ WARNING: Starting in LIVE trading mode!" -ForegroundColor Red
        $confirm = Read-Host "Are you sure? (yes/no)"
        if ($confirm -ne 'yes') {
            Write-Host "Cancelled." -ForegroundColor Yellow
            return
        }
        $process = Start-Process -FilePath "python" -ArgumentList "main.py --live" -PassThru -WindowStyle Hidden
    }
    else {
        Write-Host "Paper trading mode - no real money at risk" -ForegroundColor Green
        $process = Start-Process -FilePath "python" -ArgumentList "main.py" -PassThru -WindowStyle Hidden
    }

    # Save PID
    $process.Id | Out-File $PidFile

    Write-Host "✓ Bot started (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "`nMonitor logs with:" -ForegroundColor Cyan
    Write-Host "  .\deploy_trading_bot.ps1 -Logs" -ForegroundColor Cyan
}

# Stop the bot
function Stop-Bot {
    if (-not (Test-Path $PidFile)) {
        Write-Host "✗ Bot is not running" -ForegroundColor Yellow
        return
    }

    $pid = Get-Content $PidFile

    try {
        $process = Get-Process -Id $pid -ErrorAction Stop
        Write-Host "`nStopping bot (PID: $pid)..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
        Remove-Item $PidFile
        Write-Host "✓ Bot stopped" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Process not found (PID: $pid)" -ForegroundColor Red
        Remove-Item $PidFile
    }
}

# Check bot status
function Get-BotStatus {
    Write-Host "`nBot Status:" -ForegroundColor Cyan
    Write-Host "-" * 40

    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue

        if ($process) {
            Write-Host "Status: RUNNING" -ForegroundColor Green
            Write-Host "PID: $pid"
            Write-Host "CPU: $($process.CPU)s"
            Write-Host "Memory: $([math]::Round($process.WorkingSet / 1MB, 2)) MB"
            Write-Host "Started: $($process.StartTime)"
        }
        else {
            Write-Host "Status: STOPPED (stale PID file)" -ForegroundColor Red
            Remove-Item $PidFile
        }
    }
    else {
        Write-Host "Status: STOPPED" -ForegroundColor Yellow
    }

    # Check for .env
    if (Test-Path "$BotPath\.env") {
        Write-Host "Config: .env found" -ForegroundColor Green
    }
    else {
        Write-Host "Config: .env NOT FOUND" -ForegroundColor Red
    }

    # Check logs
    if (Test-Path "$LogPath\trading_agent.log") {
        $logInfo = Get-Item "$LogPath\trading_agent.log"
        Write-Host "Log file: $([math]::Round($logInfo.Length / 1KB, 2)) KB"
        Write-Host "Last modified: $($logInfo.LastWriteTime)"
    }
}

# View logs
function Show-Logs {
    $logFile = "$LogPath\trading_agent.log"

    if (-not (Test-Path $logFile)) {
        Write-Host "✗ Log file not found: $logFile" -ForegroundColor Red
        return
    }

    Write-Host "`nShowing last 50 lines of log (press Ctrl+C to exit):" -ForegroundColor Cyan
    Write-Host "-" * 80

    Get-Content $logFile -Tail 50 -Wait
}

# Main
Show-Banner

if (-not (Test-Python)) {
    exit 1
}

if ($Install) {
    Install-Dependencies
}
elseif ($Start) {
    Start-Bot -TradingMode $Mode
}
elseif ($Stop) {
    Stop-Bot
}
elseif ($Status) {
    Get-BotStatus
}
elseif ($Logs) {
    Show-Logs
}
else {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\deploy_trading_bot.ps1 -Install              Install dependencies"
    Write-Host "  .\deploy_trading_bot.ps1 -Start [-Mode paper]  Start bot (paper trading)"
    Write-Host "  .\deploy_trading_bot.ps1 -Start -Mode live     Start bot (LIVE trading)"
    Write-Host "  .\deploy_trading_bot.ps1 -Stop                 Stop bot"
    Write-Host "  .\deploy_trading_bot.ps1 -Status               Check status"
    Write-Host "  .\deploy_trading_bot.ps1 -Logs                 View logs"
    Write-Host ""
}
