"""
OpenAI/GPT API 客户端
从 cc-switch 的 codex provider 读取配置，用于精修
"""

import json
import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from dotenv import load_dotenv
from ai_client_base import BaseAIClient

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DEFAULT_MODEL = "gpt-5-codex"


class GPTClient(BaseAIClient):
    """GPT API 客户端，从 cc-switch codex provider 读取配置"""

    def __init__(self):
        self._config_cache = None
        self._cache_time = None
        self._cache_ttl = timedelta(minutes=5)  # 缓存5分钟

        api_key, base_url, model = self._load_config()
        self.model = model or DEFAULT_MODEL

        if not api_key:
            logger.warning("未找到 GPT API Key（cc-switch codex），GPT 精修功能将不可用")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai 包未安装，GPT 精修功能将不可用")
            self.client = None
        else:
            logger.info(f"GPT 客户端初始化: model={self.model}, base_url={base_url or '默认'}")
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self.client = OpenAI(**kwargs)

    def is_available(self) -> bool:
        return self.client is not None

    def optimize(self, prompt: str, max_tokens: int = 16000, timeout: float = 300.0) -> tuple[str, str]:
        """
        使用 GPT 精修素材

        Returns:
            (精修后的内容, 使用的模型名称)
        """
        if not self.client:
            raise Exception("GPT API 未配置，请在 cc-switch 中添加 codex provider")

        try:
            self._log_call(self.model, max_tokens, timeout)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                timeout=timeout,
            )
            response_text = response.choices[0].message.content
            return response_text, self.model
        except Exception as e:
            self._log_error(e)
            raise

    def _load_config(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        从 cc-switch codex provider 读取 API key、base_url 和 model。
        使用缓存避免频繁读取数据库。

        Returns:
            (api_key, base_url, model)
        """
        # 检查缓存是否有效
        if self._config_cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_ttl:
                return self._config_cache

        # 读取新配置
        config = self._read_config_from_db()

        # 更新缓存
        self._config_cache = config
        self._cache_time = datetime.now()

        return config

    @staticmethod
    def _read_config_from_db() -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        从 cc-switch codex provider 或 openclaw openai provider 读取配置。
        优先级：cc-switch codex > openclaw openai

        Returns:
            (api_key, base_url, model)
        """
        # 尝试从 cc-switch 读取 codex provider
        config = GPTClient._read_from_cc_switch()
        if config[0]:  # 如果找到 API key
            return config

        # 回退到 openclaw openai provider
        config = GPTClient._read_from_openclaw()
        if config[0]:
            return config

        return None, None, None

    @staticmethod
    def _read_from_cc_switch() -> tuple[Optional[str], Optional[str], Optional[str]]:
        """从 cc-switch codex provider 读取配置"""
        db_path = Path(
            os.getenv("CC_SWITCH_DB_PATH", str(Path.home() / ".cc-switch" / "cc-switch.db"))
        ).expanduser()
        if not db_path.exists():
            return None, None, None

        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT settings_config
                    FROM providers
                    WHERE app_type='codex'
                    ORDER BY is_current DESC
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
                if not row or not row[0]:
                    return None, None, None

                cfg = json.loads(row[0])

                # api key: auth.OPENAI_API_KEY
                api_key = None
                auth = cfg.get("auth", {})
                if isinstance(auth, dict):
                    api_key = auth.get("OPENAI_API_KEY")

                # base_url 和 model 在 config (toml 格式字符串) 中
                base_url = None
                model = None
                config_str = cfg.get("config", "")
                if isinstance(config_str, str):
                    # 提取 model
                    m = re.search(r'^model\s*=\s*"([^"]+)"', config_str, re.MULTILINE)
                    if m:
                        model = m.group(1)
                    # 提取 base_url
                    m = re.search(r'base_url\s*=\s*"([^"]+)"', config_str)
                    if m:
                        base_url = m.group(1)

                return api_key, base_url, model
        except Exception:
            return None, None, None

    @staticmethod
    def _read_from_openclaw() -> tuple[Optional[str], Optional[str], Optional[str]]:
        """从 openclaw openai provider 读取配置"""
        db_path = Path.home() / ".openclaw" / "openclaw.db"
        if not db_path.exists():
            return None, None, None

        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT settings_config
                    FROM providers
                    WHERE app_type='openai'
                    ORDER BY is_current DESC
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
                if not row or not row[0]:
                    return None, None, None

                cfg = json.loads(row[0])

                # api key
                api_key = None
                auth = cfg.get("auth", {})
                if isinstance(auth, dict):
                    api_key = auth.get("OPENAI_API_KEY")

                # base_url 和 model
                base_url = None
                model = None
                config_str = cfg.get("config", "")
                if isinstance(config_str, str):
                    m = re.search(r'^model\s*=\s*"([^"]+)"', config_str, re.MULTILINE)
                    if m:
                        model = m.group(1)
                    m = re.search(r'base_url\s*=\s*"([^"]+)"', config_str)
                    if m:
                        base_url = m.group(1)

                return api_key, base_url, model
        except Exception:
            return None, None, None
