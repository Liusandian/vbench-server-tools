#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Motion Evaluation Server
基于Flask的Camera Motion维度评测服务
"""

import os
import sys
import json
import uuid
import logging
import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify, send_file
import cv2
import torch
import numpy as np
import decord
decord.bridge.set_bridge('torch')

# 添加VBench-2.0路径到sys.path
current_dir = Path(__file__).parent.absolute()
vbench_path = current_dir.parent / "VBench-2.0"
sys.path.insert(0, str(vbench_path))

try:
    from vbench2.camera_motion import CameraPredict
    from vbench2.utils import split_video_into_scenes
except ImportError as e:
    print(f"无法导入VBench2模块: {e}")
    print("请确保VBench-2.0路径正确并且依赖已安装")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 全局变量
camera_predictor = None
device = None

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_camera_predictor():
    """初始化Camera预测器"""
    global camera_predictor, device
    
    try:
        # 检查CUDA可用性
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"使用设备: {device}")
        
        # 配置子模块
        submodules_dict = {
            "repo": "facebookresearch/co-tracker",
            "model": "cotracker2"
        }
        
        # 初始化Camera预测器
        camera_predictor = CameraPredict(device, submodules_dict)
        logger.info("Camera预测器初始化成功")
        
    except Exception as e:
        logger.error(f"初始化Camera预测器失败: {e}")
        raise

def evaluate_single_video(video_path, motion_type=None):
    """
    评估单个视频的Camera Motion
    
    Args:
        video_path: 视频文件路径
        motion_type: 期望的运动类型 (可选)
        
    Returns:
        dict: 评估结果
    """
    try:
        logger.info(f"开始评估视频: {video_path}")
        
        # 场景分割
        end_frame = -1
        scene_list = split_video_into_scenes(video_path, 5.0)
        if len(scene_list) != 0:
            end_frame = int(scene_list[0][1].get_frames())
        
        # 读取视频
        video_reader = decord.VideoReader(video_path)
        video = video_reader.get_batch(range(len(video_reader)))
        frame_count, height, width = video.shape[0], video.shape[1], video.shape[2]
        video = video.permute(0, 3, 1, 2)[None].float()
        
        if device == 'cuda':
            video = video.cuda()
        
        # 获取FPS
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        
        # 预测Camera Motion
        predict_results = camera_predictor.predict(video, fps, end_frame)
        
        # 计算评分
        if motion_type:
            video_score = 1.0 if motion_type in predict_results else 0.0
        else:
            video_score = 1.0  # 如果没有指定期望类型，默认为1.0
        
        result = {
            'video_path': video_path,
            'predicted_motions': predict_results,
            'expected_motion': motion_type,
            'score': video_score,
            'frame_count': frame_count,
            'fps': fps,
            'resolution': f"{width}x{height}",
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        logger.info(f"评估完成: {predict_results}")
        return result
        
    except Exception as e:
        logger.error(f"评估视频失败 {video_path}: {e}")
        raise

@app.route('/', methods=['GET'])
def index():
    """主页"""
    return jsonify({
        'message': 'Camera Motion Evaluation Server',
        'version': '1.0.0',
        'endpoints': {
            '/evaluate': 'POST - 上传视频进行评估',
            '/health': 'GET - 健康检查',
            '/results/<task_id>': 'GET - 获取评估结果'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    global camera_predictor
    status = "healthy" if camera_predictor is not None else "unhealthy"
    return jsonify({
        'status': status,
        'device': str(device),
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/evaluate', methods=['POST'])
def evaluate_video():
    """视频评估API"""
    try:
        # 检查是否有文件上传
        if 'video' not in request.files:
            return jsonify({'error': '没有上传视频文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'不支持的文件格式，支持的格式: {ALLOWED_EXTENSIONS}'}), 400
        
        # 获取可选参数
        motion_type = request.form.get('motion_type')  # 期望的运动类型
        
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{task_id}.{file_extension}"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        
        file.save(video_path)
        logger.info(f"视频已保存: {video_path}")
        
        # 进行评估
        result = evaluate_single_video(video_path, motion_type)
        result['task_id'] = task_id
        result['original_filename'] = filename
        
        # 保存结果到输出文件夹
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{task_id}_result.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 清理输入文件（可选）
        try:
            os.remove(video_path)
        except:
            pass
        
        return jsonify({
            'task_id': task_id,
            'status': 'completed',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"评估过程出错: {e}")
        return jsonify({'error': f'评估失败: {str(e)}'}), 500

@app.route('/results/<task_id>', methods=['GET'])
def get_result(task_id):
    """获取评估结果"""
    try:
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{task_id}_result.json")
        
        if not os.path.exists(result_path):
            return jsonify({'error': '结果不存在'}), 404
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取结果失败: {e}")
        return jsonify({'error': f'获取结果失败: {str(e)}'}), 500

@app.route('/results/<task_id>/download', methods=['GET'])
def download_result(task_id):
    """下载评估结果文件"""
    try:
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{task_id}_result.json")
        
        if not os.path.exists(result_path):
            return jsonify({'error': '结果文件不存在'}), 404
        
        return send_file(result_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"下载结果失败: {e}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/batch_evaluate', methods=['POST'])
def batch_evaluate():
    """批量评估API"""
    try:
        # 获取input文件夹中的所有视频文件
        input_folder = app.config['UPLOAD_FOLDER']
        video_files = []
        
        for filename in os.listdir(input_folder):
            if allowed_file(filename):
                video_files.append(filename)
        
        if not video_files:
            return jsonify({'error': 'input文件夹中没有找到视频文件'}), 400
        
        # 批量处理
        batch_id = str(uuid.uuid4())
        results = []
        
        for filename in video_files:
            video_path = os.path.join(input_folder, filename)
            try:
                result = evaluate_single_video(video_path)
                result['filename'] = filename
                results.append(result)
                logger.info(f"已处理: {filename}")
            except Exception as e:
                logger.error(f"处理文件失败 {filename}: {e}")
                results.append({
                    'filename': filename,
                    'error': str(e),
                    'status': 'failed'
                })
        
        # 保存批量结果
        batch_result = {
            'batch_id': batch_id,
            'total_files': len(video_files),
            'processed_files': len([r for r in results if 'error' not in r]),
            'failed_files': len([r for r in results if 'error' in r]),
            'results': results,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], f"batch_{batch_id}_results.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'batch_id': batch_id,
            'status': 'completed',
            'summary': {
                'total_files': batch_result['total_files'],
                'processed_files': batch_result['processed_files'],
                'failed_files': batch_result['failed_files']
            }
        })
        
    except Exception as e:
        logger.error(f"批量评估失败: {e}")
        return jsonify({'error': f'批量评估失败: {str(e)}'}), 500

if __name__ == '__main__':
    try:
        # 创建必要的文件夹
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 初始化Camera预测器
        logger.info("正在初始化Camera Motion评测服务...")
        init_camera_predictor()
        
        # 启动Flask服务
        logger.info("启动Flask服务器在 http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1) 