import unittest
from pathlib import Path

from prompt_builder import PromptBuilder


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PromptBuilderTests(unittest.TestCase):
    def setUp(self):
        self.builder = PromptBuilder(base_dir=PROJECT_ROOT)

    def test_get_material_types_contains_export_width(self):
        material_types = self.builder.get_material_types()

        self.assertGreater(len(material_types), 0)
        self.assertTrue(all("export_width" in item for item in material_types))

    def test_custom_prompt_short_circuit(self):
        custom = "this is custom prompt"
        result = self.builder.build_prompt(
            course_id="EE-QYJ",
            material_type="recruit-poster",
            custom_prompt=custom,
        )
        self.assertEqual(result, custom)

    def test_invalid_course_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.builder.build_prompt(
                course_id="INVALID",
                material_type="recruit-poster",
            )


if __name__ == "__main__":
    unittest.main()
