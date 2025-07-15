#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Motion Service Usage Example
使用示例脚本
"""

import os
import time
import requests
import json
from client import CameraMotionClient

def example_basic_usage():
    """基础使用示例"""
    print("=== Camera Motion Service 使用示例 ===\n")
    
    # 创建客户端
    client = CameraMotionClient("http://127.0.0.1:5000")
    
    # 1. 健康检查
    print("1. 检查服务器状态...")
    if not client.check_server_health():
        print("❌ 服务器未启动或不健康")
        print("请先启动服务器: python server.py")
        return
    print("✅ 服务器状态正常\n")
    
    # 2. 查看可用的API接口
    print("2. 查看服务信息...")
    try:
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 200:
            info = response.json()
            print(f"服务: {info['message']}")
            print(f"版本: {info['version']}")
            print("可用接口:")
            for endpoint, desc in info['endpoints'].items():
                print(f"  {endpoint}: {desc}")
        print()
    except Exception as e:
        print(f"获取服务信息失败: {e}\n")

def example_video_evaluation():
    """视频评估示例"""
    print("3. 视频评估示例...")
    
    # 检查是否有示例视频文件
    input_dir = "input"
    video_files = []
    if os.path.exists(input_dir):
        for file in os.listdir(input_dir):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                video_files.append(os.path.join(input_dir, file))
    
    client = CameraMotionClient("http://127.0.0.1:5000")
    
    if video_files:
        # 评估第一个视频文件
        video_path = video_files[0]
        print(f"📹 评估视频: {video_path}")
        
        try:
            # 可以指定期望的运动类型
            motion_types = ['zoom_in', 'pan_left', 'static']
            for motion_type in motion_types:
                print(f"\n🎯 期望运动类型: {motion_type}")
                result = client.upload_and_evaluate(video_path, motion_type)
                
                if 'result' in result:
                    eval_result = result['result']
                    print(f"  预测运动: {eval_result.get('predicted_motions', [])}")
                    print(f"  匹配得分: {eval_result.get('score', 0.0)}")
                    print(f"  任务ID: {result.get('task_id', 'N/A')}")
                    
                time.sleep(1)  # 避免频繁请求
                
        except Exception as e:
            print(f"❌ 评估失败: {e}")
    else:
        print("📁 input文件夹中没有找到视频文件")
        print("请将视频文件放入input文件夹中再运行此示例")

def example_batch_evaluation():
    """批量评估示例"""
    print("\n4. 批量评估示例...")
    
    input_dir = "input"
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"📁 已创建input文件夹: {input_dir}")
        print("请将要评估的视频文件放入此文件夹")
        return
    
    # 检查是否有视频文件
    video_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            video_files.append(file)
    
    if len(video_files) == 0:
        print("📁 input文件夹中没有视频文件")
        print("请将视频文件放入input文件夹中")
        return
    
    print(f"📹 找到 {len(video_files)} 个视频文件:")
    for i, file in enumerate(video_files, 1):
        print(f"  {i}. {file}")
    
    client = CameraMotionClient("http://127.0.0.1:5000")
    
    try:
        print("\n🚀 开始批量评估...")
        result = client.batch_evaluate()
        
        print(f"✅ 批量评估完成!")
        print(f"  批次ID: {result.get('batch_id', 'N/A')}")
        summary = result.get('summary', {})
        print(f"  总文件数: {summary.get('total_files', 0)}")
        print(f"  处理成功: {summary.get('processed_files', 0)}")
        print(f"  处理失败: {summary.get('failed_files', 0)}")
        
    except Exception as e:
        print(f"❌ 批量评估失败: {e}")

def example_result_management():
    """结果管理示例"""
    print("\n5. 结果管理示例...")
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        print("📁 output文件夹不存在，没有历史结果")
        return
    
    # 查找所有结果文件
    result_files = []
    for file in os.listdir(output_dir):
        if file.endswith('_result.json'):
            result_files.append(file)
    
    if not result_files:
        print("📄 没有找到历史结果文件")
        return
    
    print(f"📄 找到 {len(result_files)} 个结果文件:")
    
    # 显示最近的几个结果
    result_files.sort(reverse=True)  # 按文件名排序（包含时间戳）
    
    for i, file in enumerate(result_files[:3], 1):  # 只显示最近3个
        print(f"\n{i}. {file}")
        
        try:
            with open(os.path.join(output_dir, file), 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            print(f"   原始文件: {result.get('original_filename', 'N/A')}")
            print(f"   预测运动: {result.get('predicted_motions', [])}")
            print(f"   评分: {result.get('score', 'N/A')}")
            print(f"   时间: {result.get('timestamp', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ 读取文件失败: {e}")

def create_sample_video_info():
    """创建示例说明"""
    print("\n📝 如何准备测试视频:")
    print("1. 将视频文件放入 'input' 文件夹")
    print("2. 支持的格式: mp4, avi, mov, mkv, webm")
    print("3. 建议视频长度: 3-10秒")
    print("4. 建议分辨率: 不超过1920x1080")
    print("5. 建议文件大小: 不超过100MB")
    print("\n📋 支持的运动类型:")
    motion_types = [
        'zoom_in (放大)', 'zoom_out (缩小)', 
        'pan_left (左移)', 'pan_right (右移)',
        'tilt_up (上倾)', 'tilt_down (下倾)',
        'static (静态)', 'orbits (环绕)', 'oblique (斜向)'
    ]
    for motion in motion_types:
        print(f"  - {motion}")

def main():
    """主函数"""
    print("🎬 Camera Motion Evaluation Service - 使用示例")
    print("=" * 60)
    
    try:
        # 基础使用
        example_basic_usage()
        
        # 视频评估
        example_video_evaluation()
        
        # 批量评估
        example_batch_evaluation()
        
        # 结果管理
        example_result_management()
        
        # 示例说明
        create_sample_video_info()
        
        print("\n✅ 示例演示完成!")
        print("\n💡 提示:")
        print("- 使用 'python client.py --help' 查看完整命令选项")
        print("- 查看 README.md 了解详细使用说明")
        print("- 检查 logs/server.log 获取详细日志信息")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  示例被用户中断")
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")

if __name__ == '__main__':
    main() 