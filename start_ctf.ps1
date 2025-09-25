# CTF Platform Startup Script
# This script starts both the backend and frontend servers

# Global variables for process tracking
$script:backendProcess = $null
$script:frontendProcess = $null

# Function to check if database exists and has data
function Test-Database {
    $envFile = Join-Path $PSScriptRoot ".env"
    $databaseUrl = "sqlite:///ctf_platform.db"  # Default database
    
    # Read database URL from .env file if it exists
    if (Test-Path $envFile) {
        $envContent = Get-Content $envFile
        foreach ($line in $envContent) {
            if ($line -match "^DATABASE_URL=(.+)$") {
                $databaseUrl = $matches[1]
                break
            }
        }
    }
    
    # Extract database file path from SQLite URL
    if ($databaseUrl -match "sqlite:///(.+)") {
        $dbPath = $matches[1]
        
        # Check both possible locations: server directory and instance directory
        $fullDbPath1 = Join-Path $PSScriptRoot "server\$dbPath"
        $fullDbPath2 = Join-Path $PSScriptRoot "server\instance\$dbPath"
        
        # Check if database file exists and has content
        $dbFile = $null
        if (Test-Path $fullDbPath1) {
            $dbFile = $fullDbPath1
        } elseif (Test-Path $fullDbPath2) {
            $dbFile = $fullDbPath2
        }
        
        if ($dbFile) {
            $fileSize = (Get-Item $dbFile).Length
            if ($fileSize -gt 0) {
                Write-Host "✅ Database found and has data" -ForegroundColor Green
                return $true
            }
        }
    }
    
    Write-Host "⚠️  Database not found or empty, will initialize..." -ForegroundColor Yellow
    return $false
}

# Function to initialize database
function Initialize-Database {
    Write-Host "🔧 Initializing database with sample data..." -ForegroundColor Blue
    $serverPath = Join-Path $PSScriptRoot "server"
    $sampleDataPath = Join-Path $serverPath "utils\sample_data.py"
    
    try {
        Push-Location $serverPath
        $result = & python "utils\sample_data.py" 2>&1
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database initialized successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to initialize database: $result" -ForegroundColor Red
            return $false
        }
    } catch {
        Pop-Location
        Write-Host "❌ Error initializing database: $_" -ForegroundColor Red
        return $false
    }
}

# Function to cleanup processes
function Stop-AllProcesses {
    Write-Host "🛑 Stopping CTF Platform..." -ForegroundColor Yellow
    
    # Stop the main processes
    if ($script:backendProcess -and !$script:backendProcess.HasExited) {
        Write-Host "   Stopping backend server..." -ForegroundColor Yellow
        $script:backendProcess.Kill()
        $script:backendProcess.WaitForExit(3000) # Wait up to 3 seconds
    }
    if ($script:frontendProcess -and !$script:frontendProcess.HasExited) {
        Write-Host "   Stopping frontend server..." -ForegroundColor Yellow
        $script:frontendProcess.Kill()
        $script:frontendProcess.WaitForExit(3000) # Wait up to 3 seconds
    }
    
    # Kill any remaining Python/Node processes that might be orphaned
    Write-Host "   Cleaning up orphaned processes..." -ForegroundColor Yellow
    try {
        Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*app.py*" -or $_.CommandLine -like "*app.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*npm run dev*" -or $_.CommandLine -like "*vite*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    } catch {
        # Ignore errors when killing processes
    }
    
    Write-Host "✅ CTF Platform stopped" -ForegroundColor Green
    exit 0
}

# Create a cleanup script that will be executed when the launcher exits
$cleanupScriptContent = @"
# CTF Platform Cleanup Script
Write-Host "Cleaning up CTF Platform processes..." -ForegroundColor Yellow

# Kill any Python processes running app.py
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    try { 
        `$_.CommandLine -like "*app.py*" -or `$_.MainWindowTitle -like "*app.py*" 
    } catch { 
        `$false 
    } 
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill any Node processes running npm run dev or vite
Get-Process node -ErrorAction SilentlyContinue | Where-Object { 
    try { 
        `$_.CommandLine -like "*npm run dev*" -or `$_.CommandLine -like "*vite*" 
    } catch { 
        `$false 
    } 
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete." -ForegroundColor Green
"@

$cleanupScriptPath = Join-Path $env:TEMP "ctf_cleanup_$PID.ps1"
$cleanupScriptContent | Out-File -FilePath $cleanupScriptPath -Encoding UTF8

# Register cleanup function for Ctrl+C
Register-EngineEvent -SourceId PowerShell.Exiting -Action { 
    if (Test-Path $cleanupScriptPath) {
        & $cleanupScriptPath
        Remove-Item $cleanupScriptPath -Force -ErrorAction SilentlyContinue
    }
    Stop-AllProcesses 
} | Out-Null

Write-Host "🚀 Starting CTF Platform..." -ForegroundColor Green
Write-Host ""

# Check and initialize database if needed
if (-not (Test-Database)) {
    Write-Host ""
    if (-not (Initialize-Database)) {
        Write-Host "❌ Failed to initialize database. Please check the error messages above." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Function to check if a port is available
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to wait for a service to be ready
function Wait-ForService {
    param([int]$Port, [string]$ServiceName)
    Write-Host "⏳ Waiting for $ServiceName to start on port $Port..." -ForegroundColor Yellow
    $timeout = 30
    $elapsed = 0
    
    while ($elapsed -lt $timeout) {
        if (Test-Port -Port $Port) {
            Write-Host "✅ $ServiceName is ready!" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }
    
    Write-Host "❌ $ServiceName failed to start within $timeout seconds" -ForegroundColor Red
    return $false
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "🐍 Python found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Python not found! Please install Python and try again." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "📦 Node.js found: $nodeVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Start Backend Server in new window
Write-Host "🔧 Starting Backend Server..." -ForegroundColor Blue
$backendCommand = @"
cd '$PWD\server'
Write-Host 'Backend Server - Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host 'Closing this window will stop the backend server' -ForegroundColor Cyan
python app.py
"@
$script:backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal -PassThru

# Wait for backend to start
if (Wait-ForService -Port 5000 -ServiceName "Backend Server") {
    Write-Host ""
    
# Start Frontend Server in new window
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Blue
$frontendCommand = @"
cd '$PWD\client'
Write-Host 'Frontend Server - Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host 'Closing this window will stop the frontend server' -ForegroundColor Cyan
npm run dev
"@
$script:frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal -PassThru
    
    # Wait for frontend to start
    if (Wait-ForService -Port 3000 -ServiceName "Frontend Server") {
        Write-Host ""
        Write-Host "🎉 CTF Platform is running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📡 Services:" -ForegroundColor White
        Write-Host "   Backend:  http://localhost:5000" -ForegroundColor Cyan
        Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        # Read admin credentials from .env file
        $envFile = Join-Path $PSScriptRoot ".env"
        $adminUsername = "admin"
        $adminPassword = "admin123!"
        
        if (Test-Path $envFile) {
            $envContent = Get-Content $envFile
            foreach ($line in $envContent) {
                if ($line -match "^ADMIN_USERNAME=(.+)$") {
                    $adminUsername = $matches[1]
                }
                if ($line -match "^ADMIN_PASSWORD=(.+)$") {
                    $adminPassword = $matches[1]
                }
            }
        }
        
        Write-Host "🔐 Admin Login:" -ForegroundColor White
        Write-Host "   Username: $adminUsername" -ForegroundColor Yellow
        Write-Host "   Password: $adminPassword" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to stop all services" -ForegroundColor Gray
        
        # Function to perform graceful cleanup
        function Stop-CTFPlatform {
            Write-Host ""
            Write-Host "🛑 Stopping CTF Platform..." -ForegroundColor Yellow
            
            # Stop backend server gracefully
            if ($script:backendProcess -and !$script:backendProcess.HasExited) {
                Write-Host "   Stopping backend server..." -ForegroundColor Yellow
                try {
                    $script:backendProcess.CloseMainWindow()
                    if (!$script:backendProcess.WaitForExit(5000)) {
                        Write-Host "   Force stopping backend server..." -ForegroundColor Yellow
                        $script:backendProcess.Kill()
                    }
                } catch {
                    Write-Host "   Backend server stopped" -ForegroundColor Green
                }
            }
            
            # Stop frontend server gracefully
            if ($script:frontendProcess -and !$script:frontendProcess.HasExited) {
                Write-Host "   Stopping frontend server..." -ForegroundColor Yellow
                try {
                    $script:frontendProcess.CloseMainWindow()
                    if (!$script:frontendProcess.WaitForExit(5000)) {
                        Write-Host "   Force stopping frontend server..." -ForegroundColor Yellow
                        $script:frontendProcess.Kill()
                    }
                } catch {
                    Write-Host "   Frontend server stopped" -ForegroundColor Green
                }
            }
            
            # Clean up any remaining processes
            Write-Host "   Cleaning up remaining processes..." -ForegroundColor Yellow
            Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
                try { 
                    $_.CommandLine -like "*app.py*" -or $_.MainWindowTitle -like "*app.py*" 
                } catch { 
                    $false 
                } 
            } | Stop-Process -Force -ErrorAction SilentlyContinue
            
            Get-Process node -ErrorAction SilentlyContinue | Where-Object { 
                try { 
                    $_.CommandLine -like "*npm run dev*" -or $_.CommandLine -like "*vite*" 
                } catch { 
                    $false 
                } 
            } | Stop-Process -Force -ErrorAction SilentlyContinue
            
            Write-Host "✅ CTF Platform stopped" -ForegroundColor Green
        }

        # Register cleanup function for Ctrl+C as backup
        Register-EngineEvent -SourceId PowerShell.Exiting -Action { Stop-CTFPlatform } | Out-Null

        # Keep the script running and monitor processes
        try {
            while ($true) {
                # Check if processes are still running
                if ($script:backendProcess.HasExited) {
                    Write-Host "❌ Backend server stopped unexpectedly" -ForegroundColor Red
                    break
                }
                
                if ($script:frontendProcess.HasExited) {
                    Write-Host "❌ Frontend server stopped unexpectedly" -ForegroundColor Red
                    break
                }
                
                # Check if the actual services are still responding
                if (-not (Test-Port -Port 5000)) {
                    Write-Host "❌ Backend service is not responding on port 5000" -ForegroundColor Red
                    break
                }
                
                if (-not (Test-Port -Port 3000)) {
                    Write-Host "❌ Frontend service is not responding on port 3000" -ForegroundColor Red
                    break
                }
                
                # Check for key press (non-blocking)
                if ([Console]::KeyAvailable) {
                    $key = [Console]::ReadKey($true)
                    Write-Host ""
                    Write-Host "Key pressed: $($key.KeyChar)" -ForegroundColor Cyan
                    Stop-CTFPlatform
                    break
                }
                
                Start-Sleep -Milliseconds 100
            }
        }
        catch {
            # Ctrl+C was pressed, cleanup will be handled by the signal handler
            Stop-CTFPlatform
        }
        finally {
            # Clean up the cleanup script
            if (Test-Path $cleanupScriptPath) {
                Remove-Item $cleanupScriptPath -Force -ErrorAction SilentlyContinue
            }
        }
    } else {
        Write-Host "❌ Failed to start frontend server" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to start backend server" -ForegroundColor Red
}

# Cleanup is handled by the signal handler
Stop-AllProcesses
