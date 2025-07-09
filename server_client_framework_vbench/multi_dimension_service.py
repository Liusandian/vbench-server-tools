import os
import json
import logging
import importlib
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import traceback
from vbench2.utils import init_submodules, load_dimension_info
from vbench import utils as vbench_utils
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

class MultiDimensionService:
    def __init__(self):
        self.device = None
        self.submodules_dict = {}
        self.initialized_dimensions = set()
        self.supported_dimensions = {
            # VBench 1.0 维度
            'aesthetic_quality': {
                'module': 'vbench.aesthetic_quality',
                'function': 'compute_aesthetic_quality',
                'version': '1.0',
                'description': '美学质量评测'
            },
            'subject_consistency': {
                'module': 'vbench.subject_consistency',
                'function': 'compute_subject_consistency', 
                'version': '1.0',
                'description': '主体一致性评测'
            },
            'background_consistency': {
                'module': 'vbench.background_consistency',
                'function': 'compute_background_consistency',
                'version': '1.0', 
                'description': '背景一致性评测'
            },
            'temporal_flickering': {
                'module': 'vbench.temporal_flickering',
                'function': 'compute_temporal_flickering',
                'version': '1.0',
                'description': '时序闪烁评测'
            },
            'motion_smoothness': {
                'module': 'vbench.motion_smoothness',
                'function': 'compute_motion_smoothness',
                'version': '1.0',
                'description': '运动平滑性评测'
            },
            'dynamic_degree': {
                'module': 'vbench.dynamic_degree',
                'function': 'compute_dynamic_degree',
                'version': '1.0',
                'description': '动态程度评测'
            },
            'imaging_quality': {
                'module': 'vbench.imaging_quality',
                'function': 'compute_imaging_quality',
                'version': '1.0',
                'description': '成像质量评测'
            },
            'object_class': {
                'module': 'vbench.object_class',
                'function': 'compute_object_class',
                'version': '1.0',
                'description': '对象类别评测'
            },
            'multiple_objects': {
                'module': 'vbench.multiple_objects',
                'function': 'compute_multiple_objects',
                'version': '1.0',
                'description': '多对象评测'
            },
            'human_action': {
                'module': 'vbench.human_action',
                'function': 'compute_human_action',
                'version': '1.0',
                'description': '人类动作评测'
            },
            'color': {
                'module': 'vbench.color',
                'function': 'compute_color',
                'version': '1.0',
                'description': '颜色评测'
            },
            'spatial_relationship': {
                'module': 'vbench.spatial_relationship',
                'function': 'compute_spatial_relationship',
                'version': '1.0',
                'description': '空间关系评测'
            },
            'scene': {
                'module': 'vbench.scene',
                'function': 'compute_scene',
                'version': '1.0',
                'description': '场景评测'
            },
            'appearance_style': {
                'module': 'vbench.appearance_style',
                'function': 'compute_appearance_style',
                'version': '1.0',
                'description': '外观风格评测'
            },
            'temporal_style': {
                'module': 'vbench.temporal_style',
                'function': 'compute_temporal_style',
                'version': '1.0',
                'description': '时序风格评测'
            },
            'overall_consistency': {
                'module': 'vbench.overall_consistency',
                'function': 'compute_overall_consistency',
                'version': '1.0',
                'description': '整体一致性评测'
            },
            
            # VBench 2.0 维度
            'camera_motion': {
                'module': 'vbench2.camera_motion',
                'function': 'compute_camera_motion',
                'version': '2.0',
                'description': '运镜评测'
            },
            'human_identity': {
                'module': 'vbench2.human_identity',
                'function': 'compute_human_identity',
                'version': '2.0',
                'description': '人物身份一致性评测'
            },
            'human_clothes': {
                'module': 'vbench2.human_clothes',
                'function': 'compute_human_clothes',
                'version': '2.0',
                'description': '人物服装评测'
            },
            'human_anatomy': {
                'module': 'vbench2.human_anatomy',
                'function': 'compute_human_anatomy',
                'version': '2.0',
                'description': '人体解剖评测'
            },
            'human_interaction': {
                'module': 'vbench2.human_interaction',
                'function': 'compute_human_interaction',
                'version': '2.0',
                'description': '人物交互评测'
            },
            'composition': {
                'module': 'vbench2.composition',
                'function': 'compute_composition',
                'version': '2.0',
                'description': '构图评测'
            },
            'diversity': {
                'module': 'vbench2.diversity',
                'function': 'compute_diversity',
                'version': '2.0',
                'description': '多样性评测'
            },
            'dynamic_attribute': {
                'module': 'vbench2.dynamic_attribute',
                'function': 'compute_dynamic_attribute',
                'version': '2.0',
                'description': '动态属性评测'
            },
            'dynamic_spatial_relationship': {
                'module': 'vbench2.dynamic_spatial_relationship',
                'function': 'compute_dynamic_spatial_relationship',
                'version': '2.0',
                'description': '动态空间关系评测'
            },
            'instance_preservation': {
                'module': 'vbench2.instance_preservation',
                'function': 'compute_instance_preservation',
                'version': '2.0',
                'description': '实例保存评测'
            },
            'motion_rationality': {
                'module': 'vbench2.motion_rationality',
                'function': 'compute_motion_rationality',
                'version': '2.0',
                'description': '运动合理性评测'
            },
            'motion_order_understanding': {
                'module': 'vbench2.motion_order_understanding',
                'function': 'compute_motion_order_understanding',
                'version': '2.0',
                'description': '运动顺序理解评测'
            },
            'complex_landscape': {
                'module': 'vbench2.complex_landscape',
                'function': 'compute_complex_landscape',
                'version': '2.0',
                'description': '复杂风景评测'
            },
            'complex_plot': {
                'module': 'vbench2.complex_plot',
                'function': 'compute_complex_plot',
                'version': '2.0',
                'description': '复杂情节评测'
            },
            'multi_view_consistency': {
                'module': 'vbench2.multi_view_consistency',
                'function': 'compute_multi_view_consistency',
                'version': '2.0',
                'description': '多视角一致性评测'
            },
            'material': {
                'module': 'vbench2.material',
                'function': 'compute_material',
                'version': '2.0',
                'description': '材质评测'
            },
            'mechanics': {
                'module': 'vbench2.mechanics',
                'function': 'compute_mechanics',
                'version': '2.0',
                'description': '力学评测'
            },
            'thermotics': {
                'module': 'vbench2.thermotics',
                'function': 'compute_thermotics',
                'version': '2.0',
                'description': '热力学评测'
            }
        }
        
    def initialize_dimension(self, dimension, device='cuda:0', local_mode=False):
        """初始化特定评测维度"""
        try:
            if dimension not in self.supported_dimensions:
                raise ValueError(f"不支持的评测维度: {dimension}")
            
            # 设置设备
            if torch.cuda.is_available() and 'cuda' in device:
                self.device = device
                logger.info(f"Using device: {device}")
            else:
                self.device = 'cpu'
                logger.warning("CUDA not available, falling back to CPU")
            
            # 初始化子模块
            logger.info(f"Initializing {dimension} submodules...")
            
            # 根据版本选择初始化方法
            version = self.supported_dimensions[dimension]['version']
            if version == '2.0':
                # VBench 2.0 使用新的初始化方式
                submodules_dict = init_submodules([dimension.title().replace('_', '_')], local=local_mode)
                self.submodules_dict[dimension] = submodules_dict.get(dimension.title().replace('_', '_'), {})
            else:
                # VBench 1.0 使用旧的初始化方式
                self.submodules_dict[dimension] = self._init_vbench1_submodules(dimension, local_mode)
            
            self.initialized_dimensions.add(dimension)
            logger.info(f"{dimension} initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {dimension}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _init_vbench1_submodules(self, dimension, local_mode):
        """为 VBench 1.0 维度初始化子模块"""
        # 这里需要根据具体维度返回相应的子模块配置
        # 简化处理，返回基本配置
        if dimension == 'aesthetic_quality':
            return [
                'ViT-L/14',  # CLIP model path
                'pretrained/aesthetic_model'  # aesthetic model path
            ]
        elif dimension == 'subject_consistency':
            return {
                'repo': 'facebookresearch/dino:main',
                'model': 'dino_vitb16',
                'read_frame': False
            }
        else:
            # 其他维度的基本配置
            return {}
    
    def evaluate_dimension(self, dimension, video_paths, json_dir=None):
        """评测特定维度"""
        try:
            if dimension not in self.initialized_dimensions:
                raise ValueError(f"维度 {dimension} 未初始化")
            
            # 导入相应的模块
            dim_info = self.supported_dimensions[dimension]
            module = importlib.import_module(dim_info['module'])
            compute_func = getattr(module, dim_info['function'])
            
            # 准备评测数据
            if json_dir is None:
                # 如果没有提供 JSON 目录，创建临时评测数据
                prompt_dict_ls = []
                for video_path in video_paths:
                    prompt_dict_ls.append({
                        'video_list': [video_path],
                        'prompt': f"Evaluate {dimension} for video"
                    })
                
                # 模拟调用评测函数
                if dimension == 'camera_motion':
                    from vbench2.camera_motion import camera_motion, CameraPredict
                    camera_predictor = CameraPredict(self.device, self.submodules_dict[dimension])
                    avg_score, video_results = camera_motion(prompt_dict_ls, camera_predictor)
                elif dimension == 'human_identity':
                    avg_score, video_results = compute_func(
                        json_dir=None, 
                        device=self.device, 
                        submodules_dict=self.submodules_dict[dimension]
                    )
                elif dimension == 'aesthetic_quality':
                    avg_score, video_results = compute_func(
                        json_dir=None,
                        device=self.device,
                        submodules_list=self.submodules_dict[dimension]
                    )
                else:
                    # 其他维度的通用调用
                    avg_score, video_results = compute_func(
                        json_dir=json_dir,
                        device=self.device,
                        submodules_dict=self.submodules_dict.get(dimension, {})
                    )
            else:
                # 使用提供的 JSON 目录
                avg_score, video_results = compute_func(
                    json_dir=json_dir,
                    device=self.device,
                    submodules_dict=self.submodules_dict.get(dimension, {})
                )
            
            return avg_score, video_results
            
        except Exception as e:
            logger.error(f"Error evaluating {dimension}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

# 全局服务实例
multi_service = MultiDimensionService()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'VBench Multi-Dimension Evaluation',
        'initialized_dimensions': list(multi_service.initialized_dimensions),
        'supported_dimensions': list(multi_service.supported_dimensions.keys())
    })

@app.route('/dimensions', methods=['GET'])
def get_supported_dimensions():
    """获取支持的评测维度列表"""
    dimensions = {}
    for dim, info in multi_service.supported_dimensions.items():
        dimensions[dim] = {
            'description': info['description'],
            'version': info['version'],
            'initialized': dim in multi_service.initialized_dimensions
        }
    
    return jsonify({
        'status': 'success',
        'supported_dimensions': dimensions,
        'total_count': len(dimensions),
        'initialized_count': len(multi_service.initialized_dimensions)
    })

@app.route('/initialize', methods=['POST'])
def initialize_dimension():
    """初始化评测维度"""
    try:
        data = request.json if request.json else {}
        
        # 获取要初始化的维度
        dimensions = data.get('dimensions', ['camera_motion'])
        if isinstance(dimensions, str):
            dimensions = [dimensions]
        
        device = data.get('device', 'cuda:0')
        local_mode = data.get('local_mode', False)
        
        # 验证维度
        invalid_dims = [d for d in dimensions if d not in multi_service.supported_dimensions]
        if invalid_dims:
            return jsonify({
                'status': 'error',
                'message': f'不支持的评测维度: {invalid_dims}',
                'supported_dimensions': list(multi_service.supported_dimensions.keys())
            }), 400
        
        # 初始化维度
        success_dims = []
        failed_dims = []
        
        for dimension in dimensions:
            if multi_service.initialize_dimension(dimension, device, local_mode):
                success_dims.append(dimension)
            else:
                failed_dims.append(dimension)
        
        result = {
            'status': 'success' if not failed_dims else 'partial',
            'device': multi_service.device,
            'initialized_dimensions': success_dims,
            'failed_dimensions': failed_dims,
            'total_initialized': len(multi_service.initialized_dimensions)
        }
        
        if failed_dims:
            result['message'] = f'部分维度初始化失败: {failed_dims}'
            return jsonify(result), 207  # Multi-Status
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/evaluate', methods=['POST'])
def evaluate_multi_dimension():
    """多维度评测接口"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # 验证必需参数
        if 'video_paths' not in data:
            return jsonify({
                'status': 'error',
                'message': 'video_paths is required'
            }), 400
        
        video_paths = data['video_paths']
        if not isinstance(video_paths, list):
            video_paths = [video_paths]
        
        # 检查视频文件是否存在
        for video_path in video_paths:
            if not os.path.exists(video_path):
                return jsonify({
                    'status': 'error',
                    'message': f'Video file not found: {video_path}'
                }), 400
        
        # 获取要评测的维度
        dimensions = data.get('dimensions', ['camera_motion'])
        if isinstance(dimensions, str):
            dimensions = [dimensions]
        
        # 验证维度是否已初始化
        uninitialized_dims = [d for d in dimensions if d not in multi_service.initialized_dimensions]
        if uninitialized_dims:
            return jsonify({
                'status': 'error',
                'message': f'以下维度未初始化: {uninitialized_dims}',
                'hint': '请先调用 /initialize 接口初始化维度'
            }), 400
        
        # 执行评测
        logger.info(f"Starting multi-dimension evaluation for {len(video_paths)} videos...")
        
        results = {}
        overall_scores = {}
        
        for dimension in dimensions:
            try:
                logger.info(f"Evaluating dimension: {dimension}")
                avg_score, video_results = multi_service.evaluate_dimension(
                    dimension, video_paths, data.get('json_dir')
                )
                
                results[dimension] = {
                    'overall_score': float(avg_score),
                    'video_results': video_results,
                    'description': multi_service.supported_dimensions[dimension]['description']
                }
                overall_scores[dimension] = float(avg_score)
                
            except Exception as e:
                logger.error(f"Error evaluating {dimension}: {str(e)}")
                results[dimension] = {
                    'error': str(e),
                    'description': multi_service.supported_dimensions[dimension]['description']
                }
        
        # 计算总体评分
        valid_scores = [score for score in overall_scores.values() if isinstance(score, (int, float))]
        final_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        
        response = {
            'status': 'success',
            'final_score': final_score,
            'dimension_scores': overall_scores,
            'detailed_results': results,
            'video_count': len(video_paths),
            'evaluated_dimensions': dimensions
        }
        
        logger.info(f"Multi-dimension evaluation completed. Final score: {final_score}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/evaluate_single', methods=['POST'])
def evaluate_single_dimension():
    """单维度评测接口"""
    try:
        data = request.json
        if not data or 'video_path' not in data or 'dimension' not in data:
            return jsonify({
                'status': 'error',
                'message': 'video_path and dimension are required'
            }), 400
        
        video_path = data['video_path']
        dimension = data['dimension']
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            return jsonify({
                'status': 'error',
                'message': f'Video file not found: {video_path}'
            }), 400
        
        # 检查维度是否已初始化
        if dimension not in multi_service.initialized_dimensions:
            return jsonify({
                'status': 'error',
                'message': f'维度 {dimension} 未初始化',
                'hint': '请先调用 /initialize 接口初始化维度'
            }), 400
        
        # 执行评测
        logger.info(f"Evaluating {dimension} for single video: {video_path}")
        
        avg_score, video_results = multi_service.evaluate_dimension(
            dimension, [video_path], data.get('json_dir')
        )
        
        response = {
            'status': 'success',
            'dimension': dimension,
            'description': multi_service.supported_dimensions[dimension]['description'],
            'video_path': video_path,
            'score': float(avg_score),
            'detailed_results': video_results[0] if video_results else {}
        }
        
        logger.info(f"Single dimension evaluation completed for {video_path}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error during single dimension evaluation: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # 启动时的配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))  # 使用不同端口避免冲突
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting VBench Multi-Dimension Evaluation Service on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Supported dimensions: {len(multi_service.supported_dimensions)}")
    
    app.run(host=HOST, port=PORT, debug=DEBUG) 