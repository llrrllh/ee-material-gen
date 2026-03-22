"""
提示词构建器
根据 course_id + material_type + user_requirements 构建完整的 Gemini 提示词
"""

import json
from pathlib import Path
from typing import Dict, Optional


class PromptBuilder:
    """提示词构建器"""

    def __init__(self, base_dir: str = "."):
        """
        初始化提示词构建器

        Args:
            base_dir: 项目根目录
        """
        self.base_dir = Path(base_dir)
        self.courses_file = self.base_dir / "courses.json"
        self.combined_template_file = self.base_dir / "prompts" / "combined_template.txt"

        # 加载课程配置
        self._load_courses()

        # 加载组合模板
        with open(self.combined_template_file, "r", encoding="utf-8") as f:
            self.combined_template = f.read()

    def _load_courses(self):
        """加载课程配置（支持热重载）"""
        with open(self.courses_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.courses = {c["course_id"]: c for c in config["courses"]}
            self.material_types = {m["type_id"]: m for m in config["material_types"]}

    def reload_courses(self):
        """重新加载课程配置（热重载）"""
        self._load_courses()

    def get_courses(self):
        """获取所有课程列表（每次调用时重新加载以支持热重载）"""
        self._load_courses()
        return list(self.courses.values())

    def get_material_types(self):
        """获取所有素材类型列表"""
        return list(self.material_types.values())

    def build_prompt(
        self,
        course_id: str,
        material_type: str,
        user_requirements: str = "",
        custom_prompt: Optional[str] = None,
        narrative_style: Optional[str] = None,
        layout_structure: Optional[str] = None,
        visual_elements: Optional[str] = None,
        content_presentation: Optional[str] = None,
        include_faculty: bool = True,
        include_schedule: bool = True,
        include_tuition: bool = True,
        include_student_profile: bool = True,
        include_curriculum: bool = True,
        include_certification: bool = True,
        logo_url: Optional[str] = None,
        background_url: Optional[str] = None
    ) -> str:
        """
        构建完整的 Gemini 提示词

        Args:
            course_id: 课程ID（如 EE-QYJ）
            material_type: 素材类型（如 recruit-poster）
            user_requirements: 用户自定义要求
            custom_prompt: 如果提供，直接使用此提示词（用于重新生成）
            narrative_style: 叙事风格（权威严谨/痛点触发/圈层吸引/设问式沟通）
            layout_structure: 排版结构（模块化布局/卡片式设计/全屏沉浸式/信息流叙事）
            visual_elements: 视觉元素（数字焦点化/高对比度色系/极简留白/微动效点缀）
            content_presentation: 内容呈现（引言高亮/清单体呈现/数据快照）
            include_faculty: 是否包含师资介绍
            include_schedule: 是否包含课程表/学制信息
            include_tuition: 是否包含学费信息
            include_student_profile: 是否包含学员画像数据
            include_curriculum: 是否包含课程大纲
            include_certification: 是否包含认证/背书信息

        Returns:
            完整的提示词字符串
        """
        # 如果提供了自定义提示词，直接返回
        if custom_prompt:
            return custom_prompt

        # 验证课程和素材类型
        if course_id not in self.courses:
            raise ValueError(f"未找到课程: {course_id}")
        if material_type not in self.material_types:
            raise ValueError(f"未找到素材类型: {material_type}")

        course = self.courses[course_id]
        material = self.material_types[material_type]

        # 读取课程提示词
        course_prompt_file = self.base_dir / course["prompt_file"]
        with open(course_prompt_file, "r", encoding="utf-8") as f:
            course_prompt = f.read()

        # 读取素材类型提示词
        type_prompt_file = self.base_dir / material["prompt_file"]
        with open(type_prompt_file, "r", encoding="utf-8") as f:
            type_prompt = f.read()

        # 构建细分控制提示词
        style_controls = []

        if narrative_style:
            style_controls.append(f"**叙事风格**：{narrative_style}")

        if layout_structure:
            style_controls.append(f"**排版结构**：{layout_structure}")

        if visual_elements:
            style_controls.append(f"**视觉元素**：{visual_elements}")

        if content_presentation:
            style_controls.append(f"**内容呈现**：{content_presentation}")

        # 构建内容模块开关提示词
        content_modules = []
        excluded_modules = []

        if not include_faculty:
            excluded_modules.append("师资介绍")
        if not include_schedule:
            excluded_modules.append("课程表/学制信息")
        if not include_tuition:
            excluded_modules.append("学费信息")
        if not include_student_profile:
            excluded_modules.append("学员画像数据")
        if not include_curriculum:
            excluded_modules.append("课程大纲")
        if not include_certification:
            excluded_modules.append("认证/背书信息")

        if excluded_modules:
            content_modules.append(f"**排除以下内容模块**：{', '.join(excluded_modules)}")

        # 构建视觉资产提示词
        visual_assets = []
        if logo_url:
            visual_assets.append(f"**Logo URL**：{logo_url}（可在 HTML 中使用此 URL 引用 Logo）")
        if background_url:
            visual_assets.append(f"**背景图 URL**：{background_url}（可在 HTML 中使用此 URL 作为背景图）")

        # 组合用户要求和细分控制
        combined_requirements = user_requirements or ""

        if style_controls:
            if combined_requirements:
                combined_requirements += "\n\n## 风格控制\n"
            else:
                combined_requirements = "## 风格控制\n"
            combined_requirements += "\n".join(style_controls)

        if content_modules:
            if combined_requirements:
                combined_requirements += "\n\n## 内容控制\n"
            else:
                combined_requirements = "## 内容控制\n"
            combined_requirements += "\n".join(content_modules)

        if visual_assets:
            if combined_requirements:
                combined_requirements += "\n\n## 视觉资产\n"
            else:
                combined_requirements = "## 视觉资产\n"
            combined_requirements += "\n".join(visual_assets)
            combined_requirements += "\n\n**重要提示**：请在生成的 HTML 中使用上述提供的 Logo 和背景图 URL，而不是使用 CSS 渐变或 SVG 替代。"

        if not combined_requirements:
            combined_requirements = "无特殊要求"

        # 构建完整提示词
        prompt = self.combined_template.replace("{COURSE_PROMPT}", course_prompt)
        prompt = prompt.replace("{TYPE_PROMPT}", type_prompt)
        prompt = prompt.replace("{USER_REQUIREMENTS}", combined_requirements)

        return prompt

    def get_courses(self) -> list:
        """获取所有课程列表"""
        return [
            {
                "course_id": c["course_id"],
                "name": c["name"],
                "short_name": c["short_name"]
            }
            for c in self.courses.values()
        ]

    def get_material_types(self) -> list:
        """获取所有素材类型列表"""
        return [
            {
                "type_id": m["type_id"],
                "name": m["name"],
                "description": m["description"]
            }
            for m in self.material_types.values()
        ]

    def get_course_info(self, course_id: str) -> Dict:
        """获取课程详细信息"""
        if course_id not in self.courses:
            raise ValueError(f"未找到课程: {course_id}")
        return self.courses[course_id]
