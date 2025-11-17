# Edge TTS API 前端对接文档

## 基础信息

- **API 地址**: `https://ttsedge.egg404.com`
- **API 版本**: `v1`
- **API 前缀**: `/api/v1`
- **协议**: HTTPS
- **数据格式**: JSON

## 快速开始

### 1. 基础 URL

```javascript
const API_BASE_URL = 'https://ttsedge.egg404.com/api/v1';
```

### 2. 请求头

所有请求需要设置以下请求头：

```javascript
{
  'Content-Type': 'application/json'
}
```

## API 接口

### 1. 健康检查

**接口**: `GET /health`

**说明**: 检查服务是否正常运行

**请求示例**:

```javascript
fetch('https://ttsedge.egg404.com/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

**响应示例**:

```json
{
  "status": "healthy",
  "app_name": "Edge TTS API",
  "version": "1.0.0"
}
```

---

### 2. 获取语音列表

**接口**: `GET /api/v1/tts/voices`

**说明**: 获取可用的语音列表（仅支持中文和俄语）

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| locale | string | 否 | 语言区域过滤，例如：`zh-CN` 或 `ru-RU` |
| gender | string | 否 | 性别过滤：`Male` 或 `Female` |

**请求示例**:

```javascript
// 获取所有语音
fetch('https://ttsedge.egg404.com/api/v1/tts/voices')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取中文语音
fetch('https://ttsedge.egg404.com/api/v1/tts/voices?locale=zh-CN')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取俄语女声
fetch('https://ttsedge.egg404.com/api/v1/tts/voices?locale=ru-RU&gender=Female')
  .then(response => response.json())
  .then(data => console.log(data));
```

**响应示例**:

```json
{
  "code": 200,
  "message": "获取语音列表成功",
  "data": {
    "total": 36,
    "voices": [
      {
        "name": "zh-CN-XiaoxiaoNeural",
        "gender": "Female",
        "locale": "zh-CN",
        "friendly_name": ""
      },
      {
        "name": "zh-CN-YunxiNeural",
        "gender": "Male",
        "locale": "zh-CN",
        "friendly_name": ""
      }
    ]
  }
}
```

---

### 3. 生成语音

**接口**: `POST /api/v1/tts/generate`

**说明**: 将文本转换为语音文件

**请求参数**:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| text | string | 是 | 要转换的文本内容（1-5000字符） | `"你好，世界！"` |
| voice | string | 否 | 语音名称 | `"zh-CN-XiaoxiaoNeural"` |
| rate | string | 否 | 语速（-50% 到 +50%） | `"+0%"`、`"-30%"` |
| volume | string | 否 | 音量（-50% 到 +50%） | `"+0%"` |
| pitch | string | 否 | 音调（-50Hz 到 +50Hz） | `"+0Hz"` |
| return_audio | boolean | 否 | 是否直接在响应中返回音频数据（base64编码），适用于小文件快速播放 | `false` |

**注意**: 
- 如果不指定 `voice`，将使用默认语音（中文：`zh-CN-XiaoxiaoNeural`）
- 俄语长文本（超过50字符）会自动降低语速至 `-30%`，除非用户明确指定语速
- **性能优化**：设置 `return_audio: true` 可以直接在响应中获取音频数据，避免二次请求，特别适合单词和短语的快速播放

**请求示例**:

```javascript
// 基础请求
const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: '你好，世界！',
    voice: 'zh-CN-XiaoxiaoNeural'
  })
});

const result = await response.json();
console.log(result);
```

**响应示例**:

```json
{
  "code": 200,
  "message": "语音生成成功",
  "data": {
    "audio_url": "https://ttsedge.egg404.com/api/v1/tts/download/bbe9f5e0e0e41d188ef351e7f8292087.mp3",
    "text": "你好，世界！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "duration": null,
    "actual_rate": "+0%",
    "audio_data": "base64编码的音频数据（仅在 return_audio=true 时返回）"
  }
}
```

**性能优化示例**（直接返回音频数据，避免二次请求）：

```javascript
// 设置 return_audio: true，直接在响应中获取音频数据
const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'территория',
    voice: 'ru-RU-SvetlanaNeural',
    return_audio: true  // 直接返回音频数据
  })
});

const result = await response.json();

if (result.code === 200 && result.data.audio_data) {
  // 直接使用 base64 数据播放，无需二次请求
  const audioData = result.data.audio_data;
  const audioBlob = base64ToBlob(audioData, 'audio/mpeg');
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
  
  // base64 转 Blob 的辅助函数
  function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }
}
```

---

### 4. 流式生成语音（推荐用于单词和短语）

**接口**: `POST /api/v1/tts/generate-stream`

**说明**: 直接返回音频流，一次请求完成，适合快速播放单词和短语。比普通接口更快，因为避免了二次请求。

**请求参数**: 与 `/api/v1/tts/generate` 相同

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| text | string | 是 | 要转换的文本内容（1-5000字符） | `"你好"` |
| voice | string | 否 | 语音名称 | `"zh-CN-XiaoxiaoNeural"` |
| rate | string | 否 | 语速（-50% 到 +50%） | `"+0%"` |
| volume | string | 否 | 音量（-50% 到 +50%） | `"+0%"` |
| pitch | string | 否 | 音调（-50Hz 到 +50Hz） | `"+0Hz"` |

**响应**: 直接返回音频流（`audio/mpeg`），响应头包含：
- `Content-Type: audio/mpeg`
- `Content-Disposition: attachment; filename="{filename}"`
- `X-Audio-Filename`: 音频文件名
- `X-Actual-Rate`: 实际使用的语速

**请求示例**:

```javascript
// 方式一：使用 fetch 获取音频流
const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate-stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: '你好',
    voice: 'zh-CN-XiaoxiaoNeural'
  })
});

// 获取音频 Blob
const audioBlob = await response.blob();
const audioUrl = window.URL.createObjectURL(audioBlob);

// 播放音频
const audio = new Audio(audioUrl);
audio.play();

// 或者直接使用响应 URL
const audio2 = new Audio(audioUrl);
audio2.play();
```

**性能对比**:
- **流式接口** (`/generate-stream`): 一次请求，直接返回音频，耗时约 0.01-0.07 秒（缓存命中）
- **普通接口** (`/generate`): 两次请求（先获取URL，再下载），总耗时约 1.5-3.2 秒

**使用建议**:
- ✅ **单词和短语**（< 100字符）：使用流式接口，快速播放
- ✅ **长文本**（> 100字符）：使用普通接口，可以获取更多元数据（如 duration）

**完整示例**:

```javascript
/**
 * 流式生成语音（推荐用于单词和短语）
 */
async function generateSpeechStream(text, voice = 'zh-CN-XiaoxiaoNeural') {
  try {
    const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate-stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text, voice })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 获取音频 Blob
    const audioBlob = await response.blob();
    const audioUrl = window.URL.createObjectURL(audioBlob);
    
    // 获取文件名（从响应头）
    const filename = response.headers.get('X-Audio-Filename') || 'audio.mp3';
    const actualRate = response.headers.get('X-Actual-Rate') || '+0%';

    return {
      audioUrl,
      filename,
      actualRate,
      blob: audioBlob
    };
  } catch (error) {
    console.error('生成语音失败:', error);
    throw error;
  }
}

// 使用示例
const result = await generateSpeechStream('你好', 'zh-CN-XiaoxiaoNeural');
const audio = new Audio(result.audioUrl);
audio.play();
```

---

### 5. 下载音频文件

**接口**: `GET /api/v1/tts/download/{filename}`

**说明**: 下载生成的音频文件

**请求参数**:

| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| filename | string | URL路径 | 音频文件名（从生成接口返回的 audio_url 中获取） |

**请求示例**:

```javascript
// 方式一：直接使用返回的 audio_url
const audioUrl = result.data.audio_url;
const audioResponse = await fetch(audioUrl);
const audioBlob = await audioResponse.blob();

// 创建下载链接
const url = window.URL.createObjectURL(audioBlob);
const a = document.createElement('a');
a.href = url;
a.download = 'audio.mp3';
a.click();

// 方式二：使用 Audio 元素播放
const audio = new Audio(audioUrl);
audio.play();
```

---

### 5. 删除音频文件

**接口**: `DELETE /api/v1/tts/file/{filename}`

**说明**: 删除音频文件（通常不需要调用，系统会自动管理）

**请求示例**:

```javascript
const filename = 'bbe9f5e0e0e41d188ef351e7f8292087.mp3';
const response = await fetch(
  `https://ttsedge.egg404.com/api/v1/tts/file/${filename}`,
  {
    method: 'DELETE'
  }
);

const result = await response.json();
console.log(result);
```

---

## 完整示例代码

### JavaScript (原生)

```javascript
class TTSClient {
  constructor(baseUrl = 'https://ttsedge.egg404.com/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * 获取语音列表
   */
  async getVoices(locale = null, gender = null) {
    const params = new URLSearchParams();
    if (locale) params.append('locale', locale);
    if (gender) params.append('gender', gender);
    
    const url = `${this.baseUrl}/tts/voices${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    return await response.json();
  }

  /**
   * 生成语音
   */
  async generateSpeech(text, options = {}) {
    const {
      voice = null,
      rate = null,
      volume = null,
      pitch = null
    } = options;

    const response = await fetch(`${this.baseUrl}/tts/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        voice,
        rate,
        volume,
        pitch
      })
    });

    return await response.json();
  }

  /**
   * 下载并播放音频
   */
  async playAudio(audioUrl) {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      audio.onended = () => resolve();
      audio.onerror = (error) => reject(error);
      audio.play();
    });
  }

  /**
   * 下载音频文件
   */
  async downloadAudio(audioUrl, filename = 'audio.mp3') {
    const response = await fetch(audioUrl);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
}

// 使用示例
const tts = new TTSClient();

// 获取中文语音列表
tts.getVoices('zh-CN').then(result => {
  console.log('中文语音:', result.data.voices);
});

// 生成并播放语音
tts.generateSpeech('你好，世界！', {
  voice: 'zh-CN-XiaoxiaoNeural'
}).then(result => {
  if (result.code === 200) {
    console.log('音频URL:', result.data.audio_url);
    // 播放音频
    tts.playAudio(result.data.audio_url);
    // 或下载音频
    // tts.downloadAudio(result.data.audio_url, 'hello.mp3');
  }
});
```

### TypeScript

```typescript
interface VoiceInfo {
  name: string;
  gender: string;
  locale: string;
  friendly_name?: string;
}

interface VoiceListResponse {
  code: number;
  message: string;
  data: {
    total: number;
    voices: VoiceInfo[];
  };
}

interface TTSRequest {
  text: string;
  voice?: string;
  rate?: string;
  volume?: string;
  pitch?: string;
}

interface TTSResponse {
  code: number;
  message: string;
  data: {
    audio_url: string;
    text: string;
    voice: string;
    duration: number | null;
    actual_rate: string;
  };
}

class TTSClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'https://ttsedge.egg404.com/api/v1') {
    this.baseUrl = baseUrl;
  }

  async getVoices(locale?: string, gender?: string): Promise<VoiceListResponse> {
    const params = new URLSearchParams();
    if (locale) params.append('locale', locale);
    if (gender) params.append('gender', gender);
    
    const url = `${this.baseUrl}/tts/voices${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    return await response.json();
  }

  async generateSpeech(text: string, options: Partial<TTSRequest> = {}): Promise<TTSResponse> {
    const response = await fetch(`${this.baseUrl}/tts/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        ...options
      })
    });

    return await response.json();
  }

  async playAudio(audioUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      audio.onended = () => resolve();
      audio.onerror = (error) => reject(error);
      audio.play();
    });
  }

  async downloadAudio(audioUrl: string, filename: string = 'audio.mp3'): Promise<void> {
    const response = await fetch(audioUrl);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
}

export default TTSClient;
```

### React Hook 示例

```typescript
import { useState, useCallback } from 'react';

interface UseTTSOptions {
  voice?: string;
  rate?: string;
  volume?: string;
  pitch?: string;
}

export function useTTS() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const generateSpeech = useCallback(async (text: string, options: UseTTSOptions = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          ...options
        })
      });

      const result = await response.json();

      if (result.code === 200) {
        setAudioUrl(result.data.audio_url);
        return result.data.audio_url;
      } else {
        throw new Error(result.message || '生成语音失败');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const playAudio = useCallback((url: string) => {
    const audio = new Audio(url);
    audio.play();
  }, []);

  return {
    generateSpeech,
    playAudio,
    loading,
    error,
    audioUrl
  };
}

// 使用示例
function TTSComponent() {
  const { generateSpeech, playAudio, loading, error, audioUrl } = useTTS();

  const handleGenerate = async () => {
    try {
      const url = await generateSpeech('你好，世界！', {
        voice: 'zh-CN-XiaoxiaoNeural'
      });
      playAudio(url);
    } catch (err) {
      console.error('生成失败:', err);
    }
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? '生成中...' : '生成语音'}
      </button>
      {error && <p style={{ color: 'red' }}>错误: {error}</p>}
      {audioUrl && (
        <audio controls src={audioUrl}>
          您的浏览器不支持音频播放
        </audio>
      )}
    </div>
  );
}
```

### Vue 3 Composition API 示例

```typescript
import { ref } from 'vue';

export function useTTS() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const audioUrl = ref<string | null>(null);

  const generateSpeech = async (
    text: string,
    options: {
      voice?: string;
      rate?: string;
      volume?: string;
      pitch?: string;
    } = {}
  ) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          ...options
        })
      });

      const result = await response.json();

      if (result.code === 200) {
        audioUrl.value = result.data.audio_url;
        return result.data.audio_url;
      } else {
        throw new Error(result.message || '生成语音失败');
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '未知错误';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const playAudio = (url: string) => {
    const audio = new Audio(url);
    audio.play();
  };

  return {
    generateSpeech,
    playAudio,
    loading,
    error,
    audioUrl
  };
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 错误处理示例

```javascript
async function generateSpeechWithErrorHandling(text, voice) {
  try {
    const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text, voice })
    });

    const result = await response.json();

    if (result.code === 200) {
      return result.data;
    } else {
      // 处理业务错误
      throw new Error(result.message || '生成语音失败');
    }
  } catch (error) {
    // 处理网络错误或其他错误
    console.error('生成语音时出错:', error);
    throw error;
  }
}
```

---

## 支持的语音

### 中文语音（部分）

| 语音名称 | 性别 | 说明 |
|---------|------|------|
| zh-CN-XiaoxiaoNeural | 女 | 晓晓（默认） |
| zh-CN-YunxiNeural | 男 | 云希 |
| zh-CN-YunyangNeural | 男 | 云扬 |
| zh-CN-XiaoyiNeural | 女 | 晓伊 |

### 俄语语音

| 语音名称 | 性别 | 说明 |
|---------|------|------|
| ru-RU-SvetlanaNeural | 女 | 斯维特兰娜 |
| ru-RU-DmitryNeural | 男 | 德米特里 |
| ru-RU-DariyaNeural | 女 | 达里娅 |

**注意**: 完整的语音列表请通过 `/api/v1/tts/voices` 接口获取。

---

## 参数说明

### rate（语速）

- **范围**: `-50%` 到 `+50%`
- **默认**: `+0%`
- **示例**: 
  - `-50%`: 慢速
  - `+0%`: 正常
  - `+50%`: 快速
- **特殊说明**: 俄语长文本（>50字符）默认使用 `-30%`

### volume（音量）

- **范围**: `-50%` 到 `+50%`
- **默认**: `+0%`
- **示例**: 
  - `-50%`: 小声
  - `+0%`: 正常
  - `+50%`: 大声

### pitch（音调）

- **范围**: `-50Hz` 到 `+50Hz`
- **默认**: `+0Hz`
- **示例**: 
  - `-50Hz`: 低音
  - `+0Hz`: 正常
  - `+50Hz`: 高音

---

## 缓存说明

- API 使用缓存机制，相同内容的重复请求会直接返回缓存结果
- 缓存基于文本内容和所有语音参数生成唯一键
- 缓存可以显著提升响应速度

---

## 最佳实践

1. **错误处理**: 始终处理可能的错误情况
2. **加载状态**: 显示加载状态以提升用户体验
3. **缓存利用**: 相同内容可以复用已生成的音频 URL
4. **参数验证**: 在前端验证文本长度（最大5000字符）
5. **用户体验**: 提供播放、暂停、下载等功能

---

## 完整示例页面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TTS 测试</title>
</head>
<body>
  <h1>Edge TTS API 测试</h1>
  
  <div>
    <label>文本内容：</label>
    <textarea id="textInput" rows="4" cols="50">你好，世界！</textarea>
  </div>
  
  <div>
    <label>语音：</label>
    <select id="voiceSelect">
      <option value="zh-CN-XiaoxiaoNeural">中文-晓晓（女）</option>
      <option value="zh-CN-YunxiNeural">中文-云希（男）</option>
      <option value="ru-RU-SvetlanaNeural">俄语-斯维特兰娜（女）</option>
    </select>
  </div>
  
  <div>
    <button id="generateBtn">生成语音</button>
    <button id="playBtn" disabled>播放</button>
    <button id="downloadBtn" disabled>下载</button>
  </div>
  
  <div id="status"></div>
  <audio id="audioPlayer" controls style="display: none;"></audio>

  <script>
    const API_BASE = 'https://ttsedge.egg404.com/api/v1';
    let currentAudioUrl = null;

    document.getElementById('generateBtn').addEventListener('click', async () => {
      const text = document.getElementById('textInput').value;
      const voice = document.getElementById('voiceSelect').value;
      const statusDiv = document.getElementById('status');
      const generateBtn = document.getElementById('generateBtn');
      const playBtn = document.getElementById('playBtn');
      const downloadBtn = document.getElementById('downloadBtn');

      if (!text.trim()) {
        statusDiv.textContent = '请输入文本内容';
        return;
      }

      generateBtn.disabled = true;
      statusDiv.textContent = '生成中...';

      try {
        const response = await fetch(`${API_BASE}/tts/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: text.trim(),
            voice: voice
          })
        });

        const result = await response.json();

        if (result.code === 200) {
          currentAudioUrl = result.data.audio_url;
          document.getElementById('audioPlayer').src = currentAudioUrl;
          document.getElementById('audioPlayer').style.display = 'block';
          playBtn.disabled = false;
          downloadBtn.disabled = false;
          statusDiv.textContent = '生成成功！';
        } else {
          statusDiv.textContent = `错误: ${result.message}`;
        }
      } catch (error) {
        statusDiv.textContent = `错误: ${error.message}`;
      } finally {
        generateBtn.disabled = false;
      }
    });

    document.getElementById('playBtn').addEventListener('click', () => {
      if (currentAudioUrl) {
        document.getElementById('audioPlayer').play();
      }
    });

    document.getElementById('downloadBtn').addEventListener('click', async () => {
      if (currentAudioUrl) {
        const response = await fetch(currentAudioUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'audio.mp3';
        a.click();
        window.URL.revokeObjectURL(url);
      }
    });
  </script>
</body>
</html>
```

---

## 常见问题

### Q: 如何获取所有可用的语音？

A: 调用 `GET /api/v1/tts/voices` 接口，不传任何参数即可获取所有支持的语音。

### Q: 为什么俄语长文本语速会自动降低？

A: 为了提升可听性，系统会自动为俄语长文本（超过50字符）降低语速至 `-30%`。如果需要使用其他语速，请在请求中明确指定 `rate` 参数。

### Q: 音频文件会保存多久？

A: 音频文件会保存在服务器上，建议及时下载。系统使用缓存机制，相同内容会复用已生成的文件。

### Q: 支持哪些音频格式？

A: 目前支持 MP3 格式。

### Q: 文本长度限制是多少？

A: 最大文本长度为 5000 字符。

---

## 技术支持

如有问题，请查看：
- API 文档: https://ttsedge.egg404.com/docs
- ReDoc: https://ttsedge.egg404.com/redoc

