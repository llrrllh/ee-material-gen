import unittest

from sync_course_faculty import extract_section, replace_faculty_in_prompt


class SyncCourseFacultyTests(unittest.TestCase):
    def test_extract_section_by_heading(self):
        md = """## 课程简介
内容A

## 核心师资
- 老师1
- 老师2

## 课程安排
内容B
"""
        section = extract_section(md, "核心师资")
        self.assertIn("## 核心师资", section)
        self.assertIn("- 老师1", section)
        self.assertNotIn("## 课程安排", section)

    def test_replace_faculty_section(self):
        prompt = """### 项目定位
xxx

### 核心师资
旧内容

### 招生对象
yyy
"""
        memory_faculty = """## 核心师资
- 新老师A
- 新老师B
"""
        updated = replace_faculty_in_prompt(prompt, memory_faculty)
        self.assertIn("### 核心师资", updated)
        self.assertIn("新老师A", updated)
        self.assertNotIn("旧内容", updated)


if __name__ == "__main__":
    unittest.main()
