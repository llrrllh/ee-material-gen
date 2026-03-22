"""
Gemini API 客户端
支持多模型 Fallback 机制
"""

import os
from pathlib import Path
from typing import Tuple, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


# Gemini 模型列表（按优先级排序）
DEFAULT_MODELS = [
    "models/gemini-3.1-pro-preview",   # 首选
    "models/gemini-3.0-pro-preview",   # 备选1
    "models/gemini-2.5-pro",           # 备选2
    "models/gemini-3.0-flash-preview", # Fallback（不可用时自动降级）
]


class GeminiClient:
    """Gemini API 客户端，支持自动 Fallback"""

    def __init__(self, api_key: Optional[str] = None, models: Optional[List[str]] = None):
        """
        初始化 Gemini 客户端

        Args:
            api_key: Gemini API Key（如果为 None，从环境变量 GEMINI_API_KEY 读取）
            models: 模型列表（如果为 None，使用默认列表）
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.models = models or DEFAULT_MODELS

    def generate(self, prompt: str, models: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        调用 Gemini API 生成内容，支持自动 Fallback

        Args:
            prompt: 提示词
            models: 模型列表（如果为 None，使用初始化时的模型列表）

        Returns:
            (生成的内容, 使用的模型名称)

        Raises:
            Exception: 所有模型都失败时抛出异常
        """
        models_to_try = models or self.models

        last_error = None
        for model_name in models_to_try:
            try:
                print(f"尝试使用模型: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)

                # 检查响应是否有效
                if not response or not response.text:
                    raise ValueError(f"模型 {model_name} 返回空响应")

                print(f"✓ 成功使用模型: {model_name}")
                return response.text, model_name

            except Exception as e:
                error_msg = str(e).lower()
                last_error = e

                # 如果是配额或限流错误，尝试下一个模型
                if "quota" in error_msg or "429" in error_msg or "resource_exhausted" in error_msg:
                    print(f"✗ 模型 {model_name} 配额不足，尝试下一个模型...")
                    continue

                # 如果是其他错误，也尝试下一个模型
                print(f"✗ 模型 {model_name} 失败: {str(e)[:100]}")
                continue

        # 所有模型都失败
        raise Exception(f"所有模型都失败。最后一个错误: {last_error}")


def call_gemini_with_fallback(prompt: str, api_key: Optional[str] = None, models: Optional[List[str]] = None) -> Tuple[str, str]:
    """
    便捷函数：调用 Gemini API 生成内容

    Args:
        prompt: 提示词
        api_key: Gemini API Key（如果为 None，从环境变量读取）
        models: 模型列表（如果为 None，使用默认列表）

    Returns:
        (生成的内容, 使用的模型名称)
    """
    client = GeminiClient(api_key=api_key, models=models)
    return client.generate(prompt)
