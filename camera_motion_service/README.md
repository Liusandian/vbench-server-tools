# Camera Motion Evaluation Service

基于Flask的Camera Motion维度评测服务，将VBench-2.0的Camera Motion评测功能封装为HTTP API服务。

## 功能特性

- 🎥 支持多种视频格式 (mp4, avi, mov, mkv, webm)
- 🔄 单个视频评估和批量评估
- 📊 详细的评估结果输出
- 💾 结果自动保存到output文件夹
- 🌐 RESTful API接口
- 📝 完整的日志记录

## 文件结构

```
camera_motion_service/
├── server.py          # Flask服务端
├── client.py          # 客户端工具
├── requirements.txt   # Python依赖
├── README.md         # 使用说明
├── input/            # 视频输入文件夹
├── output/           # 评估结果输出文件夹
└── logs/             # 日志文件夹
```

## 安装和配置

### 1. 安装依赖

```bash
cd camera_motion_service
pip install -r requirements.txt
```

### 2. 确保VBench-2.0环境

确保VBench-2.0项目在上级目录中，并且相关依赖已安装。

## 使用方法

### 启动服务端

```bash
python server.py
```

服务器将在 `http://127.0.0.1:5000` 启动。

### 客户端使用

#### 1. 健康检查

```bash
python client.py --health
```

#### 2. 单个视频评估

```bash
# 基本评估
python client.py --video path/to/video.mp4

# 指定期望的运动类型
python client.py --video path/to/video.mp4 --motion-type zoom_in
```

#### 3. 批量评估

将要评估的视频文件放入 `input/` 文件夹，然后运行：

```bash
python client.py --batch
```

#### 4. 获取历史结果

```bash
# 通过任务ID获取结果
python client.py --get-result <task_id>

# 下载结果文件
python client.py --download <task_id>
```

## API接口文档

### 基础接口

- `GET /` - 服务信息
- `GET /health` - 健康检查

### 评估接口

- `POST /evaluate` - 单个视频评估
- `POST /batch_evaluate` - 批量评估
- `GET /results/<task_id>` - 获取评估结果
- `GET /results/<task_id>/download` - 下载结果文件

### 单个视频评估API

**请求:**
```bash
curl -X POST http://127.0.0.1:5000/evaluate \
  -F "video=@video.mp4" \
  -F "motion_type=zoom_in"
```

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "video_path": "input/550e8400-e29b-41d4-a716-446655440000.mp4",
    "predicted_motions": ["zoom_in", "tilt_up"],
    "expected_motion": "zoom_in",
    "score": 1.0,
    "frame_count": 120,
    "fps": 30,
    "resolution": "1920x1080",
    "timestamp": "2025-01-15T23:12:00.000000"
  }
}
```

## 支持的运动类型

- `zoom_in` - 放大
- `zoom_out` - 缩小
- `pan_left` - 向左平移
- `pan_right` - 向右平移
- `tilt_up` - 向上倾斜
- `tilt_down` - 向下倾斜
- `static` - 静态
- `orbits` - 环绕
- `oblique` - 斜向运动

## 评估结果

每个评估结果包含以下信息：

- **predicted_motions**: 预测的运动类型列表
- **expected_motion**: 期望的运动类型（可选）
- **score**: 评分（0.0-1.0）
- **frame_count**: 视频帧数
- **fps**: 视频帧率
- **resolution**: 视频分辨率
- **timestamp**: 评估时间戳

## 日志和调试

### 查看服务器日志

```bash
tail -f logs/server.log
```

### 常见问题

1. **CUDA内存不足**: 减少视频分辨率或使用CPU模式
2. **模型下载失败**: 检查网络连接，可能需要代理
3. **导入错误**: 确保VBench-2.0路径正确

## 技术架构

- **框架**: Flask + Werkzeug
- **深度学习**: PyTorch + CoTracker
- **视频处理**: OpenCV + Decord
- **API**: RESTful HTTP接口

## 注意事项

1. 首次运行会自动下载CoTracker模型，需要网络连接
2. 建议使用GPU进行评估以提高速度
3. 支持的最大视频文件大小为100MB
4. 评估结果会自动保存到output文件夹

## 扩展功能

可以根据需要扩展以下功能：

- 添加更多评估维度
- 支持视频流处理
- 添加Web界面
- 集成更多AI模型 