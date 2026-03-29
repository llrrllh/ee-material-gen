"""
Claude API 客户端
用于高级素材优化
"""

import logging
import os
from anthropic import Anthropic
from dotenv import dotenv_values
from ai_client_base import BaseAIClient

logger = logging.getLogger(__name__)


class ClaudeClient(BaseAIClient):
    """Claude API 客户端"""

    def __init__(self):
        """初始化 Claude 客户端"""
        # 只从 .env 文件读取配置，忽略系统环境变量
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        env_config = dotenv_values(env_file)

        api_key = env_config.get("ANTHROPIC_API_KEY") or env_config.get("CLAUDE_API_KEY")
        base_url = env_config.get("ANTHROPIC_BASE_URL")  # 只从 .env 文件读取

        if not api_key:
            logger.warning("未找到 Claude API Key，Claude 优化功能将不可用")
            self.client = None
        else:
            # 关键修复：显式传递 base_url 参数，覆盖系统环境变量
            # 如果 .env 文件中没有设置 base_url，传递 None 来使用官方 API
            if base_url:
                logger.info(f"使用自定义 Claude API 基础 URL: {base_url}")
                self.client = Anthropic(api_key=api_key, base_url=base_url)
            else:
                # 显式传递 base_url=None，强制使用官方 API，忽略系统环境变量
                logger.info("使用官方 Anthropic API")
                # 注意：Anthropic SDK 会自动使用默认的官方 API URL
                # 但为了确保不使用系统环境变量，我们需要显式设置
                self.client = Anthropic(
                    api_key=api_key,
                    base_url="https://api.anthropic.com"  # 显式指定官方 API URL
                )

    def is_available(self) -> bool:
        """检查 Claude API 是否可用"""
        return self.client is not None

    def optimize(self, prompt: str, max_tokens: int = 16000, timeout: float = 300.0) -> tuple[str, str]:
        """
        使用 Claude 优化素材

        Args:
            prompt: 优化提示词
            max_tokens: 最大 token 数
            timeout: 超时时间（秒），默认 300 秒（5 分钟）

        Returns:
            (优化后的内容, 使用的模型名称)
        """
        if not self.client:
            raise Exception("Claude API 未配置，请在 .env 文件中添加 ANTHROPIC_API_KEY 或 CLAUDE_API_KEY")

        try:
            model = "claude-sonnet-4-6"
            self._log_call(model, max_tokens, timeout)

            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                timeout=timeout,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            return response_text, model

        except Exception as e:
            self._log_error(e)
            raise
