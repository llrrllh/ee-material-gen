"""
项目统一配置
"""

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_WORKFILES_DIR = Path.home() / "Library/CloudStorage/OneDrive-个人/Workfiles"


class Settings(BaseSettings):
    """运行时配置（支持 .env + 环境变量覆盖）"""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "复旦EE素材生成器"
    app_version: str = "1.0.0"

    cors_allow_origins: str = "*"

    history_dir: Path = Field(default_factory=lambda: BASE_DIR / "history")
    visual_assets_dir: Path = Field(
        default_factory=lambda: DEFAULT_WORKFILES_DIR / "08.视觉素材"
    )

    memory_courses_dir: Path = Field(
        default_factory=lambda: Path.home() / ".openclaw/workspace/memory/courses"
    )
    prompt_courses_dir: Path = Field(
        default_factory=lambda: BASE_DIR / "prompts/courses"
    )

    brochure_dir: Path = Field(
        default_factory=lambda: DEFAULT_WORKFILES_DIR / "00.招生相关/02.项目资料/课程画册"
    )
    courses_colors_output_file: Path = Field(
        default_factory=lambda: BASE_DIR / "courses_colors.json"
    )

    @property
    def cors_origins(self) -> list[str]:
        """将逗号分隔字符串解析为 CORS 列表"""
        raw = self.cors_allow_origins.strip()
        if raw == "*" or not raw:
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """返回缓存后的全局配置对象"""
    return Settings()


def validate_ai_config() -> dict[str, bool]:
    """
    验证 AI API 配置

    Returns:
        各个 AI 客户端的可用状态
    """
    from gemini_client import GeminiClient
    from claude_client import ClaudeClient
    from openai_client import GPTClient

    gemini = GeminiClient()
    claude = ClaudeClient()
    gpt = GPTClient()

    status = {
        "gemini": gemini.is_available(),
        "claude": claude.is_available(),
        "gpt": gpt.is_available()
    }

    if not any(status.values()):
        logger.error("❌ 未配置任何 AI API，应用无法正常工作")
        logger.error("请至少配置以下之一：")
        logger.error("  - GEMINI_API_KEY (推荐)")
        logger.error("  - ANTHROPIC_API_KEY 或 CLAUDE_API_KEY")
        logger.error("  - cc-switch codex provider (GPT)")
        raise ValueError("至少需要配置一个 AI API Key")

    logger.info("✅ AI API 配置状态:")
    logger.info(f"  - Gemini: {'可用' if status['gemini'] else '未配置'}")
    logger.info(f"  - Claude: {'可用' if status['claude'] else '未配置'}")
    logger.info(f"  - GPT: {'可用' if status['gpt'] else '未配置'}")

    return status
