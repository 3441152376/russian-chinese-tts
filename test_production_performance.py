"""
生产环境性能测试脚本
测试优化后的流式接口性能
"""
import time
import requests
import statistics
from typing import List, Dict


# 测试配置
BASE_URL = "https://ttsedge.egg404.com"
API_PREFIX = "/api/v1"

# 测试用例
TEST_CASES = [
    {
        "name": "俄语句子（已缓存）",
        "data": {
            "text": "В университете студенты занимаются учением.",
            "voice": "ru-RU-SvetlanaNeural"
        },
        "expected_size_kb": 22.08
    },
    {
        "name": "俄语单词（已缓存）",
        "data": {
            "text": "территория",
            "voice": "ru-RU-SvetlanaNeural"
        },
        "expected_size_kb": 12.09
    }
]


def test_single_request(test_case: Dict, request_num: int = 1) -> Dict:
    """测试单个请求"""
    print(f"\n{'='*80}")
    print(f"测试 {request_num}: {test_case['name']}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
            json=test_case["data"],
            timeout=30
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            audio_size = len(response.content)
            audio_size_kb = audio_size / 1024
            
            # 获取响应头信息
            cache_hit = response.headers.get("X-Cache-Hit", "unknown")
            actual_rate = response.headers.get("X-Actual-Rate", "unknown")
            filename = response.headers.get("X-Audio-Filename", "unknown")
            
            # 计算传输速度
            transfer_speed_kbps = audio_size / elapsed_ms if elapsed_ms > 0 else 0
            
            result = {
                "success": True,
                "elapsed_ms": elapsed_ms,
                "audio_size_kb": audio_size_kb,
                "cache_hit": cache_hit,
                "actual_rate": actual_rate,
                "filename": filename,
                "transfer_speed_kbps": transfer_speed_kbps,
                "status_code": response.status_code
            }
            
            print(f"✓ 请求成功")
            print(f"  总耗时: {elapsed_ms:.2f}ms")
            print(f"  音频大小: {audio_size_kb:.2f}KB")
            print(f"  缓存命中: {cache_hit}")
            print(f"  实际语速: {actual_rate}")
            print(f"  文件名: {filename}")
            print(f"  传输速度: {transfer_speed_kbps:.2f}KB/s")
            print(f"  HTTP状态码: {response.status_code}")
            
            return result
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text[:200]
            }
            
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"✗ 请求异常: {str(e)}")
        print(f"  耗时: {elapsed_ms:.2f}ms")
        return {
            "success": False,
            "error": str(e),
            "elapsed_ms": elapsed_ms
        }


def test_multiple_requests(test_case: Dict, count: int = 5) -> List[Dict]:
    """测试多次请求（测试缓存效果）"""
    print(f"\n{'='*80}")
    print(f"多次请求测试: {test_case['name']} (共 {count} 次)")
    print(f"{'='*80}")
    
    results = []
    
    for i in range(count):
        print(f"\n--- 第 {i+1} 次请求 ---")
        result = test_single_request(test_case, i+1)
        results.append(result)
        
        # 如果不是最后一次，等待一下
        if i < count - 1:
            time.sleep(0.5)
    
    # 统计分析
    successful_results = [r for r in results if r.get("success", False)]
    
    if successful_results:
        elapsed_times = [r["elapsed_ms"] for r in successful_results]
        cache_hits = [r.get("cache_hit", "unknown") for r in successful_results]
        
        print(f"\n{'='*80}")
        print("统计分析:")
        print(f"{'='*80}")
        print(f"总请求数: {count}")
        print(f"成功请求数: {len(successful_results)}")
        print(f"失败请求数: {count - len(successful_results)}")
        
        if len(elapsed_times) > 0:
            print(f"\n耗时统计:")
            print(f"  平均耗时: {statistics.mean(elapsed_times):.2f}ms")
            print(f"  中位数耗时: {statistics.median(elapsed_times):.2f}ms")
            print(f"  最小耗时: {min(elapsed_times):.2f}ms")
            print(f"  最大耗时: {max(elapsed_times):.2f}ms")
            if len(elapsed_times) > 1:
                print(f"  标准差: {statistics.stdev(elapsed_times):.2f}ms")
            
            # 缓存命中分析
            cache_hit_count = sum(1 for h in cache_hits if h == "true")
            print(f"\n缓存分析:")
            print(f"  缓存命中次数: {cache_hit_count}/{len(successful_results)}")
            print(f"  缓存命中率: {cache_hit_count/len(successful_results)*100:.1f}%")
            
            # 首次 vs 后续请求对比
            if len(elapsed_times) >= 2:
                first_time = elapsed_times[0]
                avg_subsequent = statistics.mean(elapsed_times[1:])
                improvement = ((first_time - avg_subsequent) / first_time * 100) if first_time > 0 else 0
                print(f"\n性能对比:")
                print(f"  首次请求: {first_time:.2f}ms")
                print(f"  后续平均: {avg_subsequent:.2f}ms")
                print(f"  性能提升: {improvement:.1f}%")
    
    return results


def test_health_check():
    """测试健康检查接口"""
    print(f"\n{'='*80}")
    print("健康检查测试")
    print(f"{'='*80}")
    
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 健康检查成功")
            print(f"  耗时: {elapsed_ms:.2f}ms")
            print(f"  状态: {data.get('status', 'unknown')}")
            print(f"  应用名: {data.get('app_name', 'unknown')}")
            print(f"  版本: {data.get('version', 'unknown')}")
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"✗ 健康检查异常: {str(e)}")
        print(f"  耗时: {elapsed_ms:.2f}ms")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("生产环境性能测试")
    print("="*80)
    print(f"测试目标: {BASE_URL}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 健康检查
    test_health_check()
    
    # 测试每个用例
    all_results = []
    for test_case in TEST_CASES:
        results = test_multiple_requests(test_case, count=5)
        all_results.extend(results)
    
    # 总体统计
    print(f"\n{'='*80}")
    print("总体统计")
    print(f"{'='*80}")
    
    successful_results = [r for r in all_results if r.get("success", False)]
    if successful_results:
        elapsed_times = [r["elapsed_ms"] for r in successful_results]
        print(f"总请求数: {len(all_results)}")
        print(f"成功请求数: {len(successful_results)}")
        print(f"成功率: {len(successful_results)/len(all_results)*100:.1f}%")
        print(f"\n总体耗时统计:")
        print(f"  平均耗时: {statistics.mean(elapsed_times):.2f}ms")
        print(f"  中位数耗时: {statistics.median(elapsed_times):.2f}ms")
        print(f"  最小耗时: {min(elapsed_times):.2f}ms")
        print(f"  最大耗时: {max(elapsed_times):.2f}ms")
        
        # 性能评估
        print(f"\n性能评估:")
        avg_time = statistics.mean(elapsed_times)
        if avg_time < 100:
            print(f"  ✓ 优秀 (< 100ms)")
        elif avg_time < 500:
            print(f"  ✓ 良好 (< 500ms)")
        elif avg_time < 1000:
            print(f"  ⚠ 一般 (< 1000ms)")
        else:
            print(f"  ✗ 较慢 (> 1000ms)")
    
    print(f"\n{'='*80}")
    print("测试完成！")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

