"""
文本转语音服务
使用 edge-tts 实现 TTS 功能
"""
from pathlib import Path
from typing import Optional, List
import edge_tts
from app.config import settings
from app.utils import (
    app_logger,
    get_file_path,
    generate_filename,
    validate_file_size,
    generate_cache_key,
    check_cache_exists,
    save_to_cache,
    get_cache_filename
)
from app.models.response_models import VoiceInfo


class TTSService:
    """文本转语音服务类"""
    
    def __init__(self):
        """初始化 TTS 服务"""
        self.default_voice = settings.default_voice
        self.default_rate = settings.default_rate
        self.default_volume = settings.default_volume
        self.default_pitch = settings.default_pitch
    
    async def get_voices(
        self,
        locale: Optional[str] = None,
        gender: Optional[str] = None
    ) -> List[VoiceInfo]:
        """
        获取可用的语音列表（仅支持中文和俄语）
        
        Args:
            locale: 语言区域过滤，例如：zh-CN 或 ru-RU
            gender: 性别过滤：Male 或 Female
            
        Returns:
            语音信息列表
        """
        try:
            app_logger.info(f"获取语音列表 - locale: {locale}, gender: {gender}")
            
            # 获取所有语音
            voices = await edge_tts.list_voices()
            
            # 转换为 VoiceInfo 对象
            voice_list = []
            for voice in voices:
                voice_locale = voice.get("Locale", "")
                voice_gender = voice.get("Gender", "")
                
                # 只支持中文和俄语
                if not (voice_locale.startswith("zh-") or voice_locale.startswith("ru-")):
                    continue
                
                # 应用过滤条件
                if locale and not voice_locale.startswith(locale):
                    continue
                if gender and voice_gender != gender:
                    continue
                
                # 使用 ShortName 作为语音名称（edge-tts 实际使用的格式）
                voice_short_name = voice.get("ShortName", "")
                if not voice_short_name:
                    # 如果没有 ShortName，尝试从 Name 中提取
                    name = voice.get("Name", "")
                    # 格式: "Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)"
                    # 提取: zh-CN-XiaoxiaoNeural
                    if "(" in name and ")" in name:
                        parts = name.split("(")[1].split(")")[0].split(", ")
                        if len(parts) == 2:
                            voice_short_name = f"{parts[0]}-{parts[1]}"
                
                voice_info = VoiceInfo(
                    name=voice_short_name,
                    gender=voice_gender,
                    locale=voice_locale,
                    friendly_name=voice.get("FriendlyName", "")
                )
                voice_list.append(voice_info)
            
            app_logger.info(f"找到 {len(voice_list)} 个匹配的语音")
            return voice_list
            
        except Exception as e:
            app_logger.error(f"获取语音列表失败: {str(e)}")
            raise
    
    def _process_russian_text(self, text: str) -> str:
        """
        处理俄语文本，为长句子添加适当的停顿
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 如果文本长度超过阈值，需要处理
        if len(text) > settings.russian_long_sentence_threshold:
            # 在逗号、句号等标点后添加短暂停顿（通过添加空格实现更好的断句）
            # 将多个连续空格替换为单个空格
            processed = text.replace("  ", " ")
            
            # 在长句子中的逗号后确保有适当的停顿
            # edge-tts 会自动处理标点符号，但我们可以优化文本格式
            return processed
        
        return text
    
    def _get_optimal_rate_for_russian(self, text: str, user_rate: Optional[str]) -> str:
        """
        为俄语文本获取最佳语速
        
        Args:
            text: 文本内容
            user_rate: 用户指定的语速
            
        Returns:
            优化后的语速
        """
        # 如果用户明确指定了语速，使用用户指定的
        if user_rate is not None:
            return user_rate
        
        # 检测是否为长句子（超过阈值）
        if len(text) > settings.russian_long_sentence_threshold:
            # 长句子使用降低的语速
            app_logger.info(f"检测到俄语长文本（{len(text)} 字符），自动降低语速至 {settings.russian_sentence_rate}")
            return settings.russian_sentence_rate
        
        # 短文本使用正常语速
        return self.default_rate
    
    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        pitch: Optional[str] = None
    ) -> tuple[str, Path]:
        """
        将文本转换为语音（仅支持中文和俄语）
        
        Args:
            text: 要转换的文本
            voice: 语音名称（必须是中文或俄语语音）
            rate: 语速（如果未指定，俄语长句子会自动降低语速）
            volume: 音量
            pitch: 音调
            
        Returns:
            (文件名, 文件路径, 实际使用的语速) 元组
        """
        try:
            # 使用默认值或提供的参数
            selected_voice = voice or self.default_voice
            selected_volume = volume or self.default_volume
            selected_pitch = pitch or self.default_pitch
            
            # 验证语音是否为中文或俄语
            if not (selected_voice.startswith("zh-") or selected_voice.startswith("ru-")):
                raise ValueError(f"不支持的语音: {selected_voice}，仅支持中文（zh-）和俄语（ru-）语音")
            
            # 处理俄语文本：如果是俄语且为长句子，自动优化语速
            processed_text = text
            if selected_voice.startswith("ru-"):
                # 处理俄语文本格式
                processed_text = self._process_russian_text(text)
                # 为俄语长句子自动调整语速
                selected_rate = self._get_optimal_rate_for_russian(processed_text, rate)
            else:
                # 中文使用用户指定或默认语速
                selected_rate = rate or self.default_rate
            
            # 生成缓存键（基于处理后的文本和实际使用的参数）
            cache_key = generate_cache_key(
                text=processed_text,
                voice=selected_voice,
                rate=selected_rate,
                volume=selected_volume,
                pitch=selected_pitch
            )
            
            # 检查缓存是否存在
            cached_file = check_cache_exists(cache_key, ".mp3")
            if cached_file:
                app_logger.info(f"从缓存获取音频文件: {cache_key}")
                # 返回缓存文件名和路径
                cache_filename = get_cache_filename(cache_key, ".mp3")
                return cache_filename, cached_file, selected_rate
            
            app_logger.info(
                f"开始文本转语音 - "
                f"voice: {selected_voice}, "
                f"rate: {selected_rate}, "
                f"volume: {selected_volume}, "
                f"pitch: {selected_pitch}, "
                f"text_length: {len(processed_text)}, "
                f"cache_key: {cache_key}"
            )
            
            # 生成临时文件名（用于生成音频）
            temp_filename = generate_filename(".mp3")
            temp_file_path = get_file_path(temp_filename)
            
            # 创建 TTS 实例
            communicate = edge_tts.Communicate(
                text=processed_text,
                voice=selected_voice,
                rate=selected_rate,
                volume=selected_volume,
                pitch=selected_pitch
            )
            
            # 保存音频文件到临时位置
            await communicate.save(str(temp_file_path))
            
            # 验证文件大小
            if not validate_file_size(temp_file_path):
                temp_file_path.unlink()
                raise ValueError(f"生成的文件大小超过限制 ({settings.max_file_size_mb}MB)")
            
            # 保存到缓存
            cached_file_path = save_to_cache(cache_key, temp_file_path, ".mp3")
            
            # 返回缓存文件名和路径
            cache_filename = get_cache_filename(cache_key, ".mp3")
            app_logger.info(f"文本转语音成功 - 文件: {cache_filename}, 语速: {selected_rate}, 已缓存")
            
            return cache_filename, cached_file_path, selected_rate
            
        except Exception as e:
            app_logger.error(f"文本转语音失败: {str(e)}")
            raise
    
    async def get_audio_duration(self, file_path: Path) -> Optional[float]:
        """
        获取音频文件时长（秒）
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            音频时长（秒），如果无法获取则返回 None
        """
        try:
            # 这里可以集成音频处理库来获取时长
            # 为了简化，暂时返回 None
            # 可以使用 mutagen 或 pydub 等库来实现
            return None
        except Exception as e:
            app_logger.warning(f"获取音频时长失败: {str(e)}")
            return None

