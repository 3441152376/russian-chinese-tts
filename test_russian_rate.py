"""
测试俄语语速优化
对比不同语速设置的效果
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def test_russian_with_different_rates():
    """测试不同语速设置的俄语合成"""
    
    # 测试文本：一个较长的俄语句子
    test_text = "Искусственный интеллект — это раздел компьютерных наук, который пытается понять сущность интеллекта и создать новую интеллектуальную машину, способную реагировать способом, аналогичным человеческому интеллекту."
    
    print("="*60)
    print("俄语语速测试")
    print("="*60)
    print(f"测试文本长度: {len(test_text)} 字符")
    print(f"测试文本: {test_text[:80]}...")
    print()
    
    # 测试不同的语速设置
    test_cases = [
        ("默认语速（自动优化）", None),
        ("正常语速", "+0%"),
        ("降低20%", "-20%"),
        ("降低30%", "-30%"),
        ("降低40%", "-40%"),
    ]
    
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    for name, rate in test_cases:
        print(f"\n测试: {name}")
        print("-" * 60)
        
        data = {
            "text": test_text,
            "voice": "ru-RU-SvetlanaNeural"
        }
        
        if rate is not None:
            data["rate"] = rate
        
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/tts/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    audio_url = result["data"]["audio_url"]
                    actual_rate = result["data"].get("voice", "N/A")
                    
                    # 下载音频
                    audio_response = requests.get(f"{BASE_URL}{audio_url}")
                    if audio_response.status_code == 200:
                        filename = f"russian_test_{name.replace('（', '_').replace('）', '').replace(' ', '_')}.mp3"
                        file_path = output_dir / filename
                        with open(file_path, "wb") as f:
                            f.write(audio_response.content)
                        
                        file_size = file_path.stat().st_size / 1024
                        print(f"✓ 成功生成: {filename} ({file_size:.2f} KB)")
                        print(f"  使用的语速: {result['data'].get('voice', 'N/A')}")
                    else:
                        print(f"✗ 下载失败: {audio_response.status_code}")
                else:
                    print(f"✗ 生成失败: {result.get('message', 'Unknown error')}")
            else:
                print(f"✗ 请求失败: {response.status_code}")
                print(f"  响应: {response.text[:200]}")
        except Exception as e:
            print(f"✗ 错误: {str(e)}")
    
    print("\n" + "="*60)
    print("测试完成！请播放生成的音频文件对比效果。")
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
    
    test_russian_with_different_rates()

