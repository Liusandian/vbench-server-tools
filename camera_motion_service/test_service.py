#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Motion Service Test Script
服务测试脚本
"""

import os
import sys
import json
import time
import requests
import subprocess
import tempfile
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    
    required_packages = ['flask', 'torch', 'cv2', 'decord', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'torch':
                import torch
            elif package == 'flask':
                import flask
            elif package == 'decord':
                import decord
            elif package == 'numpy':
                import numpy
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ 缺少依赖: {missing_packages}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def check_vbench_path():
    """检查VBench-2.0路径"""
    print("\n🔍 检查VBench-2.0路径...")
    
    current_dir = Path(__file__).parent.absolute()
    vbench_path = current_dir.parent / "VBench-2.0"
    
    if not vbench_path.exists():
        print(f"❌ VBench-2.0路径不存在: {vbench_path}")
        return False
    
    # 检查关键文件
    key_files = [
        "vbench2/__init__.py",
        "vbench2/camera_motion.py",
        "vbench2/utils.py"
    ]
    
    for file in key_files:
        file_path = vbench_path / file
        if not file_path.exists():
            print(f"❌ 关键文件不存在: {file_path}")
            return False
        print(f"  ✅ {file}")
    
    print("✅ VBench-2.0路径正确")
    return True

def test_server_start():
    """测试服务器启动"""
    print("\n🔍 测试服务器启动...")
    
    # 检查端口是否被占用
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=2)
        print("⚠️  端口5000可能已被占用")
        return True  # 端口被占用但可能是我们的服务
    except requests.exceptions.RequestException:
        print("✅ 端口5000可用")
        return True

def test_api_endpoints():
    """测试API接口"""
    print("\n🔍 测试API接口...")
    
    base_url = "http://127.0.0.1:5000"
    
    # 测试主页
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 主页: {data.get('message', 'N/A')}")
        else:
            print(f"  ❌ 主页: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 主页连接失败: {e}")
        return False
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 健康检查: {data.get('status', 'N/A')}")
            print(f"  🖥️  设备: {data.get('device', 'N/A')}")
        else:
            print(f"  ❌ 健康检查: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 健康检查失败: {e}")
        return False
    
    print("✅ API接口正常")
    return True

def create_test_video():
    """创建测试视频"""
    print("\n🔍 创建测试视频...")
    
    try:
        import cv2
        import numpy as np
        
        # 创建一个简单的测试视频
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, 'test_video.mp4')
        
        out = cv2.VideoWriter(video_path, fourcc, 10.0, (640, 480))
        
        # 创建30帧的简单动画（静态->移动）
        for i in range(30):
            # 创建黑色背景
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 添加一个移动的白色矩形
            x = 50 + i * 5  # 从左到右移动
            y = 200
            cv2.rectangle(frame, (x, y), (x+100, y+80), (255, 255, 255), -1)
            
            # 添加文字
            cv2.putText(frame, f'Frame {i+1}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        
        if os.path.exists(video_path):
            print(f"  ✅ 测试视频已创建: {video_path}")
            return video_path
        else:
            print("  ❌ 测试视频创建失败")
            return None
            
    except Exception as e:
        print(f"  ❌ 创建测试视频失败: {e}")
        return None

def test_video_evaluation(video_path):
    """测试视频评估"""
    print("\n🔍 测试视频评估...")
    
    if not video_path or not os.path.exists(video_path):
        print("  ❌ 测试视频不存在")
        return False
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        # 准备文件上传
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {'motion_type': 'pan_right'}  # 期望右移
            
            print("  🚀 上传测试视频...")
            response = requests.post(
                f"{base_url}/evaluate",
                files=files,
                data=data,
                timeout=120  # 2分钟超时
            )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            eval_result = result.get('result', {})
            
            print(f"  ✅ 评估完成")
            print(f"  📋 任务ID: {task_id}")
            print(f"  🎯 预测运动: {eval_result.get('predicted_motions', [])}")
            print(f"  📊 评分: {eval_result.get('score', 'N/A')}")
            print(f"  📹 分辨率: {eval_result.get('resolution', 'N/A')}")
            print(f"  ⏱️  FPS: {eval_result.get('fps', 'N/A')}")
            
            return True
        else:
            print(f"  ❌ 评估失败: HTTP {response.status_code}")
            try:
                error_info = response.json()
                print(f"     错误信息: {error_info.get('error', '未知错误')}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"  ❌ 评估过程出错: {e}")
        return False

def test_batch_evaluation():
    """测试批量评估"""
    print("\n🔍 测试批量评估...")
    
    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"  📁 创建input目录: {input_dir}")
        os.makedirs(input_dir)
    
    # 检查是否有视频文件
    video_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            video_files.append(file)
    
    if not video_files:
        print("  📁 input文件夹中没有视频文件，跳过批量评估测试")
        return True
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        print(f"  🚀 开始批量评估 ({len(video_files)} 个文件)...")
        response = requests.post(f"{base_url}/batch_evaluate", timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            batch_id = result.get('batch_id')
            summary = result.get('summary', {})
            
            print(f"  ✅ 批量评估完成")
            print(f"  📋 批次ID: {batch_id}")
            print(f"  📊 总文件数: {summary.get('total_files', 0)}")
            print(f"  ✅ 处理成功: {summary.get('processed_files', 0)}")
            print(f"  ❌ 处理失败: {summary.get('failed_files', 0)}")
            
            return True
        else:
            print(f"  ❌ 批量评估失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ 批量评估出错: {e}")
        return False

def cleanup_test_files(video_path):
    """清理测试文件"""
    print("\n🧹 清理测试文件...")
    
    if video_path and os.path.exists(video_path):
        try:
            os.remove(video_path)
            print(f"  ✅ 已删除测试视频: {video_path}")
        except Exception as e:
            print(f"  ⚠️  删除测试视频失败: {e}")

def main():
    """主测试函数"""
    print("🧪 Camera Motion Service 测试")
    print("=" * 50)
    
    # 测试检查列表
    tests = [
        ("依赖检查", check_dependencies),
        ("VBench路径检查", check_vbench_path),
        ("服务器启动检查", test_server_start),
    ]
    
    # 执行基础检查
    all_passed = True
    for test_name, test_func in tests:
        result = test_func()
        if not result:
            all_passed = False
            break
    
    if not all_passed:
        print("\n❌ 基础检查未通过，请修复问题后重试")
        return
    
    print("\n✅ 基础检查通过!")
    
    # 询问是否进行服务测试
    try:
        user_input = input("\n是否进行服务功能测试? (需要服务器运行) [y/N]: ").lower()
        if user_input not in ['y', 'yes']:
            print("🏁 测试完成")
            return
    except KeyboardInterrupt:
        print("\n🏁 测试被中断")
        return
    
    # 服务功能测试
    service_tests = [
        ("API接口测试", test_api_endpoints),
    ]
    
    for test_name, test_func in service_tests:
        print(f"\n🧪 {test_name}...")
        result = test_func()
        if not result:
            print(f"❌ {test_name}失败")
            return
    
    # 视频评估测试
    video_path = create_test_video()
    if video_path:
        test_video_evaluation(video_path)
        cleanup_test_files(video_path)
    
    # 批量评估测试
    test_batch_evaluation()
    
    print("\n🎉 所有测试完成!")
    print("\n💡 提示:")
    print("- 如果测试通过，说明服务配置正确")
    print("- 如果某项测试失败，请检查对应的配置和依赖")
    print("- 查看logs/server.log获取详细错误信息")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc() 