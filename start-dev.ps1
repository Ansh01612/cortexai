$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker was not found. Install and start Docker Desktop, then run this script again."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js, open a new PowerShell window, and run this script again."
}

Push-Location $backendRoot
try {
    docker compose up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Redis failed to start. Check Docker Desktop and run 'docker compose logs redis' from the backend folder."
    }
}
finally {
    Pop-Location
}

$services = @(
    @{ Name = "Auth"; Path = "backend\services\auth"; Port = 8001 },
    @{ Name = "Chat"; Path = "backend\services\chat"; Port = 8002 },
    @{ Name = "Agent"; Path = "backend\services\agent"; Port = 8003 },
    @{ Name = "Billing"; Path = "backend\services\billing"; Port = 8004 },
    @{ Name = "Gateway"; Path = "backend\gateway"; Port = 8000 },
    @{ Name = "Frontend"; Path = "frontend"; Port = 5173 }
)

$shellPath = Join-Path $PSHOME "powershell.exe"
if (-not (Test-Path -LiteralPath $shellPath)) {
    throw "Could not find Windows PowerShell at $shellPath."
}

foreach ($service in $services) {
    $portIsOpen = Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($portIsOpen) {
        Write-Output "$($service.Name) is already running on port $($service.Port); leaving it alone."
        continue
    }

    $servicePath = Join-Path $projectRoot $service.Path
    if (-not (Test-Path -LiteralPath (Join-Path $servicePath "package.json"))) {
        throw "Could not find package.json for $($service.Name) at $servicePath."
    }

    $command = "Set-Location -LiteralPath '$servicePath'; npm run dev"
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    Start-Process -FilePath $shellPath -ArgumentList @("-NoExit", "-EncodedCommand", $encodedCommand)
    Write-Output "Started $($service.Name) in a new PowerShell window."
}

$frontendUrl = "http://localhost:5173/"
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
        $null = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing -TimeoutSec 2
        Start-Process $frontendUrl
        Write-Output "Frontend is responding at $frontendUrl"
        exit 0
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

Write-Warning "The services were launched, but the frontend did not respond yet. Check the Frontend PowerShell window for its startup error."
exit 1
