import os
import unittest
from pathlib import Path

from settings import get_settings


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.keys = ("CORS_ALLOW_ORIGINS", "VISUAL_ASSETS_DIR")
        self.original = {key: os.environ.get(key) for key in self.keys}

    def tearDown(self):
        for key, value in self.original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        get_settings.cache_clear()

    def test_parse_comma_separated_cors_origins(self):
        os.environ["CORS_ALLOW_ORIGINS"] = "https://a.example, https://b.example"
        get_settings.cache_clear()

        settings = get_settings()
        self.assertEqual(settings.cors_origins, ["https://a.example", "https://b.example"])

    def test_visual_assets_dir_can_be_overridden(self):
        os.environ["VISUAL_ASSETS_DIR"] = "/tmp/ee-assets"
        get_settings.cache_clear()

        settings = get_settings()
        self.assertEqual(settings.visual_assets_dir, Path("/tmp/ee-assets"))


if __name__ == "__main__":
    unittest.main()
