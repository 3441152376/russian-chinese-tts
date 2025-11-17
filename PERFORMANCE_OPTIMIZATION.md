# 性能优化指南

## 问题分析

### 当前流程的问题

即使缓存命中，前端仍需要**两次请求**：

1. **第一次请求**：`POST /api/v1/tts/generate`
   - 返回 `audio_url`
   - 耗时：~0.8秒（缓存命中）

2. **第二次请求**：`GET /api/v1/tts/download/{filename}`
   - 下载音频文件
   - 耗时：~0.86秒

**总计：~1.6秒**

### 优化方案

添加 `return_audio` 参数，直接在响应中返回音频数据（base64编码），**只需一次请求**。

## 使用方法

### 前端代码

```javascript
// 优化前（两次请求）
const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'территория',
    voice: 'ru-RU-SvetlanaNeural'
  })
});
const result = await response.json();
const audioUrl = result.data.audio_url;
// 还需要再次请求下载音频
const audio = new Audio(audioUrl);
audio.play();

// 优化后（一次请求）
const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'территория',
    voice: 'ru-RU-SvetlanaNeural',
    return_audio: true  // 关键参数
  })
});
const result = await response.json();

if (result.data.audio_data) {
  // 直接使用 base64 数据，无需二次请求
  const audioBlob = base64ToBlob(result.data.audio_data, 'audio/mpeg');
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
}

// base64 转 Blob 辅助函数
function base64ToBlob(base64, mimeType) {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
}
```

### React Hook 示例

```typescript
export function useTTS() {
  const generateSpeech = async (text: string, options: {
    voice?: string;
    returnAudio?: boolean;  // 新增参数
  } = {}) => {
    const response = await fetch('https://ttsedge.egg404.com/api/v1/tts/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        voice: options.voice,
        return_audio: options.returnAudio ?? true  // 默认开启，提升性能
      })
    });

    const result = await response.json();
    
    if (result.code === 200) {
      // 优先使用 audio_data（如果存在）
      if (result.data.audio_data) {
        const audioBlob = base64ToBlob(result.data.audio_data, 'audio/mpeg');
        return URL.createObjectURL(audioBlob);
      }
      // 降级使用 audio_url
      return result.data.audio_url;
    }
    
    throw new Error(result.message);
  };

  return { generateSpeech };
}
```

## 性能对比

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 缓存命中 + 下载 | ~1.6秒 | ~0.8秒 | **50%** |
| 首次生成 + 下载 | ~4.0秒 | ~3.2秒 | **20%** |

## 注意事项

1. **文件大小限制**：只有小于 1MB 的文件才会返回 base64 数据
2. **响应大小**：base64 编码会增加约 33% 的数据量
3. **适用场景**：
   - ✅ **推荐**：单词、短语（< 1MB）
   - ⚠️ **不推荐**：长文本（> 1MB），会回退到 URL 方式

## 最佳实践

1. **单词和短语**：使用 `return_audio: true`
2. **长文本**：使用默认方式（`return_audio: false`）
3. **前端判断**：根据文本长度自动选择

```javascript
const shouldReturnAudio = text.length < 100;  // 根据文本长度判断

const response = await fetch('...', {
  body: JSON.stringify({
    text,
    voice,
    return_audio: shouldReturnAudio
  })
});
```

