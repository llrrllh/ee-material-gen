import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault("GEMINI_API_KEY", "test-key")

import main  # noqa: E402


class MainApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_material_types_api_contains_export_width(self):
        response = self.client.get("/api/material-types")
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertGreater(len(payload), 0)
        self.assertTrue(all("export_width" in item for item in payload))

    def test_generate_returns_400_for_invalid_course(self):
        response = self.client.post(
            "/api/generate",
            json={
                "course_id": "INVALID",
                "material_type": "recruit-poster",
                "user_requirements": "",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("未找到课程", response.json()["detail"])

    def test_extract_html_from_response(self):
        response_text = "xxx```html\n<html><body>ok</body></html>\n```yyy"
        html = main.extract_html_from_response(response_text)
        self.assertEqual(html, "<html><body>ok</body></html>")

    def test_generate_fallback_to_claude_when_gemini_fails(self):
        original_gemini_generate = main.gemini_client.generate
        original_claude_available = main.claude_client.is_available
        original_claude_optimize = main.claude_client.optimize

        try:
            def fake_gemini_generate(_prompt, **_kwargs):
                raise Exception("gemini unavailable")

            def fake_claude_is_available():
                return True

            def fake_claude_optimize(_prompt):
                return "```html\n<html><body>from-claude</body></html>\n```", "claude-sonnet-4-6"

            main.gemini_client.generate = fake_gemini_generate
            main.claude_client.is_available = fake_claude_is_available
            main.claude_client.optimize = fake_claude_optimize

            response = self.client.post(
                "/api/generate",
                json={
                    "course_id": "EE-QYJ",
                    "material_type": "recruit-poster",
                    "user_requirements": "",
                },
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["model_used"], "claude-sonnet-4-6")
            self.assertIn("from-claude", payload["html"])
        finally:
            main.gemini_client.generate = original_gemini_generate
            main.claude_client.is_available = original_claude_available
            main.claude_client.optimize = original_claude_optimize

    def test_generate_does_not_auto_save_history(self):
        original_gemini_generate = main.gemini_client.generate
        original_save_history = main.save_history

        try:
            def fake_gemini_generate(_prompt, **_kwargs):
                return "```html\n<html><body>no-auto-save</body></html>\n```", "models/gemini-3.1-pro-preview"

            def fail_if_called(*_args, **_kwargs):
                raise AssertionError("save_history should not be called in /api/generate")

            main.gemini_client.generate = fake_gemini_generate
            main.save_history = fail_if_called

            response = self.client.post(
                "/api/generate",
                json={
                    "course_id": "EE-QYJ",
                    "material_type": "recruit-poster",
                    "user_requirements": "",
                },
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertIn("no-auto-save", payload["html"])
            self.assertIsNone(payload.get("history_id"))
        finally:
            main.gemini_client.generate = original_gemini_generate
            main.save_history = original_save_history

    def test_manual_save_history_api(self):
        original_save_history = main.save_history
        captured = {}

        try:
            def fake_save_history(**kwargs):
                captured.update(kwargs)
                return "manual_test_history_id"

            main.save_history = fake_save_history
            response = self.client.post(
                "/api/history",
                json={
                    "course_id": "EE-QYJ",
                    "material_type": "recruit-poster",
                    "html": "<html><body>manual-save</body></html>",
                    "prompt": "test prompt",
                    "model_used": "manual-model",
                    "user_requirements": "manual req",
                    "request_params": {"source": "test"},
                },
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertTrue(payload.get("success"))
            self.assertEqual(payload.get("history_id"), "manual_test_history_id")
            self.assertEqual(captured.get("course_id"), "EE-QYJ")
            self.assertEqual(captured.get("material_type"), "recruit-poster")
        finally:
            main.save_history = original_save_history

    def test_export_html(self):
        response = self.client.post(
            "/api/export",
            json={
                "html": "<html><body>hello</body></html>",
                "format": "html",
                "filename": "test_export",
                "export_width": 750,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("hello", response.text)


if __name__ == "__main__":
    unittest.main()
