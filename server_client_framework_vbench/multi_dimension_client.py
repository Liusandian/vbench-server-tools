#!/usr/bin/env python3
"""
VBench 多维度评测服务客户端

支持美学质量、人物身份一致性等多个评测维度的调用
"""

import argparse
import json
import requests
import os
import time
from typing import List, Optional, Dict

class MultiDimensionClient:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self) -> dict:
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_supported_dimensions(self) -> dict:
        """获取支持的评测维度"""
        try:
            response = self.session.get(f"{self.base_url}/dimensions", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def initialize_dimensions(self, dimensions: List[str], device: str = "cuda:0", local_mode: bool = False) -> dict:
        """初始化评测维度"""
        try:
            data = {
                "dimensions": dimensions,
                "device": device,
                "local_mode": local_mode
            }
            response = self.session.post(
                f"{self.base_url}/initialize", 
                json=data, 
                timeout=600  # 初始化可能需要很长时间
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def evaluate_multi_dimension(self, video_paths: List[str], dimensions: List[str], json_dir: Optional[str] = None) -> dict:
        """多维度评测"""
        try:
            data = {
                "video_paths": video_paths,
                "dimensions": dimensions
            }
            if json_dir:
                data["json_dir"] = json_dir
                
            response = self.session.post(
                f"{self.base_url}/evaluate", 
                json=data, 
                timeout=1800  # 多维度评测可能需要很长时间
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def evaluate_single_dimension(self, video_path: str, dimension: str, json_dir: Optional[str] = None) -> dict:
        """单维度评测"""
        try:
            data = {
                "video_path": video_path,
                "dimension": dimension
            }
            if json_dir:
                data["json_dir"] = json_dir
                
            response = self.session.post(
                f"{self.base_url}/evaluate_single", 
                json=data, 
                timeout=600
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

def print_result(result: dict, action: str):
    """格式化打印结果"""
    print(f"\n=== {action.upper()} 结果 ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("status") == "success":
        print(f"\n✅ {action} 成功")
        
        if action == "dimensions" and "supported_dimensions" in result:
            dimensions = result["supported_dimensions"]
            print(f"\n📋 支持的评测维度 ({len(dimensions)} 个):")
            for dim, info in dimensions.items():
                status = "✅ 已初始化" if info["initialized"] else "⭕ 未初始化"
                print(f"  • {dim}: {info['description']} (v{info['version']}) {status}")
            
        elif action == "initialize" and "initialized_dimensions" in result:
            dims = result["initialized_dimensions"]
            print(f"🎉 成功初始化 {len(dims)} 个维度: {', '.join(dims)}")
            if result.get("failed_dimensions"):
                failed = result["failed_dimensions"]
                print(f"❌ 初始化失败: {', '.join(failed)}")
                
        elif action == "evaluate" and "final_score" in result:
            score = result["final_score"]
            dims = result.get("evaluated_dimensions", [])
            print(f"📊 最终评分: {score:.4f}")
            print(f"📹 评测维度: {', '.join(dims)}")
            
            if "dimension_scores" in result:
                print(f"\n📈 各维度评分:")
                for dim, score in result["dimension_scores"].items():
                    print(f"  • {dim}: {score:.4f}")
                    
        elif action == "single_evaluate" and "score" in result:
            score = result["score"]
            dim = result.get("dimension", "")
            print(f"📊 {dim} 评分: {score:.4f}")
            
    else:
        print(f"\n❌ {action} 失败: {result.get('message', '未知错误')}")

def main():
    parser = argparse.ArgumentParser(description="VBench 多维度评测客户端")
    parser.add_argument("--url", default="http://localhost:5001", help="服务端地址")
    parser.add_argument("--action", required=True, 
                       choices=["health", "dimensions", "init", "evaluate", "single"], 
                       help="操作类型")
    
    # 维度相关参数
    parser.add_argument("--dimensions", nargs="+", 
                       help="评测维度列表")
    
    # 视频相关参数
    parser.add_argument("--video_path", help="单个视频文件路径")
    parser.add_argument("--video_paths", nargs="+", help="多个视频文件路径")
    parser.add_argument("--json_dir", help="JSON 配置目录")
    
    # 设备配置
    parser.add_argument("--device", default="cuda:0", help="设备类型")
    parser.add_argument("--local_mode", action="store_true", help="本地模式")
    
    args = parser.parse_args()
    
    # 创建客户端
    client = MultiDimensionClient(args.url)
    
    # 根据操作类型执行相应功能
    if args.action == "health":
        result = client.health_check()
        print_result(result, "health_check")
        
    elif args.action == "dimensions":
        result = client.get_supported_dimensions()
        print_result(result, "dimensions")
        
    elif args.action == "init":
        if not args.dimensions:
            print("❌ 错误: --dimensions 参数是必需的")
            print("💡 提示: 可用的维度包括:")
            print("  • aesthetic_quality (美学质量)")
            print("  • camera_motion (运镜)")
            print("  • human_identity (人物身份一致性)")
            print("  • subject_consistency (主体一致性)")
            print("  • 等等...")
            return
            
        print(f"🔄 正在初始化维度: {', '.join(args.dimensions)}")
        result = client.initialize_dimensions(args.dimensions, args.device, args.local_mode)
        print_result(result, "initialize")
        
    elif args.action == "evaluate":
        if not args.video_paths or not args.dimensions:
            print("❌ 错误: --video_paths 和 --dimensions 参数是必需的")
            return
            
        # 检查视频文件是否存在
        missing_files = [path for path in args.video_paths if not os.path.exists(path)]
        if missing_files:
            print(f"❌ 错误: 以下视频文件不存在:")
            for file in missing_files:
                print(f"  - {file}")
            return
            
        print(f"📊 正在进行多维度评测...")
        print(f"📹 视频数量: {len(args.video_paths)}")
        print(f"📋 评测维度: {', '.join(args.dimensions)}")
        
        result = client.evaluate_multi_dimension(
            args.video_paths, args.dimensions, args.json_dir
        )
        print_result(result, "evaluate")
        
    elif args.action == "single":
        if not args.video_path or not args.dimensions or len(args.dimensions) != 1:
            print("❌ 错误: --video_path 和单个 --dimensions 参数是必需的")
            return
            
        if not os.path.exists(args.video_path):
            print(f"❌ 错误: 视频文件不存在: {args.video_path}")
            return
            
        dimension = args.dimensions[0]
        print(f"📊 正在评测 {dimension}: {args.video_path}")
        
        result = client.evaluate_single_dimension(
            args.video_path, dimension, args.json_dir
        )
        print_result(result, "single_evaluate")

if __name__ == "__main__":
    main() 