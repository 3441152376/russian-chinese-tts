"""
应用配置管理
使用 Pydantic Settings 管理配置项
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "Edge TTS API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 5005
    
    # 域名配置
    domain: str = "ttsedge.egg404.com"
    base_url: Optional[str] = None  # 如果未设置，将自动从 domain 生成
    
    # API 配置
    api_prefix: str = "/api/v1"
    
    # 文件存储配置
    output_dir: str = "./output"
    cache_dir: str = "./cache"  # 缓存目录
    max_file_size_mb: int = 50
    enable_cache: bool = True  # 是否启用缓存
    
    # TTS 配置
    default_voice: str = "zh-CN-XiaoxiaoNeural"
    default_rate: str = "+0%"
    default_volume: str = "+0%"
    default_pitch: str = "+0Hz"
    
    # 俄语特殊配置
    russian_sentence_rate: str = "-30%"  # 俄语句子默认降低语速
    russian_long_sentence_threshold: int = 50  # 俄语长句子阈值（字符数）
    
    # 安全配置
    max_text_length: int = 5000
    allowed_audio_formats: list[str] = [".mp3", ".wav", ".webm"]
    max_base64_audio_size_mb: float = 1.0  # 直接返回 base64 的最大文件大小（MB）
    
    # CORS 配置
    cors_origins: list[str] = [
        "https://ttsedge.egg404.com",
        "http://ttsedge.egg404.com",
        "https://egg404.com",
        "http://egg404.com"
    ]
    
    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()

# 如果 base_url 未设置，自动从 domain 生成
if settings.base_url is None:
    settings.base_url = f"https://{settings.domain}"

