"""
TTS 测试脚本
测试中文和俄语的单词和长文本合成
"""
import asyncio
import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def print_response(title: str, response: requests.Response):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应: {response.text}")


def test_health_check():
    """测试健康检查"""
    print("\n[测试 1] 健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)
    return response.status_code == 200


def test_get_voices():
    """测试获取语音列表"""
    print("\n[测试 2] 获取中文和俄语语音列表")
    
    # 获取中文语音
    response_zh = requests.get(f"{BASE_URL}{API_PREFIX}/tts/voices?locale=zh-CN")
    print_response("中文语音列表", response_zh)
    
    # 获取俄语语音
    response_ru = requests.get(f"{BASE_URL}{API_PREFIX}/tts/voices?locale=ru-RU")
    print_response("俄语语音列表", response_ru)
    
    # 获取所有支持的语音
    response_all = requests.get(f"{BASE_URL}{API_PREFIX}/tts/voices")
    print_response("所有支持的语音（中文+俄语）", response_all)
    
    return response_zh.status_code == 200 and response_ru.status_code == 200


def test_chinese_word():
    """测试中文单词"""
    print("\n[测试 3] 中文单词合成")
    
    data = {
        "text": "你好",
        "voice": "zh-CN-XiaoxiaoNeural"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/tts/generate",
        json=data
    )
    print_response("中文单词合成", response)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 200:
            audio_url = result["data"]["audio_url"]
            download_audio(audio_url, "chinese_word.mp3")
            return True
    return False


def test_chinese_long_text():
    """测试中文长文本"""
    print("\n[测试 4] 中文长文本合成")
    
    long_text = """
    人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，
    应用领域也不断扩大。可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、
    思维的信息过程的模拟。人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。
    """
    
    data = {
        "text": long_text.strip(),
        "voice": "zh-CN-XiaoxiaoNeural"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/tts/generate",
        json=data
    )
    print_response("中文长文本合成", response)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 200:
            audio_url = result["data"]["audio_url"]
            download_audio(audio_url, "chinese_long_text.mp3")
            return True
    return False


def test_russian_word():
    """测试俄语单词"""
    print("\n[测试 5] 俄语单词合成")
    
    data = {
        "text": "Привет",
        "voice": "ru-RU-SvetlanaNeural"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/tts/generate",
        json=data
    )
    print_response("俄语单词合成", response)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 200:
            audio_url = result["data"]["audio_url"]
            download_audio(audio_url, "russian_word.mp3")
            return True
    return False


def test_russian_long_text():
    """测试俄语长文本"""
    print("\n[测试 6] 俄语长文本合成")
    
    long_text = """
    Искусственный интеллект — это раздел компьютерных наук, который пытается понять сущность интеллекта
    и создать новую интеллектуальную машину, способную реагировать способом, аналогичным человеческому интеллекту.
    Исследования в этой области включают робототехнику, распознавание речи, распознавание изображений,
    обработку естественного языка и экспертные системы. С момента своего появления искусственный интеллект
    стал все более зрелым в теории и технологиях, а область применения постоянно расширяется.
    """
    
    data = {
        "text": long_text.strip(),
        "voice": "ru-RU-SvetlanaNeural"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/tts/generate",
        json=data
    )
    print_response("俄语长文本合成", response)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 200:
            audio_url = result["data"]["audio_url"]
            download_audio(audio_url, "russian_long_text.mp3")
            return True
    return False


def download_audio(audio_url: str, filename: str):
    """下载音频文件"""
    try:
        full_url = f"{BASE_URL}{audio_url}"
        print(f"\n正在下载音频: {full_url}")
        response = requests.get(full_url)
        
        if response.status_code == 200:
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            
            file_path = output_dir / filename
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            file_size = file_path.stat().st_size / 1024  # KB
            print(f"✓ 音频已保存: {file_path} ({file_size:.2f} KB)")
            return True
        else:
            print(f"✗ 下载失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 下载失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("Edge TTS API 测试")
    print("="*60)
    print(f"测试服务器: {BASE_URL}")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n✗ 服务未正常运行，请先启动服务：")
            print("  python run.py")
            return
    except requests.exceptions.RequestException:
        print("\n✗ 无法连接到服务，请先启动服务：")
        print("  python run.py")
        return
    
    print("\n✓ 服务连接正常，开始测试...")
    
    # 执行测试
    tests = [
        ("健康检查", test_health_check),
        ("获取语音列表", test_get_voices),
        ("中文单词合成", test_chinese_word),
        ("中文长文本合成", test_chinese_long_text),
        ("俄语单词合成", test_russian_word),
        ("俄语长文本合成", test_russian_long_text),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 测试出错: {str(e)}")
            results.append((name, False))
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()

