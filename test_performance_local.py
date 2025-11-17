"""
本地性能测试脚本
测试服务器端代码的性能，不依赖网络
"""
import time
import asyncio
from pathlib import Path
from app.config import settings
from app.services import TTSService
from app.utils import (
    generate_cache_key,
    check_cache_exists,
    get_cache_path,
    get_cache_filename,
    app_logger
)


async def test_service_performance():
    """测试服务层的性能"""
    print("=" * 80)
    print("测试: TTS 服务层性能")
    print("=" * 80)
    
    service = TTSService()
    
    test_cases = [
        {
            "name": "俄语句子",
            "text": "В университете студенты занимаются учением.",
            "voice": "ru-RU-SvetlanaNeural",
            "rate": None
        },
        {
            "name": "俄语单词",
            "text": "территория",
            "voice": "ru-RU-SvetlanaNeural",
            "rate": None
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print("-" * 80)
        
        # 第一次调用（可能生成或从缓存获取）
        print("第一次调用:")
        start = time.time()
        try:
            filename, file_path, actual_rate, is_cached = await service.text_to_speech(
                text=test_case["text"],
                voice=test_case["voice"],
                rate=test_case["rate"]
            )
            elapsed = (time.time() - start) * 1000
            
            file_size = file_path.stat().st_size
            print(f"  ✓ 成功 - 耗时: {elapsed:.2f}ms")
            print(f"  文件名: {filename}")
            print(f"  文件大小: {file_size / 1024:.2f}KB")
            print(f"  缓存命中: {is_cached}")
            print(f"  实际语速: {actual_rate}")
        except Exception as e:
            print(f"  ✗ 失败: {str(e)}")
            continue
        
        # 等待一下
        await asyncio.sleep(0.1)
        
        # 第二次调用（应该命中缓存）
        print("\n第二次调用（应该命中缓存）:")
        start = time.time()
        try:
            filename2, file_path2, actual_rate2, is_cached2 = await service.text_to_speech(
                text=test_case["text"],
                voice=test_case["voice"],
                rate=test_case["rate"]
            )
            elapsed2 = (time.time() - start) * 1000
            
            file_size2 = file_path2.stat().st_size
            print(f"  ✓ 成功 - 耗时: {elapsed2:.2f}ms")
            print(f"  文件名: {filename2}")
            print(f"  文件大小: {file_size2 / 1024:.2f}KB")
            print(f"  缓存命中: {is_cached2}")
            
            if elapsed > 0:
                improvement = ((elapsed - elapsed2) / elapsed) * 100
                print(f"  性能提升: {improvement:.1f}%")
        except Exception as e:
            print(f"  ✗ 失败: {str(e)}")
        
        print()


def test_cache_operations():
    """测试缓存操作性能"""
    print("=" * 80)
    print("测试: 缓存操作性能")
    print("=" * 80)
    
    test_text = "В университете студенты занимаются учением."
    test_voice = "ru-RU-SvetlanaNeural"
    
    # 测试缓存键生成
    print("1. 缓存键生成:")
    times = []
    for _ in range(1000):
        start = time.time()
        cache_key = generate_cache_key(
            text=test_text,
            voice=test_voice,
            rate=settings.russian_sentence_rate,
            volume=settings.default_volume,
            pitch=settings.default_pitch
        )
        times.append((time.time() - start) * 1000)
    avg_time = sum(times) / len(times)
    print(f"  平均耗时: {avg_time:.4f}ms (1000次)")
    print(f"  缓存键: {cache_key}")
    
    # 测试缓存检查
    print("\n2. 缓存检查:")
    times = []
    for _ in range(1000):
        start = time.time()
        cached_file = check_cache_exists(cache_key, ".mp3")
        times.append((time.time() - start) * 1000)
    avg_time = sum(times) / len(times)
    print(f"  平均耗时: {avg_time:.4f}ms (1000次)")
    print(f"  缓存存在: {cached_file is not None}")
    
    # 测试文件读取
    if cached_file and cached_file.exists():
        print("\n3. 文件读取:")
        file_size = cached_file.stat().st_size
        print(f"  文件大小: {file_size / 1024:.2f}KB")
        
        # 同步读取
        times = []
        for _ in range(100):
            start = time.time()
            with open(cached_file, 'rb') as f:
                data = f.read()
            times.append((time.time() - start) * 1000)
        avg_time = sum(times) / len(times)
        print(f"  同步读取平均耗时: {avg_time:.4f}ms (100次)")
        print(f"  读取速度: {file_size / avg_time / 1024:.2f}MB/s")
    
    print()


def test_file_path_operations():
    """测试文件路径操作性能"""
    print("=" * 80)
    print("测试: 文件路径操作性能")
    print("=" * 80)
    
    cache_key = "3778a618ec53bcf67f8a4bda22216dc8"
    
    # 测试路径生成
    print("1. 路径生成:")
    times = []
    for _ in range(10000):
        start = time.time()
        path = get_cache_path(cache_key, ".mp3")
        times.append((time.time() - start) * 1000)
    avg_time = sum(times) / len(times)
    print(f"  平均耗时: {avg_time:.4f}ms (10000次)")
    
    # 测试文件名生成
    print("\n2. 文件名生成:")
    times = []
    for _ in range(10000):
        start = time.time()
        filename = get_cache_filename(cache_key, ".mp3")
        times.append((time.time() - start) * 1000)
    avg_time = sum(times) / len(times)
    print(f"  平均耗时: {avg_time:.4f}ms (10000次)")
    
    print()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("本地性能测试（服务器端代码）")
    print("=" * 80)
    print(f"缓存目录: {settings.cache_dir}")
    print()
    
    # 运行测试
    test_cache_operations()
    test_file_path_operations()
    await test_service_performance()
    
    print("=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

