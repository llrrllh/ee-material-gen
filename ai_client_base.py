"""
AI 客户端基类
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BaseAIClient:
    """AI 客户端基类，统一接口"""

    def is_available(self) -> bool:
        """检查客户端是否可用"""
        raise NotImplementedError

    def optimize(self, prompt: str, max_tokens: Optional[int] = None, timeout: float = 300.0) -> tuple[str, str]:
        """
        调用 AI 模型生成内容

        Args:
            prompt: 提示词
            max_tokens: 最大输出 token 数
            timeout: 超时时间（秒）

        Returns:
            (生成的内容, 使用的模型名称)
        """
        raise NotImplementedError

    def _log_call(self, model: str, max_tokens: Optional[int], timeout: float):
        """统一的调用日志"""
        logger.info(f"AI 调用: model={model}, max_tokens={max_tokens}, timeout={timeout}s")

    def _log_error(self, error: Exception):
        """统一的错误日志"""
        logger.error(f"{self.__class__.__name__} 调用失败: {str(error)}")
