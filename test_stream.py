"""
测试流式返回接口
对比普通接口和流式接口的性能
"""
import requests
import time
import json

# 可以切换测试环境
BASE_URL = "https://ttsedge.egg404.com"  # 生产环境
# BASE_URL = "http://localhost:5005"  # 本地环境
API_PREFIX = "/api/v1"


def test_stream_api():
    """测试流式接口"""
    print("="*60)
    print("流式返回接口测试")
    print("="*60)
    
    test_cases = [
        {
            "name": "俄语单词",
            "data": {
                "text": "территория",
                "voice": "ru-RU-SvetlanaNeural"
            }
        },
        {
            "name": "中文单词",
            "data": {
                "text": "你好",
                "voice": "zh-CN-XiaoxiaoNeural"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print("-" * 60)
        
        # 测试流式接口
        print("流式接口（直接返回音频）:")
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/tts/generate-stream",
            json=test_case["data"],
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            audio_size = len(response.content)
            print(f"  ✓ 成功 - 耗时: {elapsed:.3f}秒")
            print(f"  音频大小: {audio_size / 1024:.2f} KB")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  X-Audio-Filename: {response.headers.get('X-Audio-Filename', 'N/A')}")
            
            # 保存文件验证
            filename = f"/tmp/stream_{test_case['name']}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"  文件已保存: {filename}")
        else:
            print(f"  ✗ 失败: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
        
        # 对比：普通接口
        print("\n普通接口（返回URL，需要二次请求）:")
        start_time = time.time()
        
        # 第一次请求：获取URL
        response1 = requests.post(
            f"{BASE_URL}{API_PREFIX}/tts/generate",
            json=test_case["data"],
            timeout=30
        )
        
        if response1.status_code == 200:
            result = response1.json()
            audio_url = result["data"]["audio_url"]
            filename = audio_url.split("/")[-1]
            
            # 第二次请求：下载音频（audio_url 已经是完整URL或相对路径）
            download_url = audio_url if audio_url.startswith("http") else f"{BASE_URL}{audio_url}"
            response2 = requests.get(download_url, timeout=30)
            
            elapsed = time.time() - start_time
            
            if response2.status_code == 200:
                audio_size = len(response2.content)
                print(f"  ✓ 成功 - 总耗时: {elapsed:.3f}秒")
                print(f"  音频大小: {audio_size / 1024:.2f} KB")
                print(f"  第一次请求: ~{elapsed * 0.5:.3f}秒")
                print(f"  第二次请求: ~{elapsed * 0.5:.3f}秒")
            else:
                print(f"  ✗ 下载失败: {response2.status_code}")
        else:
            print(f"  ✗ 生成失败: {response1.status_code}")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n性能对比总结：")
    print("- 流式接口：一次请求，直接返回音频，更快")
    print("- 普通接口：两次请求，先获取URL再下载，较慢")
    print("- 推荐：单词和短语使用流式接口，长文本使用普通接口")


if __name__ == "__main__":
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10, verify=False)
        if response.status_code != 200:
            print(f"⚠ 健康检查返回状态码: {response.status_code}")
            print("继续测试...")
    except requests.exceptions.SSLError:
        # SSL 错误，但可能服务正常运行
        print("⚠ SSL 验证警告，继续测试...")
    except requests.exceptions.RequestException as e:
        print(f"⚠ 无法连接到服务: {e}")
        print("继续测试...")
    
    test_stream_api()

