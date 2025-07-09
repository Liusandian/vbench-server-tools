# VBench 多维度评测服务启动脚本 (PowerShell版本)

param(
    [string]$ServerHost = "0.0.0.0",
    [string]$Port = "5001", 
    [string]$Device = "cuda:0",
    [string]$Environment = "development",
    [switch]$Local,
    [switch]$Help
)

# 颜色定义
$Red = "Red"
$Green = "Green" 
$Yellow = "Yellow"
$Blue = "Blue"

Write-Host "========================================"  -ForegroundColor $Blue
Write-Host " VBench 多维度评测服务启动器"  -ForegroundColor $Blue
Write-Host "========================================"  -ForegroundColor $Blue

if ($Help) {
    Write-Host "使用方法: .\start_multi_service.ps1 [选项]"
    Write-Host ""
    Write-Host "选项:"
    Write-Host "  -ServerHost HOST    服务器地址 (默认: 0.0.0.0)"
    Write-Host "  -Port PORT          服务器端口 (默认: 5001)"
    Write-Host "  -Device DEVICE      GPU设备 (默认: cuda:0)"
    Write-Host "  -Environment ENV    环境配置 (development/production, 默认: development)"
    Write-Host "  -Local              本地模式，跳过模型下载"
    Write-Host "  -Help               显示帮助信息"
    Write-Host ""
    Write-Host "支持的评测维度:"
    Write-Host "  VBench 1.0 核心维度:"
    Write-Host "    • aesthetic_quality        - 美学质量"
    Write-Host "    • dynamic_degree           - 动态程度"
    Write-Host ""
    Write-Host "  VBench 2.0 核心维度:"
    Write-Host "    • camera_motion            - 运镜"
    Write-Host "    • human_identity           - 人物身份一致性"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\start_multi_service.ps1                          # 使用默认配置启动"
    Write-Host "  .\start_multi_service.ps1 -Port 8080 -Device cuda:1  # 指定端口和GPU设备"
    Write-Host "  .\start_multi_service.ps1 -Environment production -Local  # 生产环境本地模式"
    exit 0
}

$LocalMode = if ($Local) { "true" } else { "false" }

Write-Host "配置信息:" -ForegroundColor $Green
Write-Host "  服务器地址: $ServerHost`:$Port" -ForegroundColor $Yellow
Write-Host "  GPU设备: $Device" -ForegroundColor $Yellow
Write-Host "  环境: $Environment" -ForegroundColor $Yellow
Write-Host "  本地模式: $LocalMode" -ForegroundColor $Yellow
Write-Host ""

# 检查 Python 环境
Write-Host "检查 Python 环境..." -ForegroundColor $Blue
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 版本: $pythonVersion" -ForegroundColor $Green
} catch {
    Write-Host "错误: 未找到 python" -ForegroundColor $Red
    exit 1
}

# 检查虚拟环境
if ($env:VIRTUAL_ENV) {
    Write-Host "虚拟环境: $env:VIRTUAL_ENV" -ForegroundColor $Green
} else {
    Write-Host "警告: 未检测到虚拟环境，建议使用虚拟环境" -ForegroundColor $Yellow
}

# 检查 CUDA
if ($Device -like "cuda*") {
    Write-Host "检查 CUDA 环境..." -ForegroundColor $Blue
    try {
        $nvidiaInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>$null | Select-Object -First 1
        if ($nvidiaInfo) {
            Write-Host "CUDA GPU: $nvidiaInfo" -ForegroundColor $Green
            Write-Host "CUDA 环境可用" -ForegroundColor $Green
        } else {
            Write-Host "警告: 未检测到 CUDA 环境，将回退到 CPU" -ForegroundColor $Yellow
            $Device = "cpu"
        }
    } catch {
        Write-Host "警告: 未检测到 CUDA 环境，将回退到 CPU" -ForegroundColor $Yellow
        $Device = "cpu"
    }
}

# 检查依赖
Write-Host "检查依赖包..." -ForegroundColor $Blue
if (Test-Path "requirements_service.txt") {
    Write-Host "发现依赖文件: requirements_service.txt" -ForegroundColor $Green
    Write-Host "如需安装依赖，请运行: pip install -r requirements_service.txt" -ForegroundColor $Yellow
} else {
    Write-Host "警告: 未找到 requirements_service.txt" -ForegroundColor $Yellow
}

# 检查服务文件
if (!(Test-Path "multi_dimension_service.py")) {
    Write-Host "错误: 未找到服务文件 multi_dimension_service.py" -ForegroundColor $Red
    exit 1
}

# 设置环境变量
$env:HOST = $ServerHost
$env:PORT = $Port
$env:DEFAULT_DEVICE = $Device
$env:FLASK_ENV = $Environment

if ($Local) {
    $env:LOCAL_MODE = "true"
}

# 创建必要的目录
New-Item -ItemType Directory -Force -Path "uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host ""
Write-Host "启动多维度评测服务..." -ForegroundColor $Green
Write-Host "访问地址: http://$ServerHost`:$Port" -ForegroundColor $Blue
Write-Host "健康检查: http://$ServerHost`:$Port/health" -ForegroundColor $Blue
Write-Host "支持的维度: http://$ServerHost`:$Port/dimensions" -ForegroundColor $Blue
Write-Host ""
Write-Host "使用客户端工具:" -ForegroundColor $Yellow
Write-Host "  python multi_dimension_client.py --action dimensions" -ForegroundColor $Yellow
Write-Host "  python multi_dimension_client.py --action init --dimensions aesthetic_quality dynamic_degree camera_motion human_identity" -ForegroundColor $Yellow
Write-Host "  python multi_dimension_client.py --action evaluate --video_paths video.mp4 --dimensions aesthetic_quality camera_motion" -ForegroundColor $Yellow
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor $Yellow
Write-Host ""

# 启动服务
try {
    python multi_dimension_service.py
} catch {
    Write-Host "服务启动失败: $($_.Exception.Message)" -ForegroundColor $Red
    exit 1
} 