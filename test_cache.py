"""
测试缓存功能
验证相同内容的重复请求是否使用缓存
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def test_cache():
    """测试缓存功能"""
    print("="*60)
    print("缓存功能测试")
    print("="*60)
    
    # 测试数据
    test_cases = [
        {
            "name": "中文单词",
            "data": {
                "text": "你好",
                "voice": "zh-CN-XiaoxiaoNeural"
            }
        },
        {
            "name": "俄语单词",
            "data": {
                "text": "Привет",
                "voice": "ru-RU-SvetlanaNeural"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print("-" * 60)
        
        # 第一次请求（应该生成新文件）
        print("第一次请求（生成新文件）...")
        start_time = time.time()
        response1 = requests.post(
            f"{BASE_URL}{API_PREFIX}/tts/generate",
            json=test_case["data"],
            timeout=30
        )
        elapsed1 = time.time() - start_time
        
        if response1.status_code == 200:
            result1 = response1.json()
            filename1 = result1["data"]["audio_url"].split("/")[-1]
            print(f"  ✓ 成功 - 耗时: {elapsed1:.2f}秒")
            print(f"  文件名: {filename1}")
            print(f"  实际语速: {result1['data'].get('actual_rate', 'N/A')}")
        else:
            print(f"  ✗ 失败: {response1.status_code}")
            print(f"  响应: {response1.text[:200]}")
            continue
        
        # 等待一小段时间
        time.sleep(1)
        
        # 第二次请求（应该从缓存获取）
        print("\n第二次请求（应该从缓存获取）...")
        start_time = time.time()
        response2 = requests.post(
            f"{BASE_URL}{API_PREFIX}/tts/generate",
            json=test_case["data"],
            timeout=30
        )
        elapsed2 = time.time() - start_time
        
        if response2.status_code == 200:
            result2 = response2.json()
            filename2 = result2["data"]["audio_url"].split("/")[-1]
            print(f"  ✓ 成功 - 耗时: {elapsed2:.2f}秒")
            print(f"  文件名: {filename2}")
            print(f"  实际语速: {result2['data'].get('actual_rate', 'N/A')}")
            
            # 验证文件名是否相同（缓存应该返回相同的文件名）
            if filename1 == filename2:
                print(f"  ✓ 缓存生效：文件名相同")
            else:
                print(f"  ⚠ 警告：文件名不同，可能缓存未生效")
            
            # 验证响应时间（缓存应该更快）
            if elapsed2 < elapsed1 * 0.5:  # 缓存应该至少快50%
                print(f"  ✓ 缓存加速：第二次请求快 {((elapsed1 - elapsed2) / elapsed1 * 100):.1f}%")
            else:
                print(f"  ⚠ 警告：响应时间差异不明显")
        else:
            print(f"  ✗ 失败: {response2.status_code}")
            print(f"  响应: {response2.text[:200]}")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("✗ 服务未运行，请先启动服务：python run.py")
            exit(1)
    except requests.exceptions.RequestException:
        print("✗ 无法连接到服务，请先启动服务：python run.py")
        exit(1)
    
    test_cache()

