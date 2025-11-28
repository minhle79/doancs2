# ComputerStore Maintenance Script
# Script quản lý và bảo trì dự án Django

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('clean', 'migrate', 'run', 'shell', 'createsuperuser', 'loaddata', 'collectstatic', 'help')]
    [string]$Action = 'help'
)

$ProjectRoot = $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

function Show-Help {
    Write-Host "`n=== ComputerStore Maintenance Script ===" -ForegroundColor Cyan
    Write-Host "`nUsage: .\maintenance.ps1 -Action <action>`n"
    Write-Host "Available actions:" -ForegroundColor Yellow
    Write-Host "  clean           - Xóa cache và __pycache__"
    Write-Host "  migrate         - Chạy migrations"
    Write-Host "  run             - Chạy development server"
    Write-Host "  shell           - Mở Django shell"
    Write-Host "  createsuperuser - Tạo tài khoản admin"
    Write-Host "  loaddata        - Nạp dữ liệu mẫu"
    Write-Host "  collectstatic   - Thu thập static files"
    Write-Host "  help            - Hiển thị help này`n"
}

function Activate-Venv {
    if (Test-Path $ActivateScript) {
        Write-Host "Activating virtual environment..." -ForegroundColor Green
        & $ActivateScript
    } else {
        Write-Host "Virtual environment not found at $VenvPath" -ForegroundColor Red
        Write-Host "Please create one with: python -m venv .venv" -ForegroundColor Yellow
        exit 1
    }
}

function Clean-Project {
    Write-Host "`nCleaning project..." -ForegroundColor Cyan
    
    # Xóa __pycache__
    Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter "__pycache__" | 
        Where-Object { $_.FullName -notlike "*\.venv\*" } |
        ForEach-Object {
            Write-Host "Deleting: $($_.FullName)" -ForegroundColor Yellow
            Remove-Item -Path $_.FullName -Recurse -Force
        }
    
    # Xóa .pyc files
    Get-ChildItem -Path $ProjectRoot -Recurse -File -Filter "*.pyc" |
        Where-Object { $_.FullName -notlike "*\.venv\*" } |
        ForEach-Object {
            Write-Host "Deleting: $($_.FullName)" -ForegroundColor Yellow
            Remove-Item -Path $_.FullName -Force
        }
    
    Write-Host "`n✅ Project cleaned successfully!" -ForegroundColor Green
}

function Run-Migrations {
    Activate-Venv
    Write-Host "`nRunning makemigrations..." -ForegroundColor Cyan
    python manage.py makemigrations
    
    Write-Host "`nRunning migrate..." -ForegroundColor Cyan
    python manage.py migrate
    
    Write-Host "`n✅ Migrations completed!" -ForegroundColor Green
}

function Run-Server {
    Activate-Venv
    Write-Host "`nStarting development server..." -ForegroundColor Cyan
    Write-Host "Server will be available at http://127.0.0.1:8000/" -ForegroundColor Yellow
    Write-Host "Admin panel at http://127.0.0.1:8000/admin/`n" -ForegroundColor Yellow
    python manage.py runserver
}

function Open-Shell {
    Activate-Venv
    Write-Host "`nOpening Django shell..." -ForegroundColor Cyan
    python manage.py shell
}

function Create-SuperUser {
    Activate-Venv
    Write-Host "`nCreating superuser account..." -ForegroundColor Cyan
    python manage.py createsuperuser
}

function Load-SampleData {
    Activate-Venv
    Write-Host "`nLoading sample data..." -ForegroundColor Cyan
    python manage.py loaddata store/fixtures/sample_data.json
    Write-Host "`n✅ Sample data loaded!" -ForegroundColor Green
}

function Collect-StaticFiles {
    Activate-Venv
    Write-Host "`nCollecting static files..." -ForegroundColor Cyan
    python manage.py collectstatic --noinput
    Write-Host "`n✅ Static files collected!" -ForegroundColor Green
}

# Main logic
switch ($Action) {
    'clean' { Clean-Project }
    'migrate' { Run-Migrations }
    'run' { Run-Server }
    'shell' { Open-Shell }
    'createsuperuser' { Create-SuperUser }
    'loaddata' { Load-SampleData }
    'collectstatic' { Collect-StaticFiles }
    'help' { Show-Help }
    default { Show-Help }
}
