# Edge TTS 后端服务

基于 FastAPI 和 edge-tts 的文本转语音 RESTful API 服务。

## 功能特性

- ✅ 文本转语音（TTS）功能
- ✅ 支持多种语音和语言
- ✅ 可调节语速、音量、音调
- ✅ 获取可用语音列表
- ✅ 文件下载和管理
- ✅ RESTful API 设计
- ✅ 完整的错误处理
- ✅ 日志记录
- ✅ API 文档（Swagger/ReDoc）

## 技术栈

- **FastAPI**: 现代、高性能的 Python Web 框架
- **edge-tts**: Microsoft Edge 文本转语音服务
- **Pydantic**: 数据验证和设置管理
- **Loguru**: 日志管理
- **Uvicorn**: ASGI 服务器

## 项目结构

```
edge/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── config/                 # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── controllers/            # 控制器层
│   │   ├── __init__.py
│   │   └── tts_controller.py
│   ├── services/               # 服务层
│   │   ├── __init__.py
│   │   └── tts_service.py
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── request_models.py
│   │   └── response_models.py
│   └── utils/                  # 工具类
│       ├── __init__.py
│       ├── logger.py
│       └── file_utils.py
├── output/                     # 音频文件输出目录
├── logs/                       # 日志文件目录
├── requirements.txt            # 依赖包
├── .gitignore
└── README.md
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件：

```env
APP_NAME=Edge TTS API
DEBUG=false
HOST=0.0.0.0
PORT=8000
API_PREFIX=/api/v1
OUTPUT_DIR=./output
MAX_TEXT_LENGTH=5000
DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
```

### 3. 运行服务

```bash
# 方式一：直接运行
python -m app.main

# 方式二：使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 1. 生成语音

**POST** `/api/v1/tts/generate`

请求体：
```json
{
  "text": "你好，世界！",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+0%",
  "volume": "+0%",
  "pitch": "+0Hz"
}
```

响应：
```json
{
  "code": 200,
  "message": "语音生成成功",
  "data": {
    "audio_url": "/api/v1/tts/download/xxx.mp3",
    "text": "你好，世界！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "duration": null
  }
}
```

### 2. 下载音频文件

**GET** `/api/v1/tts/download/{filename}`

### 3. 获取语音列表

**GET** `/api/v1/tts/voices?locale=zh-CN&gender=Female`

响应：
```json
{
  "code": 200,
  "message": "获取语音列表成功",
  "data": {
    "total": 10,
    "voices": [
      {
        "name": "zh-CN-XiaoxiaoNeural",
        "gender": "Female",
        "locale": "zh-CN",
        "friendly_name": "Xiaoxiao"
      }
    ]
  }
}
```

### 4. 删除音频文件

**DELETE** `/api/v1/tts/file/{filename}`

### 5. 健康检查

**GET** `/health`

## 使用示例

### Python 示例

```python
import requests

# 生成语音
response = requests.post(
    "http://localhost:8000/api/v1/tts/generate",
    json={
        "text": "你好，这是一个测试",
        "voice": "zh-CN-XiaoxiaoNeural"
    }
)
result = response.json()
audio_url = result["data"]["audio_url"]

# 下载音频
audio_response = requests.get(f"http://localhost:8000{audio_url}")
with open("output.mp3", "wb") as f:
    f.write(audio_response.content)
```

### cURL 示例

```bash
# 生成语音
curl -X POST "http://localhost:8000/api/v1/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界！",
    "voice": "zh-CN-XiaoxiaoNeural"
  }'

# 获取语音列表
curl "http://localhost:8000/api/v1/tts/voices?locale=zh-CN"
```

## 配置说明

主要配置项在 `app/config/settings.py` 中：

- `max_text_length`: 最大文本长度（默认 5000）
- `default_voice`: 默认语音（默认 zh-CN-XiaoxiaoNeural）
- `output_dir`: 音频文件输出目录
- `max_file_size_mb`: 最大文件大小（MB）

## 注意事项

1. 首次运行会自动创建 `output` 和 `logs` 目录
2. 生成的音频文件会保存在 `output` 目录中
3. 建议定期清理 `output` 目录中的旧文件
4. 生产环境请修改 CORS 配置，限制允许的域名

## 许可证

MIT License

