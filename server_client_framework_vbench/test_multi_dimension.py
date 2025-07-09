#!/usr/bin/env python3
"""
VBench 多维度评测服务测试脚本

用于验证多维度服务的各个接口是否正常工作
"""

import requests
import json
import time
import argparse
from typing import List

class MultiDimensionTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def test_health_check(self):
        """测试健康检查接口"""
        print("🔍 测试健康检查接口...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"✅ 健康检查成功: 服务状态正常")
            print(f"📊 已初始化维度: {len(result.get('initialized_dimensions', []))}")
            print(f"📋 支持维度总数: {len(result.get('supported_dimensions', []))}")
            return True
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
    
    def test_get_dimensions(self):
        """测试获取支持的维度接口"""
        print("📋 测试获取支持的维度接口...")
        try:
            response = self.session.get(f"{self.base_url}/dimensions", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "success":
                dimensions = result.get("supported_dimensions", {})
                total_count = result.get("total_count", 0)
                
                print(f"✅ 获取维度列表成功")
                print(f"📊 支持的维度总数: {total_count}")
                
                # 按版本分组显示
                v1_dims = []
                v2_dims = []
                
                for dim, info in dimensions.items():
                    if info.get("version") == "1.0":
                        v1_dims.append(dim)
                    elif info.get("version") == "2.0":
                        v2_dims.append(dim)
                
                print(f"📝 VBench 1.0 维度 ({len(v1_dims)} 个): {', '.join(v1_dims[:5])}{'...' if len(v1_dims) > 5 else ''}")
                print(f"📝 VBench 2.0 维度 ({len(v2_dims)} 个): {', '.join(v2_dims[:5])}{'...' if len(v2_dims) > 5 else ''}")
                
                return True
            else:
                print(f"❌ 获取维度列表失败: {result.get('message', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"❌ 获取维度列表失败: {e}")
            return False
    
    def test_initialize_single_dimension(self, dimension="camera_motion", device="cuda:0", local_mode=False):
        """测试初始化单个维度"""
        print(f"🚀 测试初始化单个维度: {dimension}")
        try:
            data = {
                "dimensions": [dimension],
                "device": device,
                "local_mode": local_mode
            }
            response = self.session.post(
                f"{self.base_url}/initialize",
                json=data,
                timeout=300  # 初始化可能需要较长时间
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") in ["success", "partial"]:
                success_dims = result.get("initialized_dimensions", [])
                failed_dims = result.get("failed_dimensions", [])
                
                if dimension in success_dims:
                    print(f"✅ {dimension} 初始化成功")
                    return True
                else:
                    print(f"❌ {dimension} 初始化失败")
                    if failed_dims:
                        print(f"失败原因可能与以下维度相关: {failed_dims}")
                    return False
            else:
                print(f"❌ 初始化失败: {result.get('message', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def test_initialize_multiple_dimensions(self, dimensions=["camera_motion", "aesthetic_quality"], device="cuda:0", local_mode=False):
        """测试初始化多个维度"""
        print(f"🚀 测试初始化多个维度: {', '.join(dimensions)}")
        try:
            data = {
                "dimensions": dimensions,
                "device": device,
                "local_mode": local_mode
            }
            response = self.session.post(
                f"{self.base_url}/initialize",
                json=data,
                timeout=600  # 多维度初始化可能需要更长时间
            )
            response.raise_for_status()
            result = response.json()
            
            success_dims = result.get("initialized_dimensions", [])
            failed_dims = result.get("failed_dimensions", [])
            
            if success_dims:
                print(f"✅ 成功初始化 {len(success_dims)} 个维度: {', '.join(success_dims)}")
            
            if failed_dims:
                print(f"❌ 初始化失败 {len(failed_dims)} 个维度: {', '.join(failed_dims)}")
            
            return len(success_dims) > 0
            
        except Exception as e:
            print(f"❌ 多维度初始化失败: {e}")
            return False
    
    def test_evaluate_mock(self, dimensions=["camera_motion"]):
        """测试评测接口（模拟）"""
        print(f"📊 测试评测接口: {', '.join(dimensions)}")
        # 使用不存在的视频路径来测试接口逻辑
        test_video_paths = ["/test/fake_video1.mp4", "/test/fake_video2.mp4"]
        
        try:
            data = {
                "video_paths": test_video_paths,
                "dimensions": dimensions
            }
            response = self.session.post(
                f"{self.base_url}/evaluate",
                json=data,
                timeout=120
            )
            
            # 我们期望这里返回错误，因为文件不存在
            if response.status_code == 400:
                result = response.json()
                if "Video file not found" in result.get("message", ""):
                    print("✅ 评测接口响应正确（文件不存在错误）")
                    return True
            
            print(f"❌ 评测接口响应异常: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ 评测接口测试失败: {e}")
            return False
    
    def test_single_evaluate_mock(self, dimension="camera_motion"):
        """测试单维度评测接口（模拟）"""
        print(f"📊 测试单维度评测接口: {dimension}")
        test_video_path = "/test/fake_video.mp4"
        
        try:
            data = {
                "video_path": test_video_path,
                "dimension": dimension
            }
            response = self.session.post(
                f"{self.base_url}/evaluate_single",
                json=data,
                timeout=120
            )
            
            # 我们期望这里返回错误，因为文件不存在
            if response.status_code == 400:
                result = response.json()
                if "Video file not found" in result.get("message", ""):
                    print("✅ 单维度评测接口响应正确（文件不存在错误）")
                    return True
            
            print(f"❌ 单维度评测接口响应异常: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ 单维度评测接口测试失败: {e}")
            return False
    
    def test_invalid_dimension(self):
        """测试无效维度处理"""
        print("🚫 测试无效维度处理...")
        try:
            data = {
                "dimensions": ["invalid_dimension"],
                "device": "cuda:0"
            }
            response = self.session.post(
                f"{self.base_url}/initialize",
                json=data,
                timeout=30
            )
            
            if response.status_code == 400:
                result = response.json()
                if "不支持的评测维度" in result.get("message", ""):
                    print("✅ 无效维度处理正确")
                    return True
            
            print(f"❌ 无效维度处理异常: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ 无效维度处理测试失败: {e}")
            return False
    
    def run_basic_tests(self, device="cuda:0", local_mode=False):
        """运行基础测试"""
        print("=" * 60)
        print("🧪 VBench 多维度评测服务基础测试")
        print("=" * 60)
        
        tests = [
            ("健康检查", self.test_health_check),
            ("获取支持的维度", self.test_get_dimensions),
            ("无效维度处理", self.test_invalid_dimension),
        ]
        
        # 如果不是本地模式，添加初始化测试
        if not local_mode:
            tests.extend([
                ("初始化单个维度", lambda: self.test_initialize_single_dimension("camera_motion", device, local_mode)),
                ("评测接口测试", lambda: self.test_evaluate_mock(["camera_motion"])),
                ("单维度评测测试", lambda: self.test_single_evaluate_mock("camera_motion")),
            ])
        
        # 运行测试
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- 测试: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 通过")
                else:
                    print(f"❌ {test_name} 失败")
            except Exception as e:
                print(f"❌ {test_name} 异常: {e}")
            
            time.sleep(1)  # 短暂延迟
        
        # 总结
        print("\n" + "=" * 60)
        print(f"🎯 基础测试总结: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有基础测试通过！服务运行正常")
            return True
        else:
            print(f"⚠️  有 {total - passed} 个测试失败")
            return False
    
    def run_full_tests(self, device="cuda:0", local_mode=False, test_dimensions=None):
        """运行完整测试"""
        if test_dimensions is None:
            test_dimensions = ["camera_motion", "aesthetic_quality"]
        
        print("=" * 60)
        print("🧪 VBench 多维度评测服务完整测试")
        print("=" * 60)
        
        # 先运行基础测试
        if not self.run_basic_tests(device, local_mode):
            print("❌ 基础测试失败，跳过完整测试")
            return False
        
        if local_mode:
            print("\n📝 本地模式下跳过初始化和评测测试")
            return True
        
        print(f"\n🔧 开始完整功能测试...")
        print(f"📋 测试维度: {', '.join(test_dimensions)}")
        
        # 测试多维度初始化
        print(f"\n--- 测试: 多维度初始化 ---")
        if self.test_initialize_multiple_dimensions(test_dimensions, device, local_mode):
            print("✅ 多维度初始化通过")
        else:
            print("❌ 多维度初始化失败")
            return False
        
        # 测试多维度评测
        print(f"\n--- 测试: 多维度评测 ---")
        if self.test_evaluate_mock(test_dimensions):
            print("✅ 多维度评测通过")
        else:
            print("❌ 多维度评测失败")
        
        print("\n🎉 完整测试完成！")
        return True

def main():
    parser = argparse.ArgumentParser(description="VBench 多维度评测服务测试工具")
    parser.add_argument("--url", default="http://localhost:5001", help="服务地址")
    parser.add_argument("--device", default="cuda:0", help="GPU 设备")
    parser.add_argument("--local", action="store_true", help="本地模式")
    parser.add_argument("--basic", action="store_true", help="只运行基础测试")
    parser.add_argument("--dimensions", nargs="+", 
                       default=["camera_motion", "aesthetic_quality"],
                       help="测试的维度列表")
    
    args = parser.parse_args()
    
    tester = MultiDimensionTester(args.url)
    
    if args.basic:
        success = tester.run_basic_tests(args.device, args.local)
    else:
        success = tester.run_full_tests(args.device, args.local, args.dimensions)
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main() 