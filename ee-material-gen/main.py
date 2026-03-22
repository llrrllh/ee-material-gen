"""
复旦EE招生素材生成器 - FastAPI 主服务
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from gemini_client import GeminiClient
from prompt_builder import PromptBuilder


# 初始化 FastAPI
app = FastAPI(title="复旦EE素材生成器", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
BASE_DIR = Path(__file__).parent
WORKFILES_DIR = Path("/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles")
VISUAL_ASSETS_DIR = WORKFILES_DIR / "08.视觉素材"
HISTORY_DIR = BASE_DIR / "history"

# 确保历史目录存在
HISTORY_DIR.mkdir(exist_ok=True)

gemini_client = GeminiClient()
prompt_builder = PromptBuilder(base_dir=BASE_DIR)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# 挂载视觉资产目录
if VISUAL_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(VISUAL_ASSETS_DIR)), name="assets")


# ==================== 数据模型 ====================

class GenerateRequest(BaseModel):
    """生成素材请求"""
    course_id: str
    material_type: str
    user_requirements: str = ""
    custom_prompt: Optional[str] = None
    # Phase 2: 生成前细分控制
    narrative_style: Optional[str] = None
    layout_structure: Optional[str] = None
    visual_elements: Optional[str] = None
    content_presentation: Optional[str] = None
    # Phase 2: 局部内容开关
    include_faculty: bool = True
    include_schedule: bool = True
    include_tuition: bool = True
    include_student_profile: bool = True
    include_curriculum: bool = True
    include_certification: bool = True
    # Phase 2: 视觉资产
    logo_url: Optional[str] = None
    background_url: Optional[str] = None


class ExportRequest(BaseModel):
    """导出请求"""
    html: str
    format: str  # "pdf" or "png"
    filename: str


class EditRequest(BaseModel):
    """对话式微调请求"""
    current_html: str
    edit_instruction: str
    course_id: str
    material_type: str


# ==================== API 接口 ====================

@app.get("/")
async def root():
    """根路径，返回前端页面"""
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


@app.get("/api/courses")
async def get_courses():
    """获取所有课程列表"""
    try:
        courses = prompt_builder.get_courses()
        return JSONResponse(content=courses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/material-types")
async def get_material_types():
    """获取所有素材类型列表"""
    try:
        material_types = prompt_builder.get_material_types()
        return JSONResponse(content=material_types)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visual-assets")
async def get_visual_assets():
    """获取可用的视觉资产列表"""
    try:
        assets = {
            "logos": []
        }

        if VISUAL_ASSETS_DIR.exists():
            # 扫描 Logo 文件（从 02_EE项目标识与Logo 目录）
            logo_dir = VISUAL_ASSETS_DIR / "02_EE项目标识与Logo"
            if logo_dir.exists():
                for file in logo_dir.glob("*.png"):
                    assets["logos"].append({
                        "name": file.name,
                        "url": f"/assets/02_EE项目标识与Logo/{file.name}"
                    })
                for file in logo_dir.glob("*.jpg"):
                    assets["logos"].append({
                        "name": file.name,
                        "url": f"/assets/02_EE项目标识与Logo/{file.name}"
                    })

        return JSONResponse(content=assets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_material(request: GenerateRequest):
    """生成素材"""
    try:
        # 构建提示词
        prompt = prompt_builder.build_prompt(
            course_id=request.course_id,
            material_type=request.material_type,
            user_requirements=request.user_requirements,
            custom_prompt=request.custom_prompt,
            narrative_style=request.narrative_style,
            layout_structure=request.layout_structure,
            visual_elements=request.visual_elements,
            content_presentation=request.content_presentation,
            include_faculty=request.include_faculty,
            include_schedule=request.include_schedule,
            include_tuition=request.include_tuition,
            include_student_profile=request.include_student_profile,
            include_curriculum=request.include_curriculum,
            include_certification=request.include_certification,
            logo_url=request.logo_url,
            background_url=request.background_url
        )

        print(f"\n{'='*60}")
        print(f"生成素材: {request.course_id} - {request.material_type}")
        print(f"{'='*60}\n")

        # 调用 Gemini 生成
        response_text, model_used = gemini_client.generate(prompt)

        # 提取 HTML 代码
        html = extract_html_from_response(response_text)

        # 保存历史记录
        history_id = save_history(
            course_id=request.course_id,
            material_type=request.material_type,
            html=html,
            prompt=prompt,
            model_used=model_used,
            user_requirements=request.user_requirements,
            request_params=request.dict()
        )

        return JSONResponse(content={
            "html": html,
            "prompt_used": prompt,
            "model_used": model_used,
            "history_id": history_id
        })

    except Exception as e:
        print(f"生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/edit")
async def edit_material(request: EditRequest):
    """对话式微调素材"""
    try:
        # 构建增量修改的提示词
        edit_prompt = f"""你是一个HTML/CSS专家。用户有一个已经生成的营销素材HTML代码，现在需要根据用户的修改指令进行增量修改。

**重要要求**：
1. 不要推翻重来，只需要根据用户的修改指令对现有HTML进行局部调整
2. 保持原有的整体结构和风格
3. 只修改用户明确要求修改的部分
4. 确保修改后的HTML代码完整且可以直接渲染

**当前HTML代码**：
```html
{request.current_html}
```

**用户的修改指令**：
{request.edit_instruction}

**课程信息**：
- 课程ID: {request.course_id}
- 素材类型: {request.material_type}

请根据用户的修改指令，对上述HTML代码进行增量修改，并返回完整的修改后的HTML代码。
只返回HTML代码，不要有任何其他说明文字。代码必须用```html和```包裹。
"""

        print(f"\n{'='*60}")
        print(f"对话式微调: {request.course_id} - {request.material_type}")
        print(f"修改指令: {request.edit_instruction}")
        print(f"{'='*60}\n")

        # 调用 Gemini 生成
        response_text, model_used = gemini_client.generate(edit_prompt)

        # 提取 HTML 代码
        html = extract_html_from_response(response_text)

        return JSONResponse(content={
            "html": html,
            "prompt_used": edit_prompt,
            "model_used": model_used
        })

    except Exception as e:
        print(f"微调失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history():
    """获取历史记录列表"""
    try:
        history_list = get_history_list()
        return JSONResponse(content=history_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{history_id}")
async def get_history_by_id(history_id: str):
    """获取历史记录详情"""
    try:
        history_detail = get_history_detail(history_id)
        if not history_detail:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        return JSONResponse(content=history_detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export")
async def export_material(request: ExportRequest):
    """导出素材为 PDF 或图片"""
    try:
        # 创建导出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = BASE_DIR / "exports" / f"{timestamp}_{request.filename}"
        export_dir.mkdir(parents=True, exist_ok=True)

        # 保存 HTML
        html_path = export_dir / "output.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(request.html)

        # 根据格式导出
        if request.format == "pdf":
            output_path = export_dir / "output.pdf"
            # 使用 wkhtmltopdf 导出 PDF
            import subprocess
            subprocess.run([
                "wkhtmltopdf",
                "--enable-local-file-access",
                str(html_path),
                str(output_path)
            ], check=True)

        elif request.format == "png":
            output_path = export_dir / "output.png"
            # 使用 playwright 导出长图
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 750, 'height': 1000})
                page.goto(f'file://{html_path}')
                page.wait_for_load_state('networkidle')

                # 获取页面完整高度
                page_height = page.evaluate('document.documentElement.scrollHeight')
                page.set_viewport_size({'width': 750, 'height': page_height})

                # 截图
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()

        else:
            raise ValueError(f"不支持的导出格式: {request.format}")

        return JSONResponse(content={
            "file_path": str(output_path),
            "message": f"导出成功: {output_path.name}"
        })

    except Exception as e:
        print(f"导出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 辅助函数 ====================

def save_history(course_id: str, material_type: str, html: str, prompt: str,
                 model_used: str, user_requirements: str, request_params: dict) -> str:
    """保存生成历史记录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_id = f"{timestamp}_{course_id}_{material_type}"

    history_data = {
        "id": history_id,
        "timestamp": timestamp,
        "course_id": course_id,
        "material_type": material_type,
        "html": html,
        "prompt": prompt,
        "model_used": model_used,
        "user_requirements": user_requirements,
        "request_params": request_params
    }

    history_file = HISTORY_DIR / f"{history_id}.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    return history_id


def get_history_list():
    """获取历史记录列表"""
    history_files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)
    history_list = []

    for file in history_files[:50]:  # 最多返回50条
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history_list.append({
                    "id": data.get("id"),
                    "timestamp": data.get("timestamp"),
                    "course_id": data.get("course_id"),
                    "material_type": data.get("material_type"),
                    "model_used": data.get("model_used"),
                    "user_requirements": data.get("user_requirements", "")[:100]  # 截取前100字符
                })
        except Exception as e:
            print(f"读取历史记录失败: {file.name}, {str(e)}")
            continue

    return history_list


def get_history_detail(history_id: str):
    """获取历史记录详情"""
    history_file = HISTORY_DIR / f"{history_id}.json"

    if not history_file.exists():
        return None

    with open(history_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_html_from_response(response_text: str) -> str:
    """从 Gemini 响应中提取 HTML 代码"""
    # 尝试提取 ```html ... ``` 代码块
    pattern = r"```html\s*(.*?)\s*```"
    match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    # 如果没有代码块，尝试查找 <!DOCTYPE html> 或 <html>
    if "<!DOCTYPE html>" in response_text or "<html" in response_text:
        # 提取从 <!DOCTYPE 或 <html> 到 </html> 的内容
        start_idx = response_text.find("<!DOCTYPE html>")
        if start_idx == -1:
            start_idx = response_text.find("<html")
        end_idx = response_text.rfind("</html>")

        if start_idx != -1 and end_idx != -1:
            return response_text[start_idx:end_idx + 7].strip()

    # 如果都没找到，返回原始响应
    return response_text.strip()


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
