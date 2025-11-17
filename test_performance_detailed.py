"""
详细的性能测试脚本
用于诊断流式接口的性能瓶颈
"""
import time
import requests
import hashlib
from pathlib import Path
from app.config import settings
from app.utils import (
    generate_cache_key,
    check_cache_exists,
    get_cache_path,
    get_cache_filename
)

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
        }
    },
    {
        "name": "俄语单词（已缓存）",
        "data": {
            "text": "территория",
            "voice": "ru-RU-SvetlanaNeural"
        }
    }
]


def test_cache_check_performance():
    """测试缓存检查的性能"""
    print("=" * 80)
    print("测试1: 缓存检查性能")
    print("=" * 80)
    
    test_text = "В университете студенты занимаются учением."
    test_voice = "ru-RU-SvetlanaNeural"
    
    # 生成缓存键
    start = time.time()
    cache_key = generate_cache_key(
        text=test_text,
        voice=test_voice,
        rate=settings.russian_sentence_rate,
        volume=settings.default_volume,
        pitch=settings.default_pitch
    )
    key_gen_time = (time.time() - start) * 1000
    print(f"✓ 缓存键生成耗时: {key_gen_time:.3f}ms")
    print(f"  缓存键: {cache_key}")
    
    # 检查缓存是否存在
    start = time.time()
    cached_file = check_cache_exists(cache_key, ".mp3")
    check_time = (time.time() - start) * 1000
    print(f"✓ 缓存检查耗时: {check_time:.3f}ms")
    
    if cached_file:
        print(f"✓ 缓存文件存在: {cached_file}")
        
        # 测试文件读取性能
        print("\n测试文件读取性能:")
        file_size = cached_file.stat().st_size
        print(f"  文件大小: {file_size / 1024:.2f}KB")
        
        # 测试一次性读取
        start = time.time()
        with open(cached_file, 'rb') as f:
            data = f.read()
        read_time = (time.time() - start) * 1000
        print(f"✓ 同步读取耗时: {read_time:.3f}ms")
        print(f"  读取速度: {file_size / read_time / 1024:.2f}MB/s")
        
        # 测试文件 stat 操作
        start = time.time()
        for _ in range(100):
            cached_file.stat()
        stat_time = (time.time() - start) / 100 * 1000
        print(f"✓ 文件 stat 操作耗时: {stat_time:.3f}ms (100次平均)")
    else:
        print("✗ 缓存文件不存在")
    
    print()


def test_file_system_operations():
    """测试文件系统操作性能"""
    print("=" * 80)
    print("测试2: 文件系统操作性能")
    print("=" * 80)
    
    cache_dir = Path(settings.cache_dir)
    if not cache_dir.exists():
        print("✗ 缓存目录不存在")
        return
    
    # 统计缓存文件数量
    cache_files = list(cache_dir.glob("*.mp3"))
    print(f"✓ 缓存文件数量: {len(cache_files)}")
    
    if cache_files:
        # 测试遍历文件
        start = time.time()
        for _ in range(10):
            list(cache_dir.glob("*.mp3"))
        glob_time = (time.time() - start) / 10 * 1000
        print(f"✓ glob 操作耗时: {glob_time:.3f}ms (10次平均)")
        
        # 测试文件存在性检查
        test_file = cache_files[0]
        start = time.time()
        for _ in range(1000):
            test_file.exists()
        exists_time = (time.time() - start) / 1000 * 1000
        print(f"✓ exists() 操作耗时: {exists_time:.3f}ms (1000次平均)")
        
        # 测试路径操作
        start = time.time()
        for _ in range(10000):
            cache_dir / f"{hashlib.md5(str(_).encode()).hexdigest()}.mp3"
        path_time = (time.time() - start) / 10000 * 1000
        print(f"✓ 路径拼接耗时: {path_time:.3f}ms (10000次平均)")
    
    print()


def test_api_performance():
    """测试 API 接口性能"""
    print("=" * 80)
    print("测试3: API 接口性能（流式接口）")
    print("=" * 80)
    
    for test_case in TEST_CASES:
        print(f"\n测试: {test_case['name']}")
        print("-" * 80)
        
        # 第一次请求（确保缓存存在）
        print("第一次请求（确保缓存）:")
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
                json=test_case["data"],
                timeout=30
            )
            first_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                audio_size = len(response.content)
                cache_hit = response.headers.get("X-Cache-Hit", "unknown")
                print(f"  ✓ 成功 - 耗时: {first_time:.2f}ms")
                print(f"  音频大小: {audio_size / 1024:.2f}KB")
                print(f"  缓存命中: {cache_hit}")
                print(f"  HTTP状态码: {response.status_code}")
            else:
                print(f"  ✗ 失败: {response.status_code}")
                print(f"  响应: {response.text[:200]}")
                continue
        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")
            continue
        
        # 等待一下，确保请求完成
        time.sleep(0.5)
        
        # 第二次请求（应该命中缓存）
        print("\n第二次请求（缓存命中）:")
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
                json=test_case["data"],
                timeout=30
            )
            second_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                audio_size = len(response.content)
                cache_hit = response.headers.get("X-Cache-Hit", "unknown")
                print(f"  ✓ 成功 - 耗时: {second_time:.2f}ms")
                print(f"  音频大小: {audio_size / 1024:.2f}KB")
                print(f"  缓存命中: {cache_hit}")
                print(f"  HTTP状态码: {response.status_code}")
                
                # 性能对比
                if first_time > 0:
                    improvement = ((first_time - second_time) / first_time) * 100
                    print(f"  性能提升: {improvement:.1f}%")
            else:
                print(f"  ✗ 失败: {response.status_code}")
                print(f"  响应: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")
        
        # 第三次请求（连续请求，测试稳定性）
        print("\n第三次请求（连续请求）:")
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
                json=test_case["data"],
                timeout=30
            )
            third_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                audio_size = len(response.content)
                cache_hit = response.headers.get("X-Cache-Hit", "unknown")
                print(f"  ✓ 成功 - 耗时: {third_time:.2f}ms")
                print(f"  音频大小: {audio_size / 1024:.2f}KB")
                print(f"  缓存命中: {cache_hit}")
            else:
                print(f"  ✗ 失败: {response.status_code}")
        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")
        
        print()


def test_network_breakdown():
    """测试网络请求的各个阶段耗时"""
    print("=" * 80)
    print("测试4: 网络请求阶段分析")
    print("=" * 80)
    
    test_data = {
        "text": "территория",
        "voice": "ru-RU-SvetlanaNeural"
    }
    
    # 使用 requests 的详细时间追踪
    print("测试请求各阶段耗时:")
    start = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
            json=test_data,
            timeout=30
        )
        total_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            print(f"✓ 总耗时: {total_time:.2f}ms")
            print(f"  音频大小: {len(response.content) / 1024:.2f}KB")
            print(f"  缓存命中: {response.headers.get('X-Cache-Hit', 'unknown')}")
            
            # 计算传输速度
            transfer_speed = len(response.content) / total_time / 1024  # KB/ms -> MB/s
            print(f"  传输速度: {transfer_speed * 1000:.2f}KB/s")
        else:
            print(f"✗ 失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
    
    print()


def test_concurrent_requests():
    """测试并发请求性能"""
    print("=" * 80)
    print("测试5: 并发请求性能")
    print("=" * 80)
    
    import concurrent.futures
    
    test_data = {
        "text": "территория",
        "voice": "ru-RU-SvetlanaNeural"
    }
    
    def make_request(index):
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
                json=test_data,
                timeout=30
            )
            elapsed = (time.time() - start) * 1000
            return {
                "index": index,
                "success": response.status_code == 200,
                "time": elapsed,
                "size": len(response.content) if response.status_code == 200 else 0,
                "cache_hit": response.headers.get("X-Cache-Hit", "unknown") if response.status_code == 200 else "unknown"
            }
        except Exception as e:
            return {
                "index": index,
                "success": False,
                "error": str(e),
                "time": (time.time() - start) * 1000
            }
    
    # 并发5个请求
    print("并发5个请求:")
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    total_time = (time.time() - start) * 1000
    
    success_count = sum(1 for r in results if r.get("success", False))
    avg_time = sum(r["time"] for r in results) / len(results)
    max_time = max(r["time"] for r in results)
    min_time = min(r["time"] for r in results)
    
    print(f"✓ 总耗时: {total_time:.2f}ms")
    print(f"  成功: {success_count}/5")
    print(f"  平均耗时: {avg_time:.2f}ms")
    print(f"  最大耗时: {max_time:.2f}ms")
    print(f"  最小耗时: {min_time:.2f}ms")
    
    for r in results:
        if r.get("success"):
            print(f"  请求{r['index']}: {r['time']:.2f}ms, 缓存: {r['cache_hit']}, 大小: {r['size']/1024:.2f}KB")
        else:
            print(f"  请求{r['index']}: 失败 - {r.get('error', 'unknown')}")
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("Edge TTS API 性能诊断测试")
    print("=" * 80)
    print(f"测试目标: {BASE_URL}")
    print(f"缓存目录: {settings.cache_dir}")
    print()
    
    # 运行所有测试
    test_cache_check_performance()
    test_file_system_operations()
    test_api_performance()
    test_network_breakdown()
    test_concurrent_requests()
    
    print("=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()

