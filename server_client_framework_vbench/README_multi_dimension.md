# VBench 多维度评测服务

基于 VBench 全套评测功能的 Flask HTTP 服务框架，支持美学质量、人物身份一致性、运镜等 28+ 个评测维度，提供统一的 API 接口供 AI 工程师远程调用。

## 🎯 功能特性

- 🎬 **多维度评测**: 支持 VBench 1.0 和 2.0 的全部评测维度
- 📊 **统一接口**: 一套 API 调用所有评测功能
- 🔄 **批量处理**: 支持多个视频同时进行多维度评测
- 🌐 **HTTP服务**: 简单的 REST API，易于集成到现有系统
- 🚀 **GPU加速**: 支持 CUDA 加速，提升评测速度
- 📋 **详细日志**: 完整的评测过程日志记录
- 🛠️ **灵活配置**: 按需初始化评测维度，节省资源

## 📋 支持的评测维度

### VBench 1.0 (16个维度)

| 维度 | 描述 | 应用场景 |
|------|------|----------|
| `aesthetic_quality` | 美学质量 | 视频美观度评估 |
| `subject_consistency` | 主体一致性 | 主体对象时序一致性 |
| `background_consistency` | 背景一致性 | 背景场景时序一致性 |
| `temporal_flickering` | 时序闪烁 | 视频闪烁问题检测 |
| `motion_smoothness` | 运动平滑性 | 运动轨迹平滑度 |
| `dynamic_degree` | 动态程度 | 视频动态变化程度 |
| `imaging_quality` | 成像质量 | 视频清晰度和质量 |
| `object_class` | 对象类别 | 对象识别准确性 |
| `multiple_objects` | 多对象 | 多对象场景处理 |
| `human_action` | 人类动作 | 人物动作识别 |
| `color` | 颜色 | 色彩表现质量 |
| `spatial_relationship` | 空间关系 | 对象空间位置关系 |
| `scene` | 场景 | 场景识别和一致性 |
| `appearance_style` | 外观风格 | 视觉风格一致性 |
| `temporal_style` | 时序风格 | 时序风格一致性 |
| `overall_consistency` | 整体一致性 | 整体视觉一致性 |

### VBench 2.0 (12个维度)

| 维度 | 描述 | 应用场景 |
|------|------|----------|
| `camera_motion` | 运镜 | 摄像机运动分析 |
| `human_identity` | 人物身份一致性 | 人物身份保持一致 |
| `human_clothes` | 人物服装 | 服装细节一致性 |
| `human_anatomy` | 人体解剖 | 人体结构合理性 |
| `human_interaction` | 人物交互 | 人物间交互行为 |
| `composition` | 构图 | 画面构图质量 |
| `diversity` | 多样性 | 内容多样性评估 |
| `dynamic_attribute` | 动态属性 | 对象动态属性变化 |
| `dynamic_spatial_relationship` | 动态空间关系 | 动态空间位置关系 |
| `instance_preservation` | 实例保存 | 实例对象保持性 |
| `motion_rationality` | 运动合理性 | 运动逻辑合理性 |
| `motion_order_understanding` | 运动顺序理解 | 运动序列理解 |

### VBench 2.0 高级维度 (4个维度)

| 维度 | 描述 | 应用场景 |
|------|------|----------|
| `complex_landscape` | 复杂风景 | 复杂场景理解 |
| `complex_plot` | 复杂情节 | 复杂剧情理解 |
| `multi_view_consistency` | 多视角一致性 | 多视角场景一致性 |
| `material` | 材质 | 材质表现质量 |
| `mechanics` | 力学 | 物理力学合理性 |
| `thermotics` | 热力学 | 热力学现象合理性 |

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境（推荐）
python3 -m venv vbench_env
source vbench_env/bin/activate  # Linux/Mac
# 或 vbench_env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements_service.txt
```

### 2. 启动服务

```bash
# Linux/Mac
chmod +x start_multi_service.sh
./start_multi_service.sh

# Windows PowerShell
.\start_multi_service.ps1

# 或直接运行
python3 multi_dimension_service.py

# 自定义配置
./start_multi_service.sh --port 8080 --device cuda:1
```

### 3. 查看支持的维度

```bash
# 使用客户端工具
python3 multi_dimension_client.py --action dimensions

# 或使用 curl
curl http://localhost:5001/dimensions
```

### 4. 初始化评测维度

```bash
# 初始化单个维度
python3 multi_dimension_client.py --action init --dimensions aesthetic_quality

# 初始化多个维度
python3 multi_dimension_client.py --action init \
  --dimensions aesthetic_quality camera_motion human_identity

# 或使用 curl
curl -X POST http://localhost:5001/initialize \
  -H "Content-Type: application/json" \
  -d '{"dimensions": ["aesthetic_quality", "camera_motion"], "device": "cuda:0"}'
```

### 5. 进行评测

```bash
# 单维度评测
python3 multi_dimension_client.py --action single \
  --video_path /path/to/video.mp4 \
  --dimensions aesthetic_quality

# 多维度评测
python3 multi_dimension_client.py --action evaluate \
  --video_paths /path/to/video1.mp4 /path/to/video2.mp4 \
  --dimensions aesthetic_quality camera_motion human_identity
```

## 📡 API 文档

### 健康检查

**GET** `/health`

检查服务运行状态和已初始化的维度。

**响应示例:**
```json
{
  "status": "healthy",
  "service": "VBench Multi-Dimension Evaluation",
  "initialized_dimensions": ["camera_motion", "aesthetic_quality"],
  "supported_dimensions": ["aesthetic_quality", "camera_motion", "..."]
}
```

### 获取支持的维度

**GET** `/dimensions`

获取所有支持的评测维度信息。

**响应示例:**
```json
{
  "status": "success",
  "supported_dimensions": {
    "aesthetic_quality": {
      "description": "美学质量评测",
      "version": "1.0",
      "initialized": true
    },
    "camera_motion": {
      "description": "运镜评测", 
      "version": "2.0",
      "initialized": false
    }
    // ...
  },
  "total_count": 28,
  "initialized_count": 1
}
```

### 初始化评测维度

**POST** `/initialize`

初始化一个或多个评测维度。

**请求参数:**
```json
{
  "dimensions": ["aesthetic_quality", "camera_motion"],
  "device": "cuda:0",
  "local_mode": false
}
```

**响应示例:**
```json
{
  "status": "success",
  "device": "cuda:0",
  "initialized_dimensions": ["aesthetic_quality", "camera_motion"],
  "failed_dimensions": [],
  "total_initialized": 2
}
```

### 多维度评测

**POST** `/evaluate`

对多个视频进行多维度评测。

**请求参数:**
```json
{
  "video_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
  "dimensions": ["aesthetic_quality", "camera_motion", "human_identity"],
  "json_dir": "/path/to/config"  // 可选
}
```

**响应示例:**
```json
{
  "status": "success",
  "final_score": 0.8532,
  "dimension_scores": {
    "aesthetic_quality": 0.8234,
    "camera_motion": 0.9123,
    "human_identity": 0.8240
  },
  "detailed_results": {
    "aesthetic_quality": {
      "overall_score": 0.8234,
      "video_results": [
        {"video_path": "/path/to/video1.mp4", "video_results": 0.8456},
        {"video_path": "/path/to/video2.mp4", "video_results": 0.8012}
      ],
      "description": "美学质量评测"
    }
    // ...
  },
  "video_count": 2,
  "evaluated_dimensions": ["aesthetic_quality", "camera_motion", "human_identity"]
}
```

### 单维度评测

**POST** `/evaluate_single`

对单个视频进行单维度评测。

**请求参数:**
```json
{
  "video_path": "/path/to/video.mp4",
  "dimension": "aesthetic_quality",
  "json_dir": "/path/to/config"  // 可选
}
```

**响应示例:**
```json
{
  "status": "success",
  "dimension": "aesthetic_quality",
  "description": "美学质量评测",
  "video_path": "/path/to/video.mp4",
  "score": 0.8456,
  "detailed_results": {
    "video_path": "/path/to/video.mp4",
    "video_results": 0.8456
  }
}
```

## 💻 客户端使用示例

### 命令行客户端

```bash
# 健康检查
python3 multi_dimension_client.py --action health

# 查看支持的维度
python3 multi_dimension_client.py --action dimensions

# 初始化多个维度
python3 multi_dimension_client.py --action init \
  --dimensions aesthetic_quality camera_motion human_identity \
  --device cuda:0

# 多维度评测
python3 multi_dimension_client.py --action evaluate \
  --video_paths video1.mp4 video2.mp4 video3.mp4 \
  --dimensions aesthetic_quality camera_motion

# 单维度评测
python3 multi_dimension_client.py --action single \
  --video_path video.mp4 \
  --dimensions aesthetic_quality

# 连接远程服务
python3 multi_dimension_client.py --url http://192.168.1.100:5001 \
  --action dimensions
```

### Python 代码示例

```python
import requests

# 连接服务
base_url = "http://localhost:5001"

# 1. 查看支持的维度
response = requests.get(f"{base_url}/dimensions")
dimensions = response.json()
print(f"支持 {dimensions['total_count']} 个评测维度")

# 2. 初始化评测维度
response = requests.post(f"{base_url}/initialize", json={
    "dimensions": ["aesthetic_quality", "camera_motion", "human_identity"],
    "device": "cuda:0"
})
init_result = response.json()
print(f"初始化成功: {init_result['initialized_dimensions']}")

# 3. 多维度评测
response = requests.post(f"{base_url}/evaluate", json={
    "video_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
    "dimensions": ["aesthetic_quality", "camera_motion"]
})
eval_result = response.json()
print(f"最终评分: {eval_result['final_score']}")
print(f"各维度评分: {eval_result['dimension_scores']}")

# 4. 单维度评测
response = requests.post(f"{base_url}/evaluate_single", json={
    "video_path": "/path/to/video.mp4",
    "dimension": "aesthetic_quality"
})
single_result = response.json()
print(f"美学质量评分: {single_result['score']}")
```

## 🧪 测试服务

```bash
# 运行基础测试
python3 test_multi_dimension.py --basic

# 运行完整测试
python3 test_multi_dimension.py

# 测试特定维度
python3 test_multi_dimension.py --dimensions aesthetic_quality camera_motion

# 测试远程服务
python3 test_multi_dimension.py --url http://192.168.1.100:5001
```

## 🔧 高级配置

### 环境变量配置

```bash
export HOST=0.0.0.0
export PORT=5001
export DEFAULT_DEVICE=cuda:0
export FLASK_ENV=production
export LOCAL_MODE=true  # 本地模式，跳过模型下载
```

### 生产环境部署

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn -w 1 -b 0.0.0.0:5001 multi_dimension_service:app

# 使用 Docker
docker build -t vbench-multi-service .
docker run -p 5001:5001 --gpus all vbench-multi-service

# 使用 Nginx 反向代理
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 1800s;  # 支持长时间评测
    }
}
```

## 📊 性能优化建议

1. **按需初始化**: 只初始化需要的评测维度，避免资源浪费
2. **批量评测**: 多个视频一起评测比单独评测更高效
3. **GPU 内存管理**: 根据GPU显存选择合适的维度组合
4. **并发限制**: 建议单实例运行，避免GPU内存冲突
5. **缓存策略**: 对于重复评测的视频可以实现结果缓存

## 🚨 故障排除

### 常见问题

1. **CUDA 内存不足**
   ```bash
   # 减少同时初始化的维度数量
   python3 multi_dimension_client.py --action init --dimensions aesthetic_quality
   # 或使用 CPU 模式
   ./start_multi_service.sh --device cpu
   ```

2. **某些维度初始化失败**
   ```bash
   # 查看详细错误信息
   python3 multi_dimension_client.py --action init --dimensions problematic_dimension
   # 尝试本地模式
   ./start_multi_service.sh --local
   ```

3. **评测超时**
   ```bash
   # 增加客户端超时时间或分批评测
   # 检查视频文件大小和格式
   ```

### 维度兼容性

| 维度类型 | GPU 内存需求 | 推荐组合 |
|----------|--------------|----------|
| 轻量级 | < 2GB | aesthetic_quality, color, scene |
| 中等 | 2-4GB | camera_motion, human_action, temporal_flickering |
| 重量级 | > 4GB | human_identity, composition, complex_* |

## 📈 使用场景

### 1. 视频生成模型评估
```python
# 评估生成视频的综合质量
dimensions = [
    "aesthetic_quality",      # 美学质量
    "temporal_flickering",    # 时序稳定性
    "motion_smoothness",      # 运动平滑性
    "subject_consistency"     # 主体一致性
]
```

### 2. 人物视频专项评估
```python
# 专注于人物相关的评测维度
dimensions = [
    "human_identity",         # 人物身份一致性
    "human_clothes",          # 服装一致性
    "human_anatomy",          # 人体结构
    "human_action",           # 人物动作
    "human_interaction"       # 人物交互
]
```

### 3. 电影级质量评估
```python
# 电影级制作质量评估
dimensions = [
    "camera_motion",          # 运镜技巧
    "composition",            # 构图质量
    "aesthetic_quality",      # 美学质量
    "complex_plot",           # 复杂情节
    "motion_rationality"      # 运动合理性
]
```

## 📝 更新日志

- **v1.0.0**: 基础 camera_motion 服务
- **v2.0.0**: 新增多维度支持，支持 VBench 1.0 和 2.0 全部维度
- **v2.1.0**: 优化性能，支持批量评测和按需初始化

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目基于 VBench 项目，请遵循相应的开源许可证。

## 📞 技术支持

如有技术问题或建议，请联系 AI 工程团队。 