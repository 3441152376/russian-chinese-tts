# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 运行服务

```bash
# 方式一：使用启动脚本
python run.py

# 方式二：直接运行主模块
python -m app.main

# 方式三：使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 3. 访问 API 文档

服务启动后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 4. 测试 API

### 使用 curl 测试

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 获取语音列表
curl "http://localhost:8000/api/v1/tts/voices?locale=zh-CN"

# 3. 生成语音
curl -X POST "http://localhost:8000/api/v1/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个测试",
    "voice": "zh-CN-XiaoxiaoNeural"
  }'

# 4. 下载音频（替换 {filename} 为实际文件名）
curl -O "http://localhost:8000/api/v1/tts/download/{filename}"
```

### 使用 Python 测试

```python
import requests

# 生成语音
response = requests.post(
    "http://localhost:8000/api/v1/tts/generate",
    json={
        "text": "你好，世界！",
        "voice": "zh-CN-XiaoxiaoNeural",
        "rate": "+0%",
        "volume": "+0%",
        "pitch": "+0Hz"
    }
)

result = response.json()
print(result)

# 下载音频
if result["code"] == 200:
    audio_url = result["data"]["audio_url"]
    audio_response = requests.get(f"http://localhost:8000{audio_url}")
    
    with open("output.mp3", "wb") as f:
        f.write(audio_response.content)
    
    print("音频文件已保存为 output.mp3")
```

## 5. 常用语音列表

### 中文语音

- `zh-CN-XiaoxiaoNeural` - 晓晓（女声，默认）
- `zh-CN-YunxiNeural` - 云希（男声）
- `zh-CN-YunyangNeural` - 云扬（男声）
- `zh-CN-XiaoyiNeural` - 晓伊（女声）
- `zh-CN-YunjianNeural` - 云健（男声）

### 英文语音

- `en-US-AriaNeural` - Aria（女声）
- `en-US-DavisNeural` - Davis（男声）
- `en-US-JennyNeural` - Jenny（女声）

## 6. 参数说明

### rate（语速）
- 范围：-50% 到 +50%
- 示例：`-50%`（慢速）、`+0%`（正常）、`+50%`（快速）

### volume（音量）
- 范围：-50% 到 +50%
- 示例：`-50%`（小声）、`+0%`（正常）、`+50%`（大声）

### pitch（音调）
- 范围：-50Hz 到 +50Hz
- 示例：`-50Hz`（低音）、`+0Hz`（正常）、`+50Hz`（高音）

## 7. 常见问题

### Q: 服务启动失败？
A: 检查端口是否被占用，或修改 `app/config/settings.py` 中的端口配置。

### Q: 生成的音频文件在哪里？
A: 默认保存在 `./output` 目录中。

### Q: 如何修改默认语音？
A: 在 `.env` 文件中设置 `DEFAULT_VOICE`，或在代码中修改 `app/config/settings.py`。

### Q: 支持哪些音频格式？
A: 目前默认生成 MP3 格式，可以通过修改代码支持其他格式。

## 8. 生产环境部署

### 使用 Gunicorn + Uvicorn Workers

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用 Docker（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t edge-tts-api .
docker run -p 8000:8000 edge-tts-api
```

