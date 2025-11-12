"""
文件工具类
处理文件相关的操作
"""
import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional
from app.config import settings
from app.utils.logger import app_logger


def ensure_output_dir() -> Path:
    """确保输出目录存在"""
    output_path = Path(settings.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def ensure_cache_dir() -> Path:
    """确保缓存目录存在"""
    cache_path = Path(settings.cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def generate_filename(extension: str = ".mp3") -> str:
    """生成唯一的文件名"""
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{extension}"


def generate_cache_key(
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str
) -> str:
    """
    生成缓存键（基于文本和语音参数）
    
    Args:
        text: 文本内容
        voice: 语音名称
        rate: 语速
        volume: 音量
        pitch: 音调
        
    Returns:
        缓存键（MD5 哈希值）
    """
    # 组合所有参数生成唯一键
    cache_string = f"{text}|{voice}|{rate}|{volume}|{pitch}"
    # 使用 MD5 生成哈希值
    hash_obj = hashlib.md5(cache_string.encode('utf-8'))
    return hash_obj.hexdigest()


def get_cache_filename(cache_key: str, extension: str = ".mp3") -> str:
    """根据缓存键生成文件名"""
    return f"{cache_key}{extension}"


def get_cache_path(cache_key: str, extension: str = ".mp3") -> Path:
    """获取缓存文件的完整路径"""
    cache_dir = ensure_cache_dir()
    filename = get_cache_filename(cache_key, extension)
    return cache_dir / filename


def get_file_path(filename: str) -> Path:
    """获取文件的完整路径"""
    output_dir = ensure_output_dir()
    return output_dir / filename


def delete_file(filename: str) -> bool:
    """删除文件"""
    try:
        file_path = get_file_path(filename)
        if file_path.exists():
            file_path.unlink()
            app_logger.info(f"文件已删除: {filename}")
            return True
        return False
    except Exception as e:
        app_logger.error(f"删除文件失败 {filename}: {str(e)}")
        return False


def get_file_size_mb(filepath: Path) -> float:
    """获取文件大小（MB）"""
    if not filepath.exists():
        return 0.0
    return filepath.stat().st_size / (1024 * 1024)


def validate_file_size(filepath: Path) -> bool:
    """验证文件大小是否在限制范围内"""
    size_mb = get_file_size_mb(filepath)
    return size_mb <= settings.max_file_size_mb


def check_cache_exists(cache_key: str, extension: str = ".mp3") -> Optional[Path]:
    """
    检查缓存文件是否存在
    
    Args:
        cache_key: 缓存键
        extension: 文件扩展名
        
    Returns:
        如果缓存存在，返回文件路径；否则返回 None
    """
    if not settings.enable_cache:
        return None
    
    cache_path = get_cache_path(cache_key, extension)
    if cache_path.exists() and cache_path.is_file():
        return cache_path
    return None


def save_to_cache(cache_key: str, source_file: Path, extension: str = ".mp3") -> Path:
    """
    将文件保存到缓存
    
    Args:
        cache_key: 缓存键
        source_file: 源文件路径
        extension: 文件扩展名
        
    Returns:
        缓存文件路径
    """
    if not settings.enable_cache:
        return source_file
    
    cache_path = get_cache_path(cache_key, extension)
    
    # 如果缓存文件已存在，直接返回
    if cache_path.exists():
        return cache_path
    
    # 复制文件到缓存目录
    import shutil
    shutil.copy2(source_file, cache_path)
    app_logger.info(f"文件已保存到缓存: {cache_path}")
    return cache_path

