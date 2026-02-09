# Startup Script for StreamLink Backend Services

Write-Host "Starting StreamLink Backend Services..." -ForegroundColor Green

# 1. Start Redis (assuming Docker is installed and running)
# Check if Redis container is running
$redisContainer = docker ps -q -f name=streamlink_redis
if (-not $redisContainer) {
    Write-Host "Starting Redis container..." -ForegroundColor Cyan
    docker-compose up -d redis
} else {
    Write-Host "Redis is already running." -ForegroundColor Green
}

# Function to start a python service in a new window
function Start-Service {
    param (
        [string]$Name,
        [string]$Path,
        [string]$Port
    )
    
    $cmd = "cd $Path; if (Test-Path venv) { .\venv\Scripts\activate } else { Write-Host 'venv not found, trying global python...'; }; python main.py"
    
    Write-Host "Starting $Name on port $Port..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "$cmd"
}

# 2. Start Management Layer (Port 8000 + gRPC 50051)
Start-Service -Name "Management Layer" -Path "management_layer" -Port "8000"

# 3. Start Signaling Layer (Port 8001)
Start-Service -Name "Signaling Layer" -Path "signaling_layer" -Port "8001"

Write-Host "Services started! Check the new windows for logs." -ForegroundColor Green
Write-Host "Ensure your frontend is running (npm run dev in client_layer)." -ForegroundColor Yellow
