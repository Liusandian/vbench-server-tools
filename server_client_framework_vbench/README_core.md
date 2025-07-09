# VBench 核心评测服务 (精简版)

基于 VBench 核心评测功能的 Flask HTTP 服务框架，支持4个核心评测维度，提供统一的 API 接口供 AI 工程师远程调用。

## 🎯 功能特性

- 🎬 **4个核心维度**: 精选最重要的评测维度
- 📊 **统一接口**: 一套 API 调用所有评测功能
- 🔄 **批量处理**: 支持多个视频同时进行多维度评测
- 🌐 **HTTP服务**: 简单的 REST API，易于集成到现有系统
- 🚀 **GPU加速**: 支持 CUDA 加速，提升评测速度
- 📋 **精简依赖**: 只包含必要的依赖包，减少部署复杂度

## 📋 支持的评测维度 (4个核心维度)

| 维度 | 版本 | 描述 | 应用场景 |
|------|------|------|----------|
| `aesthetic_quality` | 1.0 | 美学质量 | 视频美观度评估 |
| `dynamic_degree` | 1.0 | 动态程度 | 视频动态变化程度 |
| `camera_motion` | 2.0 | 运镜 | 摄像机运动分析 |
| `human_identity` | 2.0 | 人物身份一致性 | 人物身份保持一致 |

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境（推荐）
python3 -m venv vbench_core_env
source vbench_core_env/bin/activate  # Linux/Mac
# 或 vbench_core_env\Scripts\activate  # Windows

# 安装精简依赖
pip install -r requirements_core.txt
```

### 2. 启动服务

```bash
# Linux/Mac
./start_multi_service.sh

# Windows PowerShell
.\start_multi_service.ps1

# 或直接运行
python3 multi_dimension_service.py
```

### 3. 查看支持的维度

```bash
# 使用客户端工具
python3 multi_dimension_client.py --action dimensions

# 或使用 curl
curl http://localhost:5001/dimensions
```

### 4. 初始化所有核心维度

```bash
# 初始化全部4个核心维度
python3 multi_dimension_client.py --action init \
  --dimensions aesthetic_quality dynamic_degree camera_motion human_identity

# 或初始化部分维度
python3 multi_dimension_client.py --action init \
  --dimensions aesthetic_quality camera_motion
```

### 5. 进行评测

```bash
# 多维度评测
python3 multi_dimension_client.py --action evaluate \
  --video_paths video1.mp4 video2.mp4 \
  --dimensions aesthetic_quality dynamic_degree camera_motion human_identity

# 单维度评测
python3 multi_dimension_client.py --action single \
  --video_path video.mp4 \
  --dimensions aesthetic_quality
```

## 📡 API 接口示例

### Python 代码示例

```python
import requests

# 连接服务
base_url = "http://localhost:5001"

# 1. 查看支持的维度
response = requests.get(f"{base_url}/dimensions")
dimensions = response.json()
print(f"支持 {dimensions['total_count']} 个评测维度")

# 2. 初始化所有核心维度
response = requests.post(f"{base_url}/initialize", json={
    "dimensions": ["aesthetic_quality", "dynamic_degree", "camera_motion", "human_identity"],
    "device": "cuda:0"
})
init_result = response.json()
print(f"初始化成功: {init_result['initialized_dimensions']}")

# 3. 核心维度评测
response = requests.post(f"{base_url}/evaluate", json={
    "video_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
    "dimensions": ["aesthetic_quality", "dynamic_degree", "camera_motion", "human_identity"]
})
eval_result = response.json()
print(f"最终评分: {eval_result['final_score']}")
print(f"美学质量: {eval_result['dimension_scores']['aesthetic_quality']}")
print(f"动态程度: {eval_result['dimension_scores']['dynamic_degree']}")
print(f"运镜质量: {eval_result['dimension_scores']['camera_motion']}")
print(f"人物身份一致性: {eval_result['dimension_scores']['human_identity']}")
```

## 🧪 测试服务

```bash
# 运行基础测试
python3 test_multi_dimension.py --basic

# 运行完整测试 (测试所有4个核心维度)
python3 test_multi_dimension.py

# 测试特定维度
python3 test_multi_dimension.py --dimensions aesthetic_quality camera_motion
```

## 🎯 核心维度详解

### 1. aesthetic_quality (美学质量)
- **功能**: 评估视频的美观度和艺术价值
- **技术**: 基于 LAION Aesthetic Predictor
- **评分范围**: 0.0 - 1.0
- **应用**: 视频生成模型的美学质量评估

### 2. dynamic_degree (动态程度)
- **功能**: 测量视频中的动态变化程度
- **技术**: 基于 DINO 特征的时序变化分析
- **评分范围**: 0.0 - 1.0
- **应用**: 静态/动态视频内容区分

### 3. camera_motion (运镜)
- **功能**: 识别和评估摄像机运动类型
- **技术**: 基于光流分析的运镜检测
- **支持类型**: pan_left/right, tilt_up/down, zoom_in/out, static, 等
- **应用**: 电影级视频制作质量评估

### 4. human_identity (人物身份一致性)
- **功能**: 评估视频中人物身份的时序一致性
- **技术**: 基于人脸识别和特征匹配
- **评分范围**: 0.0 - 1.0 (-1表示无效)
- **应用**: 人物视频生成质量检测

## 📈 使用场景

### 1. 视频生成模型综合评估
```python
# 评估生成视频的核心质量
dimensions = ["aesthetic_quality", "dynamic_degree", "camera_motion", "human_identity"]
```

### 2. 人物视频专项评估
```python
# 专注于人物相关的评测
dimensions = ["aesthetic_quality", "human_identity"]
```

### 3. 电影级制作质量评估
```python
# 评估专业视频制作质量
dimensions = ["aesthetic_quality", "camera_motion"]
```

### 4. 动态内容分析
```python
# 分析视频动态特征
dimensions = ["dynamic_degree", "camera_motion"]
```

## 📊 性能特点

| 维度 | GPU 内存需求 | 处理速度 | 复杂度 |
|------|--------------|----------|--------|
| aesthetic_quality | 低 (~1GB) | 快 | 简单 |
| dynamic_degree | 中 (~2GB) | 中等 | 中等 |
| camera_motion | 中 (~2GB) | 中等 | 中等 |
| human_identity | 高 (~3GB) | 慢 | 复杂 |

## 🚨 故障排除

### 常见问题

1. **CUDA 内存不足**
   ```bash
   # 减少同时初始化的维度数量
   python3 multi_dimension_client.py --action init --dimensions aesthetic_quality
   # 或使用 CPU 模式
   ./start_multi_service.sh --device cpu
   ```

2. **human_identity 初始化失败**
   ```bash
   # 确保安装了人脸检测依赖
   pip install retinaface-pytorch
   # 检查模型文件是否正确下载
   ```

3. **评测超时**
   ```bash
   # 建议单独测试每个维度
   python3 multi_dimension_client.py --action single --video_path video.mp4 --dimensions aesthetic_quality
   ```

## 📝 更新日志

- **v2.0.0**: 精简版发布，支持4个核心评测维度
- **v2.1.0**: 优化性能，改进错误处理

## 🤝 扩展说明

如果需要更多评测维度，可以参考完整版的 `multi_dimension_service.py` 和 `README_multi_dimension.md`。

## 📞 技术支持

如有技术问题或建议，请联系 AI 工程团队。 