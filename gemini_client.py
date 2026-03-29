"""
Gemini API 客户端
支持多模型 Fallback + 多 Key 轮转
"""

import logging
import os
import time
import json
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List, Optional, Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    from google import genai
except ImportError:  # pragma: no cover - 由部署环境决定
    genai = None

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass(frozen=True)
class GeminiProvider:
    """一个 Gemini API 提供方（key + 可选代理地址）"""
    api_key: str
    base_url: Optional[str] = None   # None = 直连 Google
    label: str = ""

    @property
    def dedup_key(self) -> tuple:
        return (self.api_key, self.base_url)


# Gemini 模型列表（按优先级排序）
DEFAULT_MODELS = [
    "models/gemini-3.1-pro-preview",   # 首选
    "models/gemini-3-pro-preview",     # 备选1
    "models/gemini-3-flash-preview",   # 备选2
    "models/gemini-2.5-pro",           # Fallback
]

DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_TOTAL_TIMEOUT_SECONDS = 120
DEFAULT_MODEL_COOLDOWN_SECONDS = 300
DEFAULT_MAX_OUTPUT_TOKENS = 0


class GeminiClient:
    """Gemini API 客户端，支持自动 Fallback + 延迟优选"""
    _state_lock = threading.Lock()
    _unsupported_models: set[str] = set()
    _model_cooldowns: Dict[str, float] = {}
    _provider_latencies: Dict[str, float] = {}   # label -> EMA 延迟（秒）
    _LATENCY_EMA_ALPHA = 0.3  # 新样本权重，越大越重视最近一次

    def __init__(self, api_key: Optional[str] = None, models: Optional[List[str]] = None):
        """
        初始化 Gemini 客户端

        Args:
            api_key: Gemini API Key（如果指定，仅使用此单 key；否则自动加载所有可用 provider）
            models: 模型列表（如果为 None，使用默认列表）
        """
        self.request_timeout_seconds = self._load_positive_int_env(
            "GEMINI_REQUEST_TIMEOUT_SECONDS",
            DEFAULT_REQUEST_TIMEOUT_SECONDS,
        )
        self.total_timeout_seconds = self._load_positive_int_env(
            "GEMINI_TOTAL_TIMEOUT_SECONDS",
            DEFAULT_TOTAL_TIMEOUT_SECONDS,
        )
        self.model_cooldown_seconds = self._load_positive_int_env(
            "GEMINI_MODEL_COOLDOWN_SECONDS",
            DEFAULT_MODEL_COOLDOWN_SECONDS,
        )
        self.fast_mode = self._load_bool_env("GEMINI_FAST_MODE", False)
        self.max_output_tokens_default = self._load_non_negative_int_env(
            "GEMINI_MAX_OUTPUT_TOKENS",
            DEFAULT_MAX_OUTPUT_TOKENS,
        )

        # 构建 provider 列表
        if api_key:
            providers = [GeminiProvider(api_key=api_key, label="explicit")]
        else:
            providers = self._load_all_providers()
        if not providers:
            raise ValueError(
                "No Gemini API key found. Checked GEMINI_API_KEY / GOOGLE_API_KEY and cc-switch Gemini providers."
            )

        # 向后兼容：保留 self.api_key（第一个 provider 的 key）
        self.api_key = providers[0].api_key

        # 为每个 provider 创建 genai.Client
        self.providers: List[Tuple[GeminiProvider, object]] = []
        if genai is None:
            self.client = None
        else:
            for p in providers:
                http_opts: Dict[str, object] = {"timeout": self.request_timeout_seconds * 1000}
                if p.base_url:
                    http_opts["base_url"] = p.base_url
                client = genai.Client(api_key=p.api_key, http_options=http_opts)
                self.providers.append((p, client))
            # 向后兼容
            self.client = self.providers[0][1] if self.providers else None

        self.models = models or self._resolve_models_from_env()
        logger.info(f"GeminiClient 初始化完成，{len(self.providers)} 个 provider，模型: {self.models}")

    def is_available(self) -> bool:
        """检查 Gemini 客户端是否可用"""
        return len(self.providers) > 0

    def generate(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        fast_mode: Optional[bool] = None,
        max_output_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        """
        调用 Gemini API 生成内容，支持多 Provider 轮转 + 多模型 Fallback

        Returns:
            (生成的内容, 使用的模型名称)
        """
        if not self.providers:
            raise RuntimeError(
                "google-genai is not installed. Please run: pip install google-genai"
            )

        models_to_try = models or self.models
        last_error = None
        use_fast_mode = self.fast_mode if fast_mode is None else fast_mode
        retry_waits = [] if use_fast_mode else [2, 5]
        deadline = time.monotonic() + self.total_timeout_seconds
        resolved_max_output_tokens = self._resolve_max_output_tokens(max_output_tokens)
        any_tried = False

        if use_fast_mode:
            logger.info("Gemini 快速模式已开启：每个模型仅尝试 1 次")
        if resolved_max_output_tokens:
            logger.info(f"Gemini maxOutputTokens={resolved_max_output_tokens}")

        for model_name in models_to_try:
            skip_reason = self._get_model_skip_reason(model_name)
            if skip_reason:
                logger.info(f"跳过模型 {model_name}: {skip_reason}")
                continue

            # 按延迟优选排列 provider
            provider_order = self._sorted_provider_indices(self.providers)
            for pidx in provider_order:
                provider, client = self.providers[pidx]

                attempts = 1 + len(retry_waits)
                for attempt in range(attempts):
                    if time.monotonic() >= deadline:
                        timeout_error = TimeoutError(
                            f"Gemini 请求总超时（{self.total_timeout_seconds}s）。"
                        )
                        raise Exception(
                            f"所有模型都失败。最后一个错误: {last_error or timeout_error}"
                        ) from timeout_error

                    try:
                        any_tried = True
                        t0 = time.monotonic()
                        logger.info(
                            f"尝试 [{provider.label}] 模型: {model_name} "
                            f"(attempt {attempt + 1}/{attempts})"
                        )
                        generate_kwargs = {
                            "model": model_name,
                            "contents": prompt,
                        }
                        if resolved_max_output_tokens:
                            generate_kwargs["config"] = {"maxOutputTokens": resolved_max_output_tokens}
                        response = client.models.generate_content(**generate_kwargs)

                        response_text = getattr(response, "text", None)
                        if not response_text:
                            raise ValueError(f"模型 {model_name} 返回空响应")

                        elapsed = time.monotonic() - t0
                        self._record_latency(provider.label, elapsed)
                        logger.info(f"成功 [{provider.label}] 模型: {model_name} ({elapsed:.1f}s)")
                        return response_text, model_name

                    except Exception as e:
                        error_msg = str(e).lower()
                        last_error = e

                        is_transient = (
                            "503" in error_msg
                            or "unavailable" in error_msg
                            or "timeout" in error_msg
                            or "timed out" in error_msg
                            or "deadline_exceeded" in error_msg
                        )
                        is_quota = (
                            "quota" in error_msg
                            or "429" in error_msg
                            or "resource_exhausted" in error_msg
                        )
                        is_not_found = (
                            ("404" in error_msg and "not_found" in error_msg)
                            or "is not found for api version" in error_msg
                        )

                        if is_not_found:
                            self._mark_model_unsupported(model_name)
                            logger.warning(f"模型 {model_name} 不可用(404)，已标记跳过后续请求")
                            break

                        if is_transient and attempt < len(retry_waits):
                            wait = retry_waits[attempt]
                            logger.warning(f"[{provider.label}] 模型 {model_name} 暂时不可用，{wait}s 后重试...")
                            time.sleep(wait)
                            continue

                        if is_quota:
                            self._mark_model_cooldown(model_name)
                            logger.warning(f"[{provider.label}] 模型 {model_name} 配额/限流，换 provider...")
                            break  # 换下一个 provider

                        if is_transient:
                            self._mark_model_cooldown(model_name)

                        logger.warning(f"[{provider.label}] 模型 {model_name} 失败: {str(e)[:120]}")
                        break  # 换下一个 provider
                else:
                    continue
                # 如果 is_not_found 导致 break，跳出 provider 循环也跳过此 model
                if model_name in self._unsupported_models:
                    break

        if not any_tried:
            raise Exception("所有 Gemini 模型当前均被熔断/跳过，请稍后重试或切换 Claude。")

        raise Exception(f"所有模型都失败。最后一个错误: {last_error}")

    def stream_generate(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        max_output_tokens: Optional[int] = None,
    ):
        """
        流式生成内容，按顺序 yield (chunk_text, model_name) 元组。
        支持延迟优选 + 多模型 Fallback。
        """
        if not self.providers:
            raise RuntimeError(
                "google-genai is not installed. Please run: pip install google-genai"
            )

        models_to_try = models or self.models
        resolved_max = self._resolve_max_output_tokens(max_output_tokens)
        last_error = None

        for model_name in models_to_try:
            skip_reason = self._get_model_skip_reason(model_name)
            if skip_reason:
                logger.info(f"跳过模型 {model_name}: {skip_reason}")
                continue

            provider_order = self._sorted_provider_indices(self.providers)
            for pidx in provider_order:
                provider, client = self.providers[pidx]

                try:
                    t0 = time.monotonic()
                    logger.info(f"流式生成 [{provider.label}] 模型: {model_name}")
                    generate_kwargs: dict = {"model": model_name, "contents": prompt}
                    if resolved_max:
                        generate_kwargs["config"] = {"maxOutputTokens": resolved_max}

                    stream = client.models.generate_content_stream(**generate_kwargs)
                    has_content = False

                    for chunk in stream:
                        text = getattr(chunk, "text", None) or ""
                        if text:
                            has_content = True
                            yield text, model_name

                    if not has_content:
                        raise ValueError(f"模型 {model_name} 流式返回空响应")

                    elapsed = time.monotonic() - t0
                    self._record_latency(provider.label, elapsed)
                    logger.info(f"流式生成完成 [{provider.label}]: {model_name} ({elapsed:.1f}s)")
                    return  # 成功

                except Exception as e:
                    error_msg = str(e).lower()
                    last_error = e

                    is_not_found = (
                        ("404" in error_msg and "not_found" in error_msg)
                        or "is not found for api version" in error_msg
                    )
                    is_quota = (
                        "quota" in error_msg
                        or "429" in error_msg
                        or "resource_exhausted" in error_msg
                    )

                    if is_not_found:
                        self._mark_model_unsupported(model_name)
                        logger.warning(f"模型 {model_name} 不可用(404)，已标记跳过")
                        break  # 跳出 provider 循环，换 model
                    elif is_quota:
                        self._mark_model_cooldown(model_name)
                        logger.warning(f"[{provider.label}] 模型 {model_name} 配额/限流，换 provider")
                    else:
                        logger.warning(f"[{provider.label}] 模型 {model_name} 流式失败: {str(e)[:120]}")
                    continue

        raise Exception(f"所有模型流式生成均失败。最后错误: {last_error}")

    @staticmethod
    def _load_positive_int_env(name: str, default: int) -> int:
        raw = os.getenv(name, "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            logger.warning(f"环境变量 {name} 无效（{raw}），回退到默认值 {default}")
            return default

    @staticmethod
    def _load_non_negative_int_env(name: str, default: int) -> int:
        raw = os.getenv(name, "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            logger.warning(f"环境变量 {name} 无效（{raw}），回退到默认值 {default}")
            return default

    @staticmethod
    def _load_bool_env(name: str, default: bool) -> bool:
        raw = os.getenv(name, "").strip().lower()
        if not raw:
            return default
        if raw in {"1", "true", "yes", "on"}:
            return True
        if raw in {"0", "false", "no", "off"}:
            return False
        logger.warning(f"环境变量 {name} 无效（{raw}），回退到默认值 {default}")
        return default

    def _resolve_max_output_tokens(self, explicit_value: Optional[int]) -> Optional[int]:
        if explicit_value is not None:
            return explicit_value if explicit_value > 0 else None
        return self.max_output_tokens_default if self.max_output_tokens_default > 0 else None

    def _mark_model_cooldown(self, model_name: str):
        cooldown_seconds = self.model_cooldown_seconds
        if cooldown_seconds <= 0:
            return
        with self._state_lock:
            self._model_cooldowns[model_name] = time.monotonic() + cooldown_seconds

    @classmethod
    def _mark_model_unsupported(cls, model_name: str):
        with cls._state_lock:
            cls._unsupported_models.add(model_name)

    @classmethod
    def _get_model_skip_reason(cls, model_name: str) -> Optional[str]:
        with cls._state_lock:
            if model_name in cls._unsupported_models:
                return "已标记为不可用(404)"

            cooldown_until = cls._model_cooldowns.get(model_name)
            if cooldown_until is None:
                return None

            remain = cooldown_until - time.monotonic()
            if remain > 0:
                return f"冷却中(约{int(remain)}s)"

            del cls._model_cooldowns[model_name]
            return None

    @staticmethod
    def _resolve_models_from_env() -> List[str]:
        # 显式列表优先：GEMINI_MODELS=a,b,c
        raw_models = os.getenv("GEMINI_MODELS", "").strip()
        if raw_models:
            unique_models: List[str] = []
            for model in [item.strip() for item in raw_models.split(",") if item.strip()]:
                if model not in unique_models:
                    unique_models.append(model)
            if unique_models:
                return unique_models

        # 临时切首选：GEMINI_PREFERRED_MODEL=models/gemini-2.5-pro
        preferred_model = os.getenv("GEMINI_PREFERRED_MODEL", "").strip()
        if preferred_model:
            reordered = [preferred_model]
            reordered.extend(model for model in DEFAULT_MODELS if model != preferred_model)
            return reordered

        return list(DEFAULT_MODELS)

    @classmethod
    def _record_latency(cls, label: str, elapsed: float):
        """记录一次成功请求的延迟，用 EMA 更新"""
        with cls._state_lock:
            prev = cls._provider_latencies.get(label)
            if prev is None:
                cls._provider_latencies[label] = elapsed
            else:
                alpha = cls._LATENCY_EMA_ALPHA
                cls._provider_latencies[label] = alpha * elapsed + (1 - alpha) * prev

    @classmethod
    def _sorted_provider_indices(cls, providers: List[Tuple["GeminiProvider", object]]) -> List[int]:
        """按历史延迟升序排列 provider 索引，无数据的排最前（优先探索）"""
        def sort_key(idx: int) -> float:
            label = providers[idx][0].label
            with cls._state_lock:
                latency = cls._provider_latencies.get(label)
            # 无数据 -> -1，保证优先被尝试
            return latency if latency is not None else -1.0
        return sorted(range(len(providers)), key=sort_key)

    @staticmethod
    def _load_all_providers() -> List[GeminiProvider]:
        """
        从 .env 和 cc-switch 数据库收集所有可用 provider，按 (api_key, base_url) 去重。
        """
        providers: List[GeminiProvider] = []
        seen: set[tuple] = set()

        def _add(p: GeminiProvider):
            if p.dedup_key not in seen:
                seen.add(p.dedup_key)
                providers.append(p)

        # 1) .env / 环境变量直连 Google
        env_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
        if env_key:
            _add(GeminiProvider(api_key=env_key, label="env"))

        # 2) cc-switch 数据库 — 所有 gemini provider
        db_path = Path(
            os.getenv("CC_SWITCH_DB_PATH", str(Path.home() / ".cc-switch" / "cc-switch.db"))
        ).expanduser()
        if db_path.exists():
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT name, settings_config
                        FROM providers
                        WHERE app_type='gemini'
                        ORDER BY is_current DESC, name
                        """
                    )
                    for name, settings_json in cursor.fetchall():
                        try:
                            cfg = json.loads(settings_json) if settings_json else {}
                            env_cfg = cfg.get("env", {})
                            if not isinstance(env_cfg, dict):
                                continue
                            key = ""
                            for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                                v = env_cfg.get(k)
                                if isinstance(v, str) and v.strip():
                                    key = v.strip()
                                    break
                            if not key:
                                continue
                            base_url = None
                            for url_key in ("GOOGLE_GEMINI_BASE_URL",):
                                v = env_cfg.get(url_key)
                                if isinstance(v, str) and v.strip():
                                    base_url = v.strip()
                                    break
                            _add(GeminiProvider(api_key=key, base_url=base_url, label=name))
                        except (json.JSONDecodeError, TypeError):
                            continue
            except Exception:
                pass

        return providers


