"""
文本转语音控制器
处理 TTS 相关的 API 请求
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import base64
import aiofiles
from app.services import TTSService
from app.models import (
    TTSRequest,
    BaseResponse,
    TTSResponse,
    VoiceListResponse
)
from app.utils import app_logger, get_file_path, get_cache_path, delete_file
from app.config import settings


# 创建路由器
router = APIRouter(prefix="/tts", tags=["文本转语音"])

# 创建服务实例
tts_service = TTSService()


@router.post("/generate-stream")
async def generate_speech_stream(request: TTSRequest):
    """
    流式生成语音文件（直接返回音频流，适合快速播放）
    
    Args:
        request: TTS 请求参数
        
    Returns:
        音频文件流
    """
    try:
        app_logger.info(f"收到流式 TTS 请求 - 文本长度: {len(request.text)}")
        
        # 验证文本长度
        if len(request.text) > settings.max_text_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文本长度超过限制 ({settings.max_text_length} 字符)"
            )
        
        # 调用服务生成语音
        filename, file_path, actual_rate = await tts_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch
        )
        
        # 流式返回音频文件
        async def generate():
            async with aiofiles.open(file_path, 'rb') as f:
                while True:
                    chunk = await f.read(8192)  # 8KB 块
                    if not chunk:
                        break
                    yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Audio-Filename": filename,
                "X-Actual-Rate": actual_rate
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"流式生成语音失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成语音失败: {str(e)}"
        )


@router.post("/generate", response_model=BaseResponse)
async def generate_speech(request: TTSRequest):
    """
    生成语音文件
    
    Args:
        request: TTS 请求参数
        
    Returns:
        包含音频文件 URL 的响应
    """
    try:
        app_logger.info(f"收到 TTS 请求 - 文本长度: {len(request.text)}")
        
        # 验证文本长度
        if len(request.text) > settings.max_text_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文本长度超过限制 ({settings.max_text_length} 字符)"
            )
        
        # 调用服务生成语音
        filename, file_path, actual_rate = await tts_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch
        )
        
        # 获取音频时长
        duration = await tts_service.get_audio_duration(file_path)
        
        # 构建响应（使用完整 URL）
        audio_url = f"{settings.base_url}{settings.api_prefix}/tts/download/{filename}"
        
        # 如果请求直接返回音频数据，读取文件并编码为 base64
        audio_data = None
        if request.return_audio:
            try:
                # 检查文件大小，只对小文件返回 base64（避免响应过大）
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                if file_size_mb <= settings.max_base64_audio_size_mb:  # 只对小于限制的文件返回 base64
                    with open(file_path, "rb") as f:
                        audio_bytes = f.read()
                        audio_data = base64.b64encode(audio_bytes).decode('utf-8')
                        app_logger.info(f"返回音频数据（base64），大小: {file_size_mb:.2f}MB")
                else:
                    app_logger.warning(f"文件过大（{file_size_mb:.2f}MB），不返回 base64 数据")
            except Exception as e:
                app_logger.warning(f"读取音频文件失败: {str(e)}")
        
        response_data = TTSResponse(
            audio_url=audio_url,
            text=request.text,
            voice=request.voice or settings.default_voice,
            duration=duration,
            actual_rate=actual_rate,
            audio_data=audio_data
        )
        
        return BaseResponse(
            code=200,
            message="语音生成成功",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"生成语音失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成语音失败: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_audio(filename: str):
    """
    下载音频文件（支持缓存文件和普通文件）
    
    Args:
        filename: 文件名
        
    Returns:
        音频文件
    """
    try:
        # 先尝试从缓存目录查找（缓存文件名是 MD5 哈希值）
        if settings.enable_cache:
            # 如果文件名是 32 位十六进制字符串（MD5），则从缓存目录查找
            if len(filename) == 36 and filename.endswith(".mp3"):  # 32位哈希 + .mp3 = 36字符
                cache_key = filename.replace(".mp3", "")
                cache_path = get_cache_path(cache_key, ".mp3")
                if cache_path.exists():
                    return FileResponse(
                        path=str(cache_path),
                        media_type="audio/mpeg",
                        filename=filename
                    )
        
        # 从普通输出目录查找
        file_path = get_file_path(filename)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type="audio/mpeg",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


@router.get("/voices", response_model=BaseResponse)
async def get_voices(
    locale: Optional[str] = None,
    gender: Optional[str] = None
):
    """
    获取可用的语音列表
    
    Args:
        locale: 语言区域过滤
        gender: 性别过滤
        
    Returns:
        语音列表
    """
    try:
        app_logger.info(f"获取语音列表请求 - locale: {locale}, gender: {gender}")
        
        voices = await tts_service.get_voices(locale=locale, gender=gender)
        
        response_data = VoiceListResponse(
            total=len(voices),
            voices=voices
        )
        
        return BaseResponse(
            code=200,
            message="获取语音列表成功",
            data=response_data
        )
        
    except Exception as e:
        app_logger.error(f"获取语音列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音列表失败: {str(e)}"
        )


@router.delete("/file/{filename}")
async def delete_audio_file(filename: str):
    """
    删除音频文件
    
    Args:
        filename: 文件名
        
    Returns:
        删除结果
    """
    try:
        success = delete_file(filename)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在或删除失败"
            )
        
        return BaseResponse(
            code=200,
            message="文件删除成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"删除文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )

