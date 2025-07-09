# VBench 核心评测服务功能总结

## 📋 精简后的4个核心维度

| 维度名称 | 中文名称 | 版本 | 功能描述 |
|----------|----------|------|----------|
| `aesthetic_quality` | 美学质量 | VBench 1.0 | 评估视频的美观度和艺术价值 |
| `dynamic_degree` | 动态程度 | VBench 1.0 | 测量视频中的动态变化程度 |
| `camera_motion` | 运镜 | VBench 2.0 | 识别和评估摄像机运动类型 |
| `human_identity` | 人物身份一致性 | VBench 2.0 | 评估视频中人物身份的时序一致性 |

## 🚀 快速使用

### 1. 启动服务
```bash
# Linux/Mac
./start_multi_service.sh

# Windows PowerShell  
.\start_multi_service.ps1
```

### 2. 初始化所有核心维度
```bash
python3 multi_dimension_client.py --action init \
  --dimensions aesthetic_quality dynamic_degree camera_motion human_identity
```

### 3. 评测示例
```bash
# 单维度评测
python3 multi_dimension_client.py --action single \
  --video_path video.mp4 --dimensions aesthetic_quality

# 多维度评测
python3 multi_dimension_client.py --action evaluate \
  --video_paths video1.mp4 video2.mp4 \
  --dimensions aesthetic_quality dynamic_degree camera_motion human_identity
```

## 📊 核心维度组合推荐

### 基础质量评估
```bash
--dimensions aesthetic_quality dynamic_degree
```

### 人物视频评估
```bash
--dimensions aesthetic_quality human_identity
```

### 电影级评估
```bash
--dimensions aesthetic_quality camera_motion
```

### 全面评估
```bash
--dimensions aesthetic_quality dynamic_degree camera_motion human_identity
```

## 📝 主要改动

1. **维度精简**: 从28+个维度精简到4个核心维度
2. **代码优化**: 移除了不必要的维度配置代码
3. **依赖精简**: 创建了 `requirements_core.txt` 精简依赖文件
4. **文档更新**: 提供了核心版本的使用文档 `README_core.md`
5. **默认配置**: 更新了所有默认维度配置为4个核心维度

## 🎯 性能优化

- **内存使用**: 大幅减少GPU内存占用
- **启动速度**: 更快的服务启动时间
- **部署简化**: 更少的依赖包和模型文件
- **维护成本**: 降低系统复杂度和维护难度

## 📁 关键文件

- `multi_dimension_service.py` - 精简的主服务文件
- `requirements_core.txt` - 核心依赖包
- `README_core.md` - 核心版本使用说明
- `start_multi_service.sh/.ps1` - 更新的启动脚本 