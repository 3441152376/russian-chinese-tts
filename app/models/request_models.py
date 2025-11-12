"""
请求数据模型
定义 API 请求的数据结构
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TTSRequest(BaseModel):
    """文本转语音请求模型"""
    
    text: str = Field(
        ...,
        description="要转换的文本内容",
        min_length=1,
        max_length=5000
    )
    
    voice: Optional[str] = Field(
        None,
        description="语音名称，例如：zh-CN-XiaoxiaoNeural"
    )
    
    rate: Optional[str] = Field(
        None,
        description="语速，例如：+0%、-50%、+50%"
    )
    
    volume: Optional[str] = Field(
        None,
        description="音量，例如：+0%、-50%、+50%"
    )
    
    pitch: Optional[str] = Field(
        None,
        description="音调，例如：+0Hz、-50Hz、+50Hz"
    )
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """验证文本内容"""
        if not v or not v.strip():
            raise ValueError("文本内容不能为空")
        return v.strip()


class VoiceListRequest(BaseModel):
    """获取语音列表请求模型"""
    
    locale: Optional[str] = Field(
        None,
        description="语言区域过滤，例如：zh-CN"
    )
    
    gender: Optional[str] = Field(
        None,
        description="性别过滤：Male 或 Female"
    )

