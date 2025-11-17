"""
响应数据模型
定义 API 响应的数据结构
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """基础响应模型"""
    
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class TTSResponse(BaseModel):
    """文本转语音响应模型"""
    
    audio_url: str = Field(..., description="生成的音频文件 URL")
    text: str = Field(..., description="转换的文本内容")
    voice: str = Field(..., description="使用的语音名称")
    duration: Optional[float] = Field(None, description="音频时长（秒）")
    actual_rate: Optional[str] = Field(None, description="实际使用的语速（自动优化后）")
    audio_data: Optional[str] = Field(None, description="音频数据（base64编码），仅在 return_audio=true 时返回")


class VoiceInfo(BaseModel):
    """语音信息模型"""
    
    name: str = Field(..., description="语音名称")
    gender: str = Field(..., description="性别")
    locale: str = Field(..., description="语言区域")
    friendly_name: Optional[str] = Field(None, description="友好名称")


class VoiceListResponse(BaseModel):
    """语音列表响应模型"""
    
    total: int = Field(..., description="语音总数")
    voices: list[VoiceInfo] = Field(..., description="语音列表")

