import os
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from gemini_client import GeminiClient, GeminiProvider


class GeminiClientEnvTests(unittest.TestCase):
    def setUp(self):
        self.old_gemini = os.environ.get("GEMINI_API_KEY")
        self.old_google = os.environ.get("GOOGLE_API_KEY")
        self.old_cc_switch_db = os.environ.get("CC_SWITCH_DB_PATH")
        self.old_preferred_model = os.environ.get("GEMINI_PREFERRED_MODEL")
        self.old_models = os.environ.get("GEMINI_MODELS")
        self.old_request_timeout = os.environ.get("GEMINI_REQUEST_TIMEOUT_SECONDS")
        self.old_total_timeout = os.environ.get("GEMINI_TOTAL_TIMEOUT_SECONDS")
        self.old_fast_mode = os.environ.get("GEMINI_FAST_MODE")
        self.old_model_cooldown = os.environ.get("GEMINI_MODEL_COOLDOWN_SECONDS")
        self.old_max_output_tokens = os.environ.get("GEMINI_MAX_OUTPUT_TOKENS")

    def tearDown(self):
        if self.old_gemini is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = self.old_gemini

        if self.old_google is None:
            os.environ.pop("GOOGLE_API_KEY", None)
        else:
            os.environ["GOOGLE_API_KEY"] = self.old_google
        if self.old_cc_switch_db is None:
            os.environ.pop("CC_SWITCH_DB_PATH", None)
        else:
            os.environ["CC_SWITCH_DB_PATH"] = self.old_cc_switch_db
        if self.old_preferred_model is None:
            os.environ.pop("GEMINI_PREFERRED_MODEL", None)
        else:
            os.environ["GEMINI_PREFERRED_MODEL"] = self.old_preferred_model
        if self.old_models is None:
            os.environ.pop("GEMINI_MODELS", None)
        else:
            os.environ["GEMINI_MODELS"] = self.old_models
        if self.old_request_timeout is None:
            os.environ.pop("GEMINI_REQUEST_TIMEOUT_SECONDS", None)
        else:
            os.environ["GEMINI_REQUEST_TIMEOUT_SECONDS"] = self.old_request_timeout
        if self.old_total_timeout is None:
            os.environ.pop("GEMINI_TOTAL_TIMEOUT_SECONDS", None)
        else:
            os.environ["GEMINI_TOTAL_TIMEOUT_SECONDS"] = self.old_total_timeout
        if self.old_fast_mode is None:
            os.environ.pop("GEMINI_FAST_MODE", None)
        else:
            os.environ["GEMINI_FAST_MODE"] = self.old_fast_mode
        if self.old_model_cooldown is None:
            os.environ.pop("GEMINI_MODEL_COOLDOWN_SECONDS", None)
        else:
            os.environ["GEMINI_MODEL_COOLDOWN_SECONDS"] = self.old_model_cooldown
        if self.old_max_output_tokens is None:
            os.environ.pop("GEMINI_MAX_OUTPUT_TOKENS", None)
        else:
            os.environ["GEMINI_MAX_OUTPUT_TOKENS"] = self.old_max_output_tokens

    def test_use_google_api_key_as_fallback(self):
        os.environ["GEMINI_API_KEY"] = ""
        os.environ["GOOGLE_API_KEY"] = "google-key-from-switch"

        client = GeminiClient(models=["models/gemini-2.5-pro"])
        self.assertEqual(client.api_key, "google-key-from-switch")

    def test_use_cc_switch_db_key_as_fallback(self):
        os.environ["GEMINI_API_KEY"] = ""
        os.environ["GOOGLE_API_KEY"] = ""

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "cc-switch.db"
            self._build_cc_switch_test_db(db_path)
            os.environ["CC_SWITCH_DB_PATH"] = str(db_path)

            client = GeminiClient(models=["models/gemini-2.5-pro"])
            self.assertEqual(client.api_key, "cc-switch-gemini-key")

    def test_preferred_model_reorders_defaults(self):
        os.environ["GEMINI_PREFERRED_MODEL"] = "models/gemini-2.5-pro"
        os.environ.pop("GEMINI_MODELS", None)

        client = GeminiClient(api_key="test-key")
        self.assertEqual(client.models[0], "models/gemini-2.5-pro")
        self.assertIn("models/gemini-3.1-pro-preview", client.models)

    def test_gemini_models_env_override(self):
        os.environ["GEMINI_MODELS"] = "models/gemini-2.5-pro, models/gemini-3.1-pro-preview, models/gemini-2.5-pro"

        client = GeminiClient(api_key="test-key")
        self.assertEqual(
            client.models,
            ["models/gemini-2.5-pro", "models/gemini-3.1-pro-preview"],
        )

    def test_invalid_timeout_env_falls_back_to_default(self):
        os.environ["GEMINI_REQUEST_TIMEOUT_SECONDS"] = "abc"
        os.environ["GEMINI_TOTAL_TIMEOUT_SECONDS"] = "-1"

        client = GeminiClient(api_key="test-key", models=["models/gemini-2.5-pro"])
        self.assertEqual(client.request_timeout_seconds, 30)
        self.assertEqual(client.total_timeout_seconds, 120)

    def test_fast_mode_and_max_output_tokens_env(self):
        os.environ["GEMINI_FAST_MODE"] = "true"
        os.environ["GEMINI_MODEL_COOLDOWN_SECONDS"] = "180"
        os.environ["GEMINI_MAX_OUTPUT_TOKENS"] = "8192"

        client = GeminiClient(api_key="test-key", models=["models/gemini-2.5-pro"])
        self.assertTrue(client.fast_mode)
        self.assertEqual(client.model_cooldown_seconds, 180)
        self.assertEqual(client.max_output_tokens_default, 8192)

    @staticmethod
    def _build_cc_switch_test_db(db_path: Path) -> None:
        settings_config = json.dumps(
            {
                "env": {
                    "GEMINI_API_KEY": "cc-switch-gemini-key",
                    "GEMINI_MODEL": "gemini-2.5-pro",
                }
            }
        )

        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE providers (
                    id TEXT NOT NULL,
                    app_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    settings_config TEXT NOT NULL,
                    is_current BOOLEAN NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                INSERT INTO providers (id, app_type, name, settings_config, is_current)
                VALUES ('test-provider', 'gemini', 'Test Gemini', ?, 1)
                """,
                (settings_config,),
            )
            conn.commit()


if __name__ == "__main__":
    unittest.main()


class GeminiProviderLoadTests(unittest.TestCase):
    """多 Provider 加载和轮转相关测试"""

    def setUp(self):
        self.env_vars = [
            "GEMINI_API_KEY", "GOOGLE_API_KEY", "CC_SWITCH_DB_PATH",
        ]
        self.old_env = {k: os.environ.get(k) for k in self.env_vars}
        # 重置类级别状态
        GeminiClient._provider_index = 0

    def tearDown(self):
        for k, v in self.old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_load_env_provider(self):
        """只有 .env key 时创建单个 provider"""
        os.environ["GEMINI_API_KEY"] = "env-key-123"
        os.environ["CC_SWITCH_DB_PATH"] = "/nonexistent/path.db"

        client = GeminiClient(models=["models/gemini-2.5-pro"])
        self.assertEqual(client.api_key, "env-key-123")
        self.assertEqual(len(client.providers), 1)
        self.assertEqual(client.providers[0][0].label, "env")
        self.assertIsNone(client.providers[0][0].base_url)

    def test_load_multiple_providers_from_cc_switch(self):
        """从 cc-switch 加载多个 provider"""
        os.environ["GEMINI_API_KEY"] = ""
        os.environ["GOOGLE_API_KEY"] = ""

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "cc-switch.db"
            self._build_multi_provider_db(db_path)
            os.environ["CC_SWITCH_DB_PATH"] = str(db_path)

            client = GeminiClient(models=["models/gemini-2.5-pro"])
            # 应该有 2 个 provider（2 个不同的 key+base_url）
            self.assertEqual(len(client.providers), 2)
            labels = {p.label for p, _ in client.providers}
            self.assertIn("Provider-A", labels)
            self.assertIn("Provider-B", labels)

    def test_dedup_same_key_and_base_url(self):
        """相同 (api_key, base_url) 的 provider 应去重"""
        os.environ["GEMINI_API_KEY"] = ""
        os.environ["GOOGLE_API_KEY"] = ""

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "cc-switch.db"
            self._build_dedup_db(db_path)
            os.environ["CC_SWITCH_DB_PATH"] = str(db_path)

            client = GeminiClient(models=["models/gemini-2.5-pro"])
            # 两条记录 key+base_url 相同，应只保留 1 个
            self.assertEqual(len(client.providers), 1)

    def test_env_plus_cc_switch_combined(self):
        """.env key + cc-switch key 一起加载"""
        os.environ["GEMINI_API_KEY"] = "direct-google-key"

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "cc-switch.db"
            self._build_multi_provider_db(db_path)
            os.environ["CC_SWITCH_DB_PATH"] = str(db_path)

            client = GeminiClient(models=["models/gemini-2.5-pro"])
            # 1 env + 2 cc-switch = 3
            self.assertEqual(len(client.providers), 3)
            self.assertEqual(client.providers[0][0].label, "env")

    def test_explicit_api_key_ignores_others(self):
        """显式传入 api_key 时只用该单 key"""
        os.environ["GEMINI_API_KEY"] = "env-key"

        client = GeminiClient(api_key="explicit-key", models=["models/gemini-2.5-pro"])
        self.assertEqual(len(client.providers), 1)
        self.assertEqual(client.api_key, "explicit-key")

    def test_latency_tracking_and_sorting(self):
        """延迟追踪：记录后按 EMA 排序，快的排前面"""
        GeminiClient._provider_latencies.clear()

        # 模拟 3 个 provider
        p_a = GeminiProvider(api_key="ka", label="A")
        p_b = GeminiProvider(api_key="kb", label="B")
        p_c = GeminiProvider(api_key="kc", label="C")
        fake_providers = [(p_a, None), (p_b, None), (p_c, None)]

        # 无数据时，所有 provider 都排前面（优先探索）
        order = GeminiClient._sorted_provider_indices(fake_providers)
        self.assertEqual(order, [0, 1, 2])

        # 记录延迟：B=1s, A=5s, C 无数据
        GeminiClient._record_latency("A", 5.0)
        GeminiClient._record_latency("B", 1.0)

        order = GeminiClient._sorted_provider_indices(fake_providers)
        # C 无数据排最前（-1），B(1s) 次之，A(5s) 最后
        self.assertEqual(order, [2, 1, 0])

    def test_latency_ema_updates(self):
        """EMA 平滑更新"""
        GeminiClient._provider_latencies.clear()

        # 第一次记录
        GeminiClient._record_latency("X", 10.0)
        self.assertAlmostEqual(GeminiClient._provider_latencies["X"], 10.0)

        # 第二次记录 alpha=0.3: 0.3*2 + 0.7*10 = 7.6
        GeminiClient._record_latency("X", 2.0)
        self.assertAlmostEqual(GeminiClient._provider_latencies["X"], 7.6)

    def test_provider_dedup_key(self):
        """GeminiProvider.dedup_key 正确工作"""
        p1 = GeminiProvider(api_key="k1", base_url="https://a.com", label="A")
        p2 = GeminiProvider(api_key="k1", base_url="https://a.com", label="B")
        p3 = GeminiProvider(api_key="k1", base_url=None, label="C")
        self.assertEqual(p1.dedup_key, p2.dedup_key)
        self.assertNotEqual(p1.dedup_key, p3.dedup_key)

    @staticmethod
    def _build_multi_provider_db(db_path: Path):
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE providers (
                    id TEXT NOT NULL,
                    app_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    settings_config TEXT NOT NULL,
                    is_current BOOLEAN NOT NULL DEFAULT 0
                )
            """)
            for pid, name, key, base_url, current in [
                ("p1", "Provider-A", "key-aaa", "https://proxy-a.com", 1),
                ("p2", "Provider-B", "key-bbb", "https://proxy-b.com", 0),
            ]:
                cfg = json.dumps({"env": {
                    "GEMINI_API_KEY": key,
                    "GOOGLE_GEMINI_BASE_URL": base_url,
                }})
                conn.execute(
                    "INSERT INTO providers VALUES (?, 'gemini', ?, ?, ?)",
                    (pid, name, cfg, current),
                )
            conn.commit()

    @staticmethod
    def _build_dedup_db(db_path: Path):
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE providers (
                    id TEXT NOT NULL,
                    app_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    settings_config TEXT NOT NULL,
                    is_current BOOLEAN NOT NULL DEFAULT 0
                )
            """)
            cfg = json.dumps({"env": {
                "GEMINI_API_KEY": "same-key",
                "GOOGLE_GEMINI_BASE_URL": "https://same-proxy.com",
            }})
            for pid, name in [("p1", "Dup-A"), ("p2", "Dup-B")]:
                conn.execute(
                    "INSERT INTO providers VALUES (?, 'gemini', ?, ?, 0)",
                    (pid, name, cfg),
                )
            conn.commit()
