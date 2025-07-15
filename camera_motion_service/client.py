#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Motion Evaluation Client
Camera Motion评测服务的客户端
"""

import os
import json
import time
import argparse
import requests
from pathlib import Path

class CameraMotionClient:
    """Camera Motion评测客户端"""
    
    def __init__(self, server_url="http://127.0.0.1:5000"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def check_server_health(self):
        """检查服务器健康状态"""
        try:
            response = self.session.get(f"{self.server_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"服务器状态: {health_data['status']}")
                print(f"使用设备: {health_data['device']}")
                return health_data['status'] == 'healthy'
            else:
                print(f"服务器健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"无法连接到服务器: {e}")
            return False
    
    def upload_and_evaluate(self, video_path, motion_type=None):
        """
        上传视频并进行评估
        
        Args:
            video_path: 视频文件路径
            motion_type: 期望的运动类型 (可选)
            
        Returns:
            dict: 评估结果
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        print(f"正在上传视频: {video_path}")
        
        # 准备文件上传
        files = {'video': open(video_path, 'rb')}
        data = {}
        if motion_type:
            data['motion_type'] = motion_type
        
        try:
            # 发送POST请求
            response = self.session.post(
                f"{self.server_url}/evaluate",
                files=files,
                data=data,
                timeout=300  # 5分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                print("评估完成!")
                return result
            else:
                error_msg = response.json().get('error', '未知错误')
                raise Exception(f"评估失败 ({response.status_code}): {error_msg}")
                
        finally:
            files['video'].close()
    
    def get_result(self, task_id):
        """
        获取评估结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 评估结果
        """
        try:
            response = self.session.get(f"{self.server_url}/results/{task_id}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise Exception("结果不存在")
            else:
                error_msg = response.json().get('error', '未知错误')
                raise Exception(f"获取结果失败 ({response.status_code}): {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {e}")
    
    def download_result(self, task_id, save_path=None):
        """
        下载评估结果文件
        
        Args:
            task_id: 任务ID
            save_path: 保存路径 (可选)
            
        Returns:
            str: 保存的文件路径
        """
        try:
            response = self.session.get(f"{self.server_url}/results/{task_id}/download")
            
            if response.status_code == 200:
                if save_path is None:
                    save_path = f"{task_id}_result.json"
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"结果已保存到: {save_path}")
                return save_path
            else:
                error_msg = response.json().get('error', '未知错误')
                raise Exception(f"下载失败 ({response.status_code}): {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"下载请求失败: {e}")
    
    def batch_evaluate(self):
        """
        批量评估input文件夹中的视频
        
        Returns:
            dict: 批量评估结果
        """
        try:
            print("开始批量评估...")
            response = self.session.post(f"{self.server_url}/batch_evaluate")
            
            if response.status_code == 200:
                result = response.json()
                print("批量评估完成!")
                return result
            else:
                error_msg = response.json().get('error', '未知错误')
                raise Exception(f"批量评估失败 ({response.status_code}): {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"批量评估请求失败: {e}")

def print_result(result):
    """打印评估结果"""
    if 'result' in result:
        eval_result = result['result']
        print("\n=== 评估结果 ===")
        print(f"任务ID: {result.get('task_id', 'N/A')}")
        print(f"原始文件名: {eval_result.get('original_filename', 'N/A')}")
        print(f"预测运动类型: {eval_result.get('predicted_motions', [])}")
        print(f"期望运动类型: {eval_result.get('expected_motion', 'N/A')}")
        print(f"评分: {eval_result.get('score', 'N/A')}")
        print(f"视频分辨率: {eval_result.get('resolution', 'N/A')}")
        print(f"帧数: {eval_result.get('frame_count', 'N/A')}")
        print(f"FPS: {eval_result.get('fps', 'N/A')}")
        print(f"评估时间: {eval_result.get('timestamp', 'N/A')}")
    else:
        print(f"结果: {result}")

def main():
    parser = argparse.ArgumentParser(description='Camera Motion评测客户端')
    parser.add_argument('--server', default='http://127.0.0.1:5000', 
                       help='服务器地址')
    parser.add_argument('--video', type=str, 
                       help='要评估的视频文件路径')
    parser.add_argument('--motion-type', type=str,
                       choices=['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 
                               'tilt_up', 'tilt_down', 'static', 'orbits', 'oblique'],
                       help='期望的运动类型')
    parser.add_argument('--batch', action='store_true',
                       help='批量评估input文件夹中的视频')
    parser.add_argument('--get-result', type=str,
                       help='根据任务ID获取结果')
    parser.add_argument('--download', type=str,
                       help='根据任务ID下载结果文件')
    parser.add_argument('--health', action='store_true',
                       help='检查服务器健康状态')
    
    args = parser.parse_args()
    
    # 创建客户端
    client = CameraMotionClient(args.server)
    
    try:
        if args.health:
            # 健康检查
            client.check_server_health()
            
        elif args.video:
            # 单个视频评估
            if not client.check_server_health():
                print("服务器不健康，无法进行评估")
                return
            
            result = client.upload_and_evaluate(args.video, args.motion_type)
            print_result(result)
            
        elif args.batch:
            # 批量评估
            if not client.check_server_health():
                print("服务器不健康，无法进行评估")
                return
            
            result = client.batch_evaluate()
            print(f"\n=== 批量评估结果 ===")
            print(f"批次ID: {result.get('batch_id', 'N/A')}")
            print(f"总文件数: {result.get('summary', {}).get('total_files', 0)}")
            print(f"处理成功: {result.get('summary', {}).get('processed_files', 0)}")
            print(f"处理失败: {result.get('summary', {}).get('failed_files', 0)}")
            
        elif args.get_result:
            # 获取结果
            result = client.get_result(args.get_result)
            print_result({'result': result})
            
        elif args.download:
            # 下载结果
            file_path = client.download_result(args.download)
            print(f"结果文件已下载: {file_path}")
            
        else:
            print("请指定操作参数，使用 -h 查看帮助")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    main() 